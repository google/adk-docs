import com.google.genai.types.FunctionResponse;
import com.google.common.collect.ImmutableList;
import java.util.Map;

ImmutableList<FunctionResponse> responses = event.functionResponses(); // from Event.java
if (!responses.isEmpty()) {
    for (FunctionResponse response : responses) {
        String toolName = response.name().get();
        Map<String, String> result= response.response().get(); // Check before getting the response
        System.out.println("  Tool Result: " + toolName + " -> " + result);
    }
}