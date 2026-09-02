import com.google.adk.agents.Instruction;
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.ReadonlyContext;
import io.reactivex.rxjava3.core.Single;

// This is an Instruction.Provider
Instruction.Provider myInstructionProvider = new Instruction.Provider(
    (ReadonlyContext context) -> {
        // No state injection occurs — curly braces are treated as literal text.
        return Single.just("Format your output as JSON: {\"city\": \"<name>\", \"population\": <number>}");
    }
);

LlmAgent agent = LlmAgent.builder()
    .model("gemini-flash-latest")
    .name("template_helper_agent")
    .instruction(myInstructionProvider)
    .build();