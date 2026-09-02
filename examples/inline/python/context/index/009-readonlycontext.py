# Example: Instruction provider receiving ReadonlyContext
from google.adk.agents.readonly_context import ReadonlyContext

def my_instruction_provider(context: ReadonlyContext) -> str:
    # Read-only access example
    # The state property provides a read-only MappingProxyType view of the state
    user_tier = context.state.get("user_tier", "standard")
    # context.state['new_key'] = 'value' # TypeError: 'mappingproxy' object does not support item assignment
    return f"Process the request for a {user_tier} user."