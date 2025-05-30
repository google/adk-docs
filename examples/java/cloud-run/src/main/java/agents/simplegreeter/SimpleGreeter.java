package agents.simplegreeter;

import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;

/** A simple greeter agent that greets the user in a friendly way. */
public class SimpleGreeter {

  // The Agent should be exposed as a "public static" argument.
  public static BaseAgent ROOT_AGENT =
      LlmAgent.builder()
          .name("GreeterBot")
          .description("A friendly agent that greets the user.")
          .model("gemini-2.0-flash")
          .instruction(
              "Greet the user in a very friendly and welcoming way based on their message. If they"
                  + " just say hi, say hi back warmly.")
          .build();
  public static String getPurpose() {
    return "To offer a warm greeting.";
  }
}