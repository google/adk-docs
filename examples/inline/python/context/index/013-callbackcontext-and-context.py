# Example: Callback receiving Context (CallbackContext is unified into Context)
from google.adk.agents.context import Context
from google.adk.models import LlmRequest
from google.genai import types
from typing import Optional

def my_before_model_cb(context: Context, request: LlmRequest) -> Optional[types.Content]:
    # Read/Write state example
    call_count = context.state.get("model_calls", 0)
    context.state["model_calls"] = call_count + 1 # Modify state (tracks delta)

    # Optionally load an artifact
    # config_part = context.load_artifact("model_config.json")
    print(f"Preparing model call #{call_count + 1} for invocation {context.invocation_id}")
    return None # Allow model call to proceed