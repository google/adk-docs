import { LlmAgent, MCPToolset } from "@google/adk";

const MAILGUN_API_KEY = "YOUR_MAILGUN_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "mailgun_agent",
    instruction: "Help users send emails and manage their Mailgun account",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "@mailgun/mcp-server"],
                env: {
                    MAILGUN_API_KEY: MAILGUN_API_KEY,
                    // MAILGUN_API_REGION: "eu",  // Optional: defaults to "us"
                },
            },
        }),
    ],
});

export { rootAgent };