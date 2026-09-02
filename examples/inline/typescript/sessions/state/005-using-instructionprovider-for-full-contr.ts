import { LlmAgent, ReadonlyContext } from "@google/adk";

// This is an InstructionProvider
function myInstructionProvider(context: ReadonlyContext): string {
    // No state injection occurs — curly braces are treated as literal text.
    return 'Format your output as JSON: {"city": "<name>", "population": <number>}';
}

const agent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "template_helper_agent",
    instruction: myInstructionProvider
});