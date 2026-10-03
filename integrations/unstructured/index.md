# Unstructured Transform MCP tool for ADK

Supported in ADKPython

The [Unstructured Transform MCP Server](https://docs.unstructured.io/transform/overview) connects your ADK agent to [Unstructured](https://unstructured.io), a document processing platform that turns raw files into structured, AI-ready data. This integration gives your agent the ability to parse PDFs, Office documents, emails, images, and scanned files (40+ [supported file types](https://docs.unstructured.io/transform/supported-file-types) in total) into partitioned, enriched, chunked, and embedded output using natural language. Transform is a hosted remote MCP server, so there is nothing to install or run locally.

## Use cases

- **RAG ingestion**: Parse heterogeneous document collections into clean, chunked, embedding-ready output for vector stores and retrieval pipelines.
- **Document Q&A agents**: Let an agent fetch and parse a contract, report, or paper on demand, then answer questions grounded in the parsed content.
- **Format normalization**: Convert mixed inputs (scanned PDFs, spreadsheets, presentations, email threads) into one consistent structured representation.
- **OCR at agent runtime**: Extract text and structure from images and scanned documents as a step inside a larger agent workflow.
- **Structured data extraction**: Pull named fields out of forms, invoices, and contracts as JSON matching a schema, either one you supply or one the server drafts from the document.

## Prerequisites

- An [Unstructured account](https://transform.unstructured.io) and API key. See [Get your API key](https://docs.unstructured.io/transform/code#get-your-unstructured-api-key-and-url).
- A [Gemini API key](https://aistudio.google.com/apikey) for the agent's model.
- Python 3.10 or later.

## Installation

Install ADK with the `mcp` extra. The extra is required; without it, ADK's MCP classes are not importable:

```bash
pip install "google-adk[mcp]"
```

## Use with agent

Set your API keys as environment variables:

```bash
export UNSTRUCTURED_API_KEY="<your-unstructured-api-key>"
export GOOGLE_API_KEY="<your-gemini-api-key>"
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

The server authenticates with your Unstructured API key as a bearer token on every request, including the initial handshake. The `wait_seconds` helper lets the agent pause between status checks, because parsing jobs run asynchronously:

```python
import asyncio
import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams


async def wait_seconds(seconds: int) -> dict:
    """Pause before the next status check. Use 30 seconds unless told otherwise.

    Args:
        seconds: How long to wait.

    Returns:
        dict confirming the wait.
    """
    seconds = max(1, min(int(seconds), 120))
    await asyncio.sleep(seconds)
    return {"waited_seconds": seconds}


root_agent = Agent(
    model="gemini-flash-latest",
    name="transform_agent",
    instruction=(
        "You parse documents with the Unstructured Transform MCP server. "
        "Pass public https:// file URLs straight to start_transform_job. It "
        "returns a job_id; poll with check_job_status, calling "
        "wait_seconds(30) between checks (jobs take 30 seconds to a few "
        "minutes). When the job completes, call get_job_results and "
        "report the parsed content back to the user. start_transform_job "
        "accepts an optional stages config; it auto-selects a parse "
        "strategy by default, but if the output looks low quality "
        "(garbled text or lost tables), re-run the file with a hi_res "
        "partition strategy for a cleaner result. If the user wants "
        "specific fields rather than the whole document, extract "
        "instead of just parsing. The extraction tools read the element "
        "JSON a parse produces, so parse the file first and keep the "
        "output_ref that get_job_results returns for it. Call "
        "suggest_extraction_schema_for_file with that output_ref when "
        "you need a schema, then start_extraction_job with "
        "element_json_refs set to the output_refs and schema_to_extract "
        "set to a JSON Schema passed as a JSON string. Poll and read an "
        "extraction job with check_job_status and get_job_results like "
        "any other job; its results come back inline, wrapped with the "
        "source filename, so report that filename with each object. If "
        "asked to parse a local file, explain that this requires the "
        "upload helper from the Unstructured ADK guide."
    ),
    tools=[
        wait_seconds,
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.transform.unstructured.io",  # root URL; do not append /mcp
                headers={
                    "Authorization": f"Bearer {os.environ['UNSTRUCTURED_API_KEY']}",
                },
                timeout=30.0,  # ADK's 5s default is too short for a remote handshake
                sse_read_timeout=300.0,
            ),
            tool_filter=[
                "request_file_upload_url",
                "start_transform_job",
                "suggest_extraction_schema_for_file",
                "start_extraction_job",
                "check_job_status",
                "get_job_results",
            ],
        )
    ],
)
```

Note

Transforming a document is asynchronous: `start_transform_job` starts a job, the agent polls `check_job_status`, and `get_job_results` returns pre-signed download URLs for the output. Instruct your agent to pause between status checks, as shown above, so a polling loop does not burn through model rate limits.

Structured-data extraction is a second asynchronous job that runs on the element JSON of a completed parse, identified by the `output_ref` that `get_job_results` returns for each file. A prompt that parses and then extracts therefore runs two polling loops, so allow for the extra time and model steps.

To parse **local** files, the agent also needs a plain function tool that HTTP `PUT`s the file bytes to the pre-signed URL returned by `request_file_upload_url` (this upload is not an MCP call, and it must not send the `Authorization` header). A complete agent with the upload and wait helpers is in the [Unstructured Transform ADK guide](https://docs.unstructured.io/transform/install/google-adk).

## Available tools

| Tool                                 | Description                                                                                                                       |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| `request_file_upload_url`            | Returns a pre-signed upload URL and file reference for a local file.                                                              |
| `start_transform_job`                | Starts a parsing job for uploaded files or public HTTP(S) URLs; returns a `job_id`.                                               |
| `suggest_extraction_schema_for_file` | Drafts a JSON Schema from one parsed document's element JSON, for when you do not have a schema yet.                              |
| `start_extraction_job`               | Starts a structured-data extraction job over parsed element JSON against a JSON Schema; returns a `job_id`.                       |
| `check_job_status`                   | Reports whether a job is `SCHEDULED`, `IN_PROGRESS`, or `COMPLETED`. Serves both parsing and extraction jobs.                     |
| `get_job_results`                    | Returns a completed job's output: pre-signed download URLs for a parsing job, or the extracted data inline for an extraction job. |

## Resources

- [Unstructured Transform documentation](https://docs.unstructured.io/transform/overview)
- [ADK installation guide for Unstructured Transform](https://docs.unstructured.io/transform/install/google-adk)
- [Supported file types](https://docs.unstructured.io/transform/supported-file-types)
