import google.genai.types as types
from google.adk.agents.callback_context import CallbackContext # Or ToolContext

async def save_generated_report_py(context: CallbackContext, report_bytes: bytes):
    """Saves generated PDF report bytes as an artifact."""
    report_artifact = types.Part.from_bytes(
        data=report_bytes,
        mime_type="application/pdf"
    )
    filename = "generated_report.pdf"

    try:
        version = await context.save_artifact(filename=filename, artifact=report_artifact)
        print(f"Successfully saved Python artifact '{filename}' as version {version}.")
        # The event generated after this callback will contain:
        # event.actions.artifact_delta == {"generated_report.pdf": version}
    except ValueError as e:
        print(f"Error saving Python artifact: {e}. Is ArtifactService configured in Runner?")
    except Exception as e:
        # Handle potential storage errors (e.g., GCS permissions)
        print(f"An unexpected error occurred during Python artifact save: {e}")

# --- Example Usage Concept (Python) ---
# async def main_py():
#   callback_context: CallbackContext = ... # obtain context
#   report_data = b'...' # Assume this holds the PDF bytes
#   await save_generated_report_py(callback_context, report_data)