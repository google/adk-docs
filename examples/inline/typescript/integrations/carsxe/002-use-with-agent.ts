import { LlmAgent, MCPToolset } from "@google/adk";

const CARSXE_API_KEY = "YOUR_CARSXE_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "carsxe_agent",
    instruction:
        "You are a vehicle data assistant. Use the CarsXE tools to decode " +
        "VINs and license plates and to look up specifications, market value, " +
        "history, recalls, and OBD-II codes.",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.carsxe.com/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        "X-API-Key": CARSXE_API_KEY,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };