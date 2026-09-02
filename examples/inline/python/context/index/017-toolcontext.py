# Example: Tool function receiving ToolContext
from google.adk.tools import ToolContext
from typing import Dict, Any

# Assume this function is wrapped by a FunctionTool
def search_external_api(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    api_key = tool_context.state.get("api_key")
    if not api_key:
        # Define required auth config
        # auth_config = AuthConfig(...)
        # tool_context.request_credential(auth_config) # Request credentials
        # Use the 'actions' property to signal the auth request has been made
        # tool_context.actions.requested_auth_configs[tool_context.function_call_id] = auth_config
        return {"status": "Auth Required"}

    # Use the API key...
    print(f"Tool executing for query '{query}' using API key. Invocation: {tool_context.invocation_id}")

    # Optionally search memory or list artifacts
    # relevant_docs = tool_context.search_memory(f"info related to {query}")
    # available_files = tool_context.list_artifacts()

    return {"result": f"Data for {query} fetched."}