// Example: In any context (ToolContext shown)
import com.google.adk.tools.ToolContext;

public void logToolUsage(ToolContext toolContext) {
    String agentName = toolContext.agentName();
    String invId = toolContext.invocationId();
    String functionCallId = toolContext.functionCallId().orElse("N/A"); // Specific to ToolContext
    System.out.println("Log: Invocation= " + invId + " Agent= " + agentName + " FunctionCallID= " + functionCallId);
}