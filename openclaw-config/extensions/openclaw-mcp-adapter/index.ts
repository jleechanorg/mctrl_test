import { parseConfig } from "./config.js";
import { McpClientPool } from "./mcp-client.js";
import { execFileSync } from "node:child_process";
import { homedir } from "node:os";
import { join } from "node:path";

function sanitizeToolName(name: string): string {
  return name.replace(/[^a-zA-Z0-9_-]/g, "_");
}

function resolveSecondOpinionToken(): string | undefined {
  const envToken =
    process.env.SECOND_OPINION_ID_TOKEN ??
    process.env.AI_UNIVERSE_ID_TOKEN ??
    process.env.FIREBASE_ID_TOKEN;
  if (envToken) {
    return envToken;
  }

  // Fallback to local auth helper when running in a profile process
  // where the ID token is not exported into the environment.
  try {
    const script = join(homedir(), ".claude", "scripts", "auth-aiuniverse.mjs");
    const token = execFileSync("node", [script, "token"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    return token || undefined;
  } catch {
    return undefined;
  }
}

function normalizeToolArgs(toolName: string, params: unknown): Record<string, unknown> {
  const args =
    params && typeof params === "object" && !Array.isArray(params)
      ? { ...(params as Record<string, unknown>) }
      : {};

  const shouldInjectAuth = toolName.startsWith("agent.") || toolName.startsWith("rate_limit.") || toolName.startsWith("conversation.");
  if (shouldInjectAuth && args.idToken === undefined) {
    const authToken = resolveSecondOpinionToken();
    if (authToken) {
      args.idToken = authToken;
    }
  }

  if (toolName === "agent.second_opinion") {
    if (args.maxOpinions === undefined && args.secondaryModels === undefined) {
      // Keep default calls low-latency to avoid MCP server timeout.
      args.maxOpinions = 0;
    }
    if (args.primaryModel === undefined) {
      args.primaryModel = "cerebras";
    }
  }

  return args;
}

export default function (api: any) {
  const pool = new McpClientPool();

  // Use service lifecycle - connections only happen when gateway starts
  api.registerService({
    id: "mcp-adapter",

    async start() {
      // Re-read config on each start so hot-reload picks up new servers
      const config = parseConfig(api.pluginConfig);
      if (config.servers.length === 0) {
        console.log("[mcp-adapter] No servers configured");
        return;
      }
      for (const server of config.servers) {
        try {
          console.log(`[mcp-adapter] Connecting to ${server.name}...`);
          await pool.connect(server);

          const tools = await pool.listTools(server.name);
          console.log(`[mcp-adapter] ${server.name}: found ${tools.length} tools`);

          const registeredNames = new Set<string>();
          for (const tool of tools) {
            const rawToolName = config.toolPrefix ? `${server.name}_${tool.name}` : tool.name;
            const toolName = sanitizeToolName(rawToolName);

            if (registeredNames.has(toolName)) {
              console.warn(`[mcp-adapter] Skipping duplicate sanitized tool name: ${toolName} (from ${rawToolName})`);
              continue;
            }
            registeredNames.add(toolName);

            api.registerTool({
              name: toolName,
              description: tool.description ?? `Tool from ${server.name}`,
              parameters: tool.inputSchema ?? { type: "object", properties: {} },
              async execute(_id: string, params: unknown) {
                const result = await pool.callTool(server.name, tool.name, normalizeToolArgs(tool.name, params));
                const text = result.content
                  ?.map((c: any) => {
                    if (typeof c.text === "string") return c.text;
                    if (c.data !== undefined) return typeof c.data === "string" ? c.data : JSON.stringify(c.data);
                    return "";
                  })
                  .join("\n") ?? "";
                return {
                  content: [{ type: "text", text }],
                  isError: result.isError,
                };
              },
            });

            if (toolName !== rawToolName) {
              console.log(`[mcp-adapter] Registered: ${toolName} (from ${rawToolName})`);
            } else {
              console.log(`[mcp-adapter] Registered: ${toolName}`);
            }
          }
        } catch (err) {
          console.error(`[mcp-adapter] Failed to connect to ${server.name}:`, err);
        }
      }
    },

    async stop() {
      console.log("[mcp-adapter] Shutting down...");
      await pool.closeAll();
      console.log("[mcp-adapter] All connections closed");
    },
  });
}
