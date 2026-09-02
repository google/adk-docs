# Example: In any context (ToolContext shown)
from google.adk.tools import ToolContext

def log_tool_usage(tool_context: ToolContext, **kwargs):
    agent_name = tool_context.agent_name
    inv_id = tool_context.invocation_id
    func_call_id = getattr(tool_context, 'function_call_id', 'N/A') # Specific to ToolContext

    print(f"Log: Invocation={inv_id}, Agent={agent_name}, FunctionCallID={func_call_id} - Tool Executed.")