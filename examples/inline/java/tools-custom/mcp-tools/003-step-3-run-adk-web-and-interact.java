package agents;

import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.SessionKey;
import com.google.adk.tools.mcp.McpToolset;
import com.google.adk.tools.mcp.StdioServerParameters;
import com.google.genai.types.Content;
import com.google.genai.types.Part;

import java.util.List;

public class McpAgentCreator {

    /**
     * Initializes an McpToolset, retrieves tools from an MCP server using stdio,
     * creates an LlmAgent with these tools, sends a prompt to the agent,
     * and ensures the toolset is closed.
     * @param args Command line arguments (not used).
     */
    public static void main(String[] args) {
        //Note: you may have permissions issues if the folder is outside home
        String yourFolderPath = "~/path/to/folder";

        StdioServerParameters serverParams = StdioServerParameters.builder()
                .command("npx")
                .args(List.of(
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        yourFolderPath
                ))
                .build();

        try (McpToolset toolset = new McpToolset(serverParams.toServerParameters())) {
            LlmAgent agent = LlmAgent.builder()
                    .model("gemini-flash-latest")
                    .name("enterprise_assistant")
                    .description("An agent to help users access their file systems")
                    .instruction(
                            "Help user accessing their file systems. You can list files in a directory."
                    )
                    .tools(toolset)
                    .build();

            System.out.println("Agent created: " + agent.name());

            InMemoryRunner runner = new InMemoryRunner(agent);
            String userId = "user123";
            String sessionId = "1234";
            String promptText = "Which files are in this directory - " + yourFolderPath + "?";

            // Explicitly create the session first
            SessionKey sessionKey = runner.sessionService().createSession(runner.appName(), userId, null, sessionId).blockingGet().sessionKey();
            System.out.println("Session created: " + sessionId + " for user: " + userId);

            Content promptContent = Content.fromParts(Part.fromText(promptText));

            System.out.println("\nSending prompt: \"" + promptText + "\" to agent...\n");

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