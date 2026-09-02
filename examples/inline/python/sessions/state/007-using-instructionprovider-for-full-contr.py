from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.utils import instructions_utils

async def my_dynamic_instruction_provider(context: ReadonlyContext) -> str:
    template = "This is a {adjective} instruction. Use JSON like: {\"key\": \"value\"}."
    # This will inject the 'adjective' state variable.
    # The JSON braces are left alone because their content is not a valid identifier.
    return await instructions_utils.inject_session_state(template, context)

agent = LlmAgent(
    model="gemini-flash-latest",
    name="dynamic_template_helper_agent",
    instruction=my_dynamic_instruction_provider
)