import { LlmAgent, MCPToolset } from "@google/adk";

const NOTION_TOKEN = "YOUR_NOTION_TOKEN";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "notion_agent",
    instruction: "Help users get information from Notion",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "@notionhq/notion-mcp-server"],
                env: {
                    NOTION_TOKEN: NOTION_TOKEN,
                },
            },
        }),
    ],
});

export { rootAgent };