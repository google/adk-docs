import { LlmAgent, MCPToolset } from "@google/adk";

const GRAFANA_URL = "https://<your-stack>.grafana.net";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "observability_agent",
    instruction: "Help users investigate issues using Grafana Cloud observability data",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.grafana.com/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        "X-Grafana-URL": GRAFANA_URL,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };