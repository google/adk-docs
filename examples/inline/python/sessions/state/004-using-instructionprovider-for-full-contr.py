from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext

# This is an InstructionProvider
def my_instruction_provider(context: ReadonlyContext) -> str:
    # No state injection occurs — curly braces are treated as literal text.
    return 'Format your output as JSON: {"city": "<name>", "population": <number>}'

agent = LlmAgent(
    model="gemini-flash-latest",
    name="template_helper_agent",
    instruction=my_instruction_provider
)