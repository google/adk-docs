import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.LongRunningFunctionTool;
import java.util.HashMap;
import java.util.Map;

public class ExampleLongRunningFunction {

  // Define your Long Running function.
  // Ask for approval for the reimbursement.
  public static Map<String, Object> askForApproval(String purpose, double amount) {
    // Simulate creating a ticket and sending a notification
    System.out.println(
        "Simulating ticket creation for purpose: " + purpose + ", amount: " + amount);

    // Send a notification to the approver with the link of the ticket
    Map<String, Object> result = new HashMap<>();
    result.put("status", "pending");
    result.put("approver", "Sean Zhou");
    result.put("purpose", purpose);
    result.put("amount", amount);
    result.put("ticket-id", "approval-ticket-1");
    return result;
  }

  public static void main(String[] args) throws NoSuchMethodException {
    // Pass the method to LongRunningFunctionTool.create
    LongRunningFunctionTool approveTool =
        LongRunningFunctionTool.create(ExampleLongRunningFunction.class, "askForApproval");

    // Include the tool in the agent
    LlmAgent approverAgent =
        LlmAgent.builder()
            // ...
            .tools(approveTool)
            .build();
  }
}