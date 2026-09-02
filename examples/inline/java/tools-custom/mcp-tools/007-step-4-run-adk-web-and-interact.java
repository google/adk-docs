package agents;

import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.SessionKey;
import com.google.adk.tools.mcp.McpToolset;
import com.google.adk.tools.mcp.StdioServerParameters;
import com.google.genai.types.Content;
import com.google.genai.types.Part;

import java.util.HashMap;
import java.util.Map;

public class MapsAgentCreator {

    /**
     * Initializes an McpToolset for Google Maps Grounding Lite,
     * creates an LlmAgent, sends a map-related prompt, and closes the toolset.
     */
    public static void main(String[] args) {
        // Read from environment variables
        String googleMapsApiKey = System.getenv("GOOGLE_MAPS_API_KEY");

        if (googleMapsApiKey == null || googleMapsApiKey.trim().isEmpty()) {
            // Fallback or direct assignment for testing - NOT RECOMMENDED FOR PRODUCTION
            googleMapsApiKey = "YOUR_GOOGLE_MAPS_API_KEY_HERE"; // Replace if not using env var
            if ("YOUR_GOOGLE_MAPS_API_KEY_HERE".equals(googleMapsApiKey)) {
                System.out.println("WARNING: GOOGLE_MAPS_API_KEY is not set. Please set it as an environment variable or in the script.");
            }
        }

        // Setup the headers for the remote MCP connection
        Map<String, String> headers = new HashMap<>();
        headers.put("X-Goog-Api-Key", googleMapsApiKey);
        headers.put("Content-Type", "application/json");
        headers.put("Accept", "application/json, text/event-stream");

        // Use StreamableHttpServerParameters for the remote HTTP MCP server connection
        StreamableHttpServerParameters serverParams = StreamableHttpServerParameters.builder("https://mapstools.googleapis.com/mcp")
                .headers(headers)
                .build();

        try (McpToolset toolset = new McpToolset(serverParams)) {
            // Build the Agent with the configured Toolset
            LlmAgent agent = LlmAgent.builder()
                    .model("gemini-flash-latest")
                    .name("travel_planner_agent")
                    .description("A helpful assistant for planning travel routes.")
                    .tools(toolset)
                    .build();

            System.out.println("Agent created: " + agent.name());

            // Set up the runner and session
            InMemoryRunner runner = new InMemoryRunner(agent);
            String userId = "maps-user-" + System.currentTimeMillis();
            String sessionId = "maps-session-" + System.currentTimeMillis();

            String promptText = "Please give me directions to the nearest pharmacy to Madison Square Garden.";

            // Explicitly create the session first
            SessionKey sessionKey = runner.sessionService().createSession(runner.appName(), userId, null, sessionId).blockingGet().sessionKey();
            System.out.println("Session created: " + sessionId + " for user: " + userId);

            Content promptContent = Content.fromParts(Part.fromText(promptText));

            System.out.println("\nSending prompt: \"" + promptText + "\" to agent...\n");

            // Execute the prompt asynchronously and print the streamed events
            runner.runAsync(sessionKey, promptContent)
                    .blockingForEach(event -> {
                        System.out.println("Event received: " + event.toJson());
                    });
        } catch (Exception e) {
            System.err.println("An error occurred: " + e.getMessage());
            e.printStackTrace();
        }
    }
}