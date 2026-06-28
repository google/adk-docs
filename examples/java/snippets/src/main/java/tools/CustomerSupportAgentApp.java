package tools;

// --8<-- [start:full_code]

import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

public class CustomerSupportAgentApp {

  private static final String APP_NAME = "customer_support_agent";
  private static final String USER_ID = "user1234";
  private static final String SESSION_ID = "1234";
  private static final String MODEL_ID = "gemini-2.0-flash";

  /**
   * Checks if the query requires escalation and transfers to another agent if needed.
   *
   * @param query The user's query.
   * @param toolContext The context for the tool.
   * @return A map indicating the result of the check and transfer.
   */
  public static Map<String, Object> checkAndTransfer(
      @Schema(name = "query", description = "the user query")
      String query,
      @Schema(name = "toolContext", description = "the tool context")
      ToolContext toolContext) {
    Map<String, Object> response = new HashMap<>();
    if (query.toLowerCase(Locale.ROOT).contains("urgent")) {
      System.out.println("Tool: Detected urgency, transferring to the support agent.");
      toolContext.actions().setTransferToAgent("support_agent");
      response.put("status", "transferring");
      response.put("message", "Transferring to the support agent...");
    } else {
      response.put("status", "processed");
      response.put(
          "message", String.format("Processed query: '%s'. No further action needed.", query));
    }
    return response;
  }

  /**
   * Calls the agent with the given query and prints the final response.
   *
   * @param runner The runner to use.
   * @param query The query to send to the agent.
   */
  public static void callAgent(Runner runner, String query) {
    Content content =
        Content.fromParts(Part.fromText(query));

    InMemorySessionService sessionService = (InMemorySessionService) runner.sessionService();
    // Fixed: session ID does not need to be an optional.
    Session session =
        sessionService
            .createSession(APP_NAME, USER_ID, /* state= */ null, SESSION_ID)
            .blockingGet();

    runner
        .runAsync(session.userId(), session.id(), content)
        .forEach(
            event -> {
              if (event.finalResponse()
                  && event.content().isPresent()
                  && event.content().get().parts().isPresent()
                  && !event.content().get().parts().get().isEmpty()
                  && event.content().get().parts().get().get(0).text().isPresent()) {
                String finalResponse = event.content().get().parts().get().get(0).text().get();
                System.out.println("Agent Response: " + finalResponse);
              }
            });
  }

  public static void main(String[] args) throws NoSuchMethodException {
    FunctionTool escalationTool =
        FunctionTool.create(
            CustomerSupportAgentApp.class.getMethod(
                "checkAndTransfer", String.class, ToolContext.class));

    LlmAgent supportAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("support_agent")
            .description("""
                The dedicated support agent.
                Mentions it is a support handler and helps the user with their urgent issue.
            """)
            .instruction("""
                You are the dedicated support agent.
                Mentioned you are a support handler and please help the user with their urgent issue.
            """)
            .build();

    LlmAgent mainAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("main_agent")
            .description("""
                The first point of contact for customer support of an analytics tool.
                Answers general queries.
                If the user indicates urgency, uses the 'check_and_transfer' tool.
                """)
            .instruction("""
                You are the first point of contact for customer support of an analytics tool.
                Answer general queries.
                If the user indicates urgency, use the 'check_and_transfer' tool.
                """)
            .tools(ImmutableList.of(escalationTool))
            .subAgents(supportAgent)
            .build();
    // Fixed: LlmAgent.subAgents() expects 0 arguments.
    // Sub-agents are now added to the main agent via its builder,
    // as `subAgents` is a property that should be set during agent construction
    // if it's not dynamically managed.

    InMemorySessionService sessionService = new InMemorySessionService();
    Runner runner = new Runner(mainAgent, APP_NAME, null, sessionService);

    // Agent Interaction
    callAgent(runner, "this is urgent, i cant login");
  }
}
// --8<-- [end:full_code]
