package tools;

// --8<-- [start:init]

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.ReadonlyContext;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.BaseTool;
import com.google.adk.tools.BaseToolset;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;
import io.reactivex.rxjava3.core.Flowable;
import java.util.HashMap;
import java.util.Map;

public class SimpleMathToolsetApp {

  // 1. Define the individual tool functions

  /**
   * Adds two integer numbers.
   *
   * @param a The first number.
   * @param b The second number.
   * @param toolContext The tool context.
   * @return A map with the sum.
   */
  public static Map<String, Object> addNumbers(
      @Schema(name = "a", description = "The first number") int a,
      @Schema(name = "b", description = "The second number") int b,
      ToolContext toolContext) {
    System.out.println("Tool: add_numbers called with a=" + a + ", b=" + b);
    int result = a + b;
    // Example: Storing something in tool_context state
    toolContext.state().put("last_math_operation", "addition");
    Map<String, Object> response = new HashMap<>();
    response.put("status", "success");
    response.put("result", result);
    return response;
  }

  /**
   * Subtracts the second number from the first.
   *
   * @param a The first number.
   * @param b The second number.
   * @return A map with the difference.
   */
  public static Map<String, Object> subtractNumbers(
      @Schema(name = "a", description = "The first number") int a,
      @Schema(name = "b", description = "The second number") int b) {
    System.out.println("Tool: subtract_numbers called with a=" + a + ", b=" + b);
    Map<String, Object> response = new HashMap<>();
    response.put("status", "success");
    response.put("result", a - b);
    return response;
  }

  // 2. Create the Toolset by implementing BaseToolset
  public static class SimpleMathToolset implements BaseToolset {
    private final BaseTool addTool;
    private final BaseTool subtractTool;

    public SimpleMathToolset() throws NoSuchMethodException {
      // Create FunctionTool instances once
      this.addTool =
          FunctionTool.create(
              SimpleMathToolsetApp.class.getMethod(
                  "addNumbers", int.class, int.class, ToolContext.class));
      this.subtractTool =
          FunctionTool.create(
              SimpleMathToolsetApp.class.getMethod("subtractNumbers", int.class, int.class));
      System.out.println("SimpleMathToolset initialized");
    }

    @Override
    public Flowable<BaseTool> getTools(ReadonlyContext readonlyContext) {
      System.out.println("SimpleMathToolset.getTools() called.");
      // Example of dynamic behavior:
      // Could use readonlyContext to access state and conditionally return tools.
      // For this simple example, always return both tools:
      return Flowable.just(addTool, subtractTool);
    }

    @Override
    public void close() throws Exception {
      // No resources to clean up in this simple example
      System.out.println("SimpleMathToolset.close() called.");
    }
  }

  // 3. Define an individual tool (not part of the toolset)

  /**
   * Greets the user.
   *
   * @param name The name of the user.
   * @return A map with the greeting.
   */
  public static Map<String, Object> greetUser(
      @Schema(name = "name", description = "The name of the user") String name) {
    System.out.println("Tool: greetUser called with name=" + name);
    Map<String, Object> response = new HashMap<>();
    response.put("greeting", "Hello, " + name + "!");
    return response;
  }

  public static void main(String[] args) throws Exception {
    BaseTool greetTool =
        FunctionTool.create(SimpleMathToolsetApp.class.getMethod("greetUser", String.class));

    // 4. Instantiate the toolset
    BaseToolset mathToolsetInstance = new SimpleMathToolset();

    // 5. Define an agent that uses both the individual tool and the toolset
    LlmAgent calculatorAgent =
        LlmAgent.builder()
            .name("CalculatorAgent")
            .model("gemini-2.5-flash") // Replace with your desired model
            .instruction(
                "You are a helpful calculator and greeter. "
                    + "Use 'greetUser' for greetings. "
                    + "Use 'addNumbers' to add and 'subtractNumbers' to subtract. "
                    + "Announce the state of 'last_math_operation' if it's set.")
            .tools(greetTool, mathToolsetInstance) // Individual tool and Toolset instance
            .build();

    // System.out.println("Agent '" + calculatorAgent.name() + "' created.");

    // Runner runner = new Runner(calculatorAgent, ...);
    // ... setup and usage ...

    // Important: Clean up the toolset if it manages resources
    mathToolsetInstance.close();
  }
}
// --8<-- [end:init]
