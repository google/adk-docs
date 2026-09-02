# Example: In a callback or initial tool
from google.adk.agents.context import Context # Or ToolContext
from google.genai import types

def save_document_reference(context: Context, file_path: str) -> None:
    # Assume file_path is something like "gs://my-bucket/docs/report.pdf" or "/local/path/to/report.pdf"
    try:
        # Create a Part containing the path/URI text
        artifact_part = types.Part.from_text(file_path)
        version = context.save_artifact("document_to_summarize.txt", artifact_part)
        print(f"Saved document reference '{file_path}' as artifact version {version}")
        # Store the filename in state if needed by other tools
        context.state["temp:doc_artifact_name"] = "document_to_summarize.txt"
    except ValueError as e:
        print(f"Error saving artifact: {e}") # E.g., Artifact service not configured
    except Exception as e:
        print(f"Unexpected error saving artifact reference: {e}")

# Example usage:
# save_document_reference(context, "gs://my-bucket/docs/report.pdf")