import { LlmAgent, MCPToolset } from "@google/adk";

const GITHUB_TOKEN = "YOUR_GITHUB_TOKEN";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "github_agent",
    instruction: "Help users get information from GitHub",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://api.githubcopilot.com/mcp/",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${GITHUB_TOKEN}`,
                        "X-MCP-Toolsets": "all",
                        "X-MCP-Readonly": "true",
                    },
                },
            },
        }),
    ],
});

export { rootAgent };