export interface ServerConfig {
  name: string;
  transport: "stdio" | "http";
  command?: string;
  args?: string[];
  env?: Record<string, string>;
  url?: string;
  headers?: Record<string, string>;
}

export interface McpAdapterConfig {
  servers: ServerConfig[];
  toolPrefix: boolean;
}

function interpolateEnv(obj: Record<string, string>): Record<string, string> {
  const result: Record<string, string> = {};
  for (const [k, v] of Object.entries(obj)) {
    result[k] = v.replace(/\$\{([^}]+)\}/g, (_, name) => process.env[name] ?? "");
  }
  return result;
}

export function parseConfig(raw: unknown): McpAdapterConfig {
  const cfg = (raw ?? {}) as Record<string, unknown>;
  const servers: ServerConfig[] = [];

  for (const s of (cfg.servers as unknown[]) ?? []) {
    const srv = s as Record<string, unknown>;
    if (!srv.name) throw new Error("Server missing 'name'");

    const transport = (srv.transport as string) ?? "stdio";
    if (transport !== "stdio" && transport !== "http") {
      throw new Error(`Server "${srv.name}" has invalid transport "${transport}"; expected "stdio" or "http"`);
    }
    if (transport === "stdio" && !srv.command) throw new Error(`Server "${srv.name}" missing 'command'`);
    if (transport === "http" && !srv.url) throw new Error(`Server "${srv.name}" missing 'url'`);

    const rawUrl = srv.url as string | undefined;
    const rawCommand = srv.command as string | undefined;
    servers.push({
      name: srv.name as string,
      transport: transport as "stdio" | "http",
      command: rawCommand ? interpolateEnv({ command: rawCommand }).command : undefined,
      args: srv.args ? (srv.args as string[]).map(a => interpolateEnv({ v: a }).v) : undefined,
      env: srv.env ? interpolateEnv(srv.env as Record<string, string>) : undefined,
      url: rawUrl ? interpolateEnv({ url: rawUrl }).url : undefined,
      headers: srv.headers ? interpolateEnv(srv.headers as Record<string, string>) : undefined,
    });
  }

  return {
    servers,
    toolPrefix: cfg.toolPrefix !== false,
  };
}
