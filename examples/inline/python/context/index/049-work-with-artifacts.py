# Example: In a tool function
from google.adk.tools import ToolContext

def check_available_docs(tool_context: ToolContext) -> dict:
    try:
        artifact_keys = tool_context.list_artifacts()
        print(f"Available artifacts: {artifact_keys}")
        return {"available_docs": artifact_keys}
    except ValueError as e:
        return {"error": f"Artifact service error: {e}"}