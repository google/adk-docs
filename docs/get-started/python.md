import os
from google.adk.agents.llm_agent import Agent
from pypdf import PdfReader


def read_pdf(file_path: str) -> dict:
    """Extracts and returns the text content of a PDF file.

    Args:
        file_path: Absolute or relative path to the PDF file on disk.

    Returns:
        A dict with status ("success"/"error"), the extracted text
        (truncated to keep responses manageable), and page count.
    """
    if not os.path.exists(file_path):
        return {"status": "error", "error": f"File not found: {file_path}"}

    try:
        reader = PdfReader(file_path)
        pages_text = []
        for i, page in enumerate(reader.pages):
            pages_text.append(f"--- Page {i + 1} ---\n{page.extract_text() or ''}")
        full_text = "\n".join(pages_text)

        # Keep the tool result to a reasonable size for the model context.
        max_chars = 20000
        truncated = len(full_text) > max_chars
        if truncated:
            full_text = full_text[:max_chars]

        return {
            "status": "success",
            "file_path": file_path,
            "num_pages": len(reader.pages),
            "text": full_text,
            "truncated": truncated,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def list_pdfs(directory: str = ".") -> dict:
    """Lists all PDF files found in a given directory.

    Args:
        directory: Directory to search (defaults to current directory).

    Returns:
        A dict with status and a list of PDF file paths found.
    """
    if not os.path.isdir(directory):
        return {"status": "error", "error": f"Directory not found: {directory}"}

    pdfs = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(".pdf")
    ]
    return {"status": "success", "directory": directory, "pdfs": pdfs}


root_agent = Agent(
    model="gemini-flash-latest",
    name="pdf_agent",
    description="Reads PDF documents and answers questions, summarizes, or extracts information from them.",
    instruction=(
        "You are a helpful assistant that works with PDF documents. "
        "When the user refers to a PDF file, use the 'read_pdf' tool to extract "
        "its text before answering. If the user isn't sure of the file path, "
        "use 'list_pdfs' to help them find it. Always base your answers on the "
        "actual extracted text — don't guess at PDF contents. If a document was "
        "truncated, mention that your answer is based on the available portion."
    ),
    tools=[read_pdf, list_pdfs],
)
