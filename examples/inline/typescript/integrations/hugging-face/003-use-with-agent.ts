import { LlmAgent, MCPToolset } from "@google/adk";

const HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "hugging_face_agent",
    instruction: "Help users get information from Hugging Face",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "@llmindset/hf-mcp-server"],
                env: {
                    HF_TOKEN: HUGGING_FACE_TOKEN,
                },
            },
        }),
    ],
});

export { rootAgent };