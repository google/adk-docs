import google.genai.types as types
from google.adk.agents.callback_context import CallbackContext # Or ToolContext

async def process_latest_report_py(context: CallbackContext):
    """Loads the latest report artifact and processes its data."""
    filename = "generated_report.pdf"
    try:
        # Load the latest version
        report_artifact = await context.load_artifact(filename=filename)

        if report_artifact and report_artifact.inline_data:
            print(f"Successfully loaded latest Python artifact '{filename}'.")
            print(f"MIME Type: {report_artifact.inline_data.mime_type}")
            # Process the report_artifact.inline_data.data (bytes)
            pdf_bytes = report_artifact.inline_data.data
            print(f"Report size: {len(pdf_bytes)} bytes.")
            # ... further processing ...
        else:
            print(f"Python artifact '{filename}' not found.")

        # Example: Load a specific version (if version 0 exists)
        # specific_version_artifact = await context.load_artifact(filename=filename, version=0)
        # if specific_version_artifact:
        #     print(f"Loaded version 0 of '{filename}'.")

    except ValueError as e:
        print(f"Error loading Python artifact: {e}. Is ArtifactService configured?")
    except Exception as e:
        # Handle potential storage errors
        print(f"An unexpected error occurred during Python artifact load: {e}")

# --- Example Usage Concept (Python) ---
# async def main_py():
#   callback_context: CallbackContext = ... # obtain context
#   await process_latest_report_py(callback_context)