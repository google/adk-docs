import { LlmAgent, MCPToolset } from "@google/adk";

const N8N_INSTANCE_URL = "https://localhost:5678";
const N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "n8n_agent",
    instruction: "Help users manage and execute workflows in n8n",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: `${N8N_INSTANCE_URL}/mcp-server/http`,
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${N8N_MCP_TOKEN}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };