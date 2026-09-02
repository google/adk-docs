import com.google.genai.types.FunctionCall;
import com.google.common.collect.ImmutableList;
import java.util.Map;

ImmutableList<FunctionCall> calls = event.functionCalls(); // from Event.java
if (!calls.isEmpty()) {
  for (FunctionCall call : calls) {
    String toolName = call.name().get();
    // args is Optional<Map<String, Object>>
    Map<String, Object> arguments = call.args().get();
           System.out.println("  Tool: " + toolName + ", Args: " + arguments);
    // Application might dispatch execution based on this
  }
}