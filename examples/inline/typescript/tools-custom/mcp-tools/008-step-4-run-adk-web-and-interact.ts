import 'dotenv/config';
import {LlmAgent, MCPToolset} from "@google/adk";

// Retrieve the API key from an environment variable.
// Ensure this environment variable is set in the terminal where you run 'adk web'.
// Example: export GOOGLE_MAPS_API_KEY="YOUR_ACTUAL_KEY"
const googleMapsApiKey = process.env.GOOGLE_MAPS_API_KEY;
if (!googleMapsApiKey) {
    console.warn("WARNING: GOOGLE_MAPS_API_KEY is not set.");
    // We throw an error here to prevent the agent from booting without its crucial grounding key
    throw new Error('GOOGLE_MAPS_API_KEY is not provided, please run "export GOOGLE_MAPS_API_KEY=YOUR_ACTUAL_KEY" to add that.');
}

export const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "travel_planner_agent",
    description: "A helpful assistant for planning travel.",
    tools: [
        new MCPToolset({
            // Using SseConnectionParams to connect to the remote Grounding Lite service,
            // mirroring Python's StreamableHTTPConnectionParams.
            type: "SseConnectionParams",
            url: "https://mapstools.googleapis.com/mcp",
            headers: {
                "X-Goog-Api-Key": googleMapsApiKey,
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        })
    ],
});