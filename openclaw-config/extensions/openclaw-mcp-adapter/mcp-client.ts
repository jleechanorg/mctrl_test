import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import type { ServerConfig } from "./config.js";

interface ClientEntry {
  config: ServerConfig;
  client: Client;
  transport: StdioClientTransport | StreamableHTTPClientTransport;
  connected: boolean;
}

export class McpClientPool {
  private clients = new Map<string, ClientEntry>();
  private reconnectingPromises = new Map<string, Promise<void>>();
  private closedServers = new Set<string>();

  async connect(config: ServerConfig): Promise<Client> {
    if (this.clients.has(config.name)) {
      throw new Error(`Server "${config.name}" is already registered; close it before reconnecting`);
    }
    this.closedServers.delete(config.name);

    const client = new Client({ name: "openclaw-mcp-adapter", version: "0.1.1" });
    const transport = this.createTransport(config);

    await client.connect(transport);

    // Re-check after async gap: close() may have been called during await client.connect()
    if (this.closedServers.has(config.name)) {
      try { await transport.close?.(); } catch {}
      throw new Error(`Server "${config.name}" was closed during connect`);
    }

    // Watch for stdio process exit
    if (transport instanceof StdioClientTransport) {
      transport.onerror = () => this.markDisconnected(config.name);
      transport.onclose = () => this.markDisconnected(config.name);
    }

    this.clients.set(config.name, { config, client, transport, connected: true });
    return client;
  }

  private createTransport(config: ServerConfig) {
    if (config.transport === "http") {
      return new StreamableHTTPClientTransport(new URL(config.url!), {
        requestInit: { headers: config.headers },
      });
    }
    return new StdioClientTransport({
      command: config.command!,
      args: config.args,
      env: { ...process.env, ...config.env },
    });
  }

  async listTools(serverName: string) {
    const entry = this.clients.get(serverName);
    if (!entry) throw new Error(`Unknown server: ${serverName}`);
    const result = await entry.client.listTools();
    return result.tools;
  }

  async callTool(serverName: string, toolName: string, args: unknown) {
    const entry = this.clients.get(serverName);
    if (!entry) throw new Error(`Unknown server: ${serverName}`);

    try {
      return await entry.client.callTool({ name: toolName, arguments: args as Record<string, unknown> });
    } catch (err) {
      if (!entry.connected || this.isConnectionError(err)) {
        await this.reconnect(serverName);
        const newEntry = this.clients.get(serverName);
        if (!newEntry) throw new Error(`Reconnect for "${serverName}" failed`);
        return await newEntry.client.callTool({ name: toolName, arguments: args as Record<string, unknown> });
      }
      throw err;
    }
  }

  private async reconnect(serverName: string) {
    // Deduplicate concurrent reconnect attempts for the same server
    const existing = this.reconnectingPromises.get(serverName);
    if (existing) return existing;

    const promise = this._doReconnect(serverName).finally(() => {
      this.reconnectingPromises.delete(serverName);
    });
    this.reconnectingPromises.set(serverName, promise);
    return promise;
  }

  private async _doReconnect(serverName: string) {
    const entry = this.clients.get(serverName);
    if (!entry) return;

    try { await entry.transport.close?.(); } catch {}
    this.clients.delete(serverName);
    // Abort if close() was called while reconnect was in flight
    if (this.closedServers.has(serverName)) return;
    await this.connect(entry.config).catch(err => {
      if (!this.closedServers.has(serverName)) this.clients.set(serverName, { ...entry, connected: false });
      throw err;
    });
  }

  private markDisconnected(serverName: string) {
    const entry = this.clients.get(serverName);
    if (entry) entry.connected = false;
  }

  private isConnectionError(err: unknown): boolean {
    const msg = String(err);
    return msg.includes("closed") || msg.includes("ECONNREFUSED") || msg.includes("EPIPE");
  }

  getStatus(serverName: string) {
    const entry = this.clients.get(serverName);
    return { connected: entry?.connected ?? false };
  }

  async close(serverName: string) {
    // Mark closed before deleting to prevent reconnect resurrection
    this.closedServers.add(serverName);
    this.reconnectingPromises.delete(serverName);
    const entry = this.clients.get(serverName);
    if (!entry) return;
    this.clients.delete(serverName);
    try {
      await entry.transport.close?.();
    } catch {
      // Ignore close errors
    }
  }

  async closeAll() {
    for (const name of this.clients.keys()) {
      await this.close(name);
    }
  }
}
