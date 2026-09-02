import com.google.adk.agents.Instruction;
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.ReadonlyContext;
import com.google.adk.utils.InstructionUtils;
import io.reactivex.rxjava3.core.Single;

Instruction.Provider myDynamicInstructionProvider = new Instruction.Provider(
    (ReadonlyContext context) -> {
        String template = "This is a " + adjective + " instruction. Use JSON like: {\"key\": \"value\"}.";
        // This will inject the 'adjective' state variable.
        // The JSON braces are left alone because their content is not a valid identifier.
        return InstructionUtils.injectSessionState(context.invocationContext(), template);
    }
);

LlmAgent agent = LlmAgent.builder()
    .model("gemini-flash-latest")
    .name("dynamic_template_helper_agent")
    .instruction(myDynamicInstructionProvider)
    .build();