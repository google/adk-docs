import { LlmAgent, MCPToolset } from "@google/adk";

// Replace with your instance URL if self-hosted (e.g., "gitlab.example.com")
const GITLAB_INSTANCE_URL = "gitlab.com";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "gitlab_agent",
    instruction: "Help users get information from GitLab",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mcp-remote",
                    `https://${GITLAB_INSTANCE_URL}/api/v4/mcp`,
                    "--static-oauth-client-metadata",
                    '{"scope": "mcp"}',
                ],
            },
        }),
    ],
});

export { rootAgent };