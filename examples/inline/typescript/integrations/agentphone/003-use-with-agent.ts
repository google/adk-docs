import { LlmAgent, MCPToolset } from "@google/adk";

const AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "agentphone_agent",
    instruction: "Help users make phone calls, send SMS, and manage phone numbers",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "agentphone-mcp"],
                env: {
                    AGENTPHONE_API_KEY: AGENTPHONE_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };