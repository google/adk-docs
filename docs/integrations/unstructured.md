---
catalog_title: Unstructured
catalog_description: Parse PDFs, Office docs, images, and 60+ file types into structured, AI-ready data
catalog_icon: /integrations/assets/unstructured.png
catalog_tags: ["mcp"]
---

# Unstructured Transform MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [Unstructured Transform MCP Server](https://docs.unstructured.io/transform/overview)
connects your ADK agent to [Unstructured](https://unstructured.io), a document
processing platform that turns raw files into structured, AI-ready data. This
integration gives your agent the ability to parse PDFs, Office documents,
emails, images, and scanned files — 60+
[supported file types](https://docs.unstructured.io/transform/supported-file-types)
in total — into partitioned, enriched, chunked, and embedded output using
natural language. Transform is a hosted remote MCP server, so there is nothing
to install or run locally.

## Use cases

- **RAG ingestion**: Parse heterogeneous document collections into clean,
  chunked, embedding-ready output for vector stores and retrieval pipelines.

- **Document Q&A agents**: Let an agent fetch and parse a contract, report, or
  paper on demand, then answer questions grounded in the parsed content.

- **Format normalization**: Convert mixed inputs — scanned PDFs, spreadsheets,
  presentations, email threads — into one consistent structured representation.

- **OCR at agent runtime**: Extract text and structure from images and scanned
  documents as a step inside a larger agent workflow.

## Prerequisites

- An [Unstructured account](https://transform.unstructured.io) and API key.
  See [Get your API key](https://docs.unstructured.io/transform/code#get-your-unstructured-api-key-and-url).
- Python 3.10 or later.

## Installation

Install ADK with the `mcp` extra. The extra is required — without it, ADK's
MCP classes are not importable:

```bash
pip install "google-adk[mcp]"
```

## Use with agent

The server authenticates with your Unstructured API key as a bearer token on
every request, including the initial handshake:

```python
import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

root_agent = Agent(
    model="gemini-flash-latest",
    name="transform_agent",
    instruction=(
        "You parse documents with the Unstructured Transform MCP server. "
        "Pass public https:// file URLs straight to transform_files. It "
        "returns a job_id; poll with check_transform_status, waiting about "
        "30 seconds between checks - jobs take 30 seconds to a few minutes. "
        "When the job completes, call get_transform_results and report the "
        "parsed content back to the user."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.transform.unstructured.io",  # root URL - do not append /mcp
                headers={
                    "Authorization": f"Bearer {os.environ['UNSTRUCTURED_API_KEY']}",
                },
                timeout=30.0,  # ADK's 5s default is too short for a remote handshake
                sse_read_timeout=300.0,
            ),
            tool_filter=[
                "request_file_upload_url",
                "transform_files",
                "check_transform_status",
                "get_transform_results",
            ],
        )
    ],
)
```

!!! note

    Transforming a document is asynchronous: `transform_files` starts a job,
    the agent polls `check_transform_status`, and `get_transform_results`
    returns pre-signed download URLs for the output. Instruct your agent to
    pause between status checks, as shown above, so a polling loop does not
    burn through model rate limits.

    To parse **local** files, the agent also needs a plain function tool that
    HTTP `PUT`s the file bytes to the pre-signed URL returned by
    `request_file_upload_url` (this upload is not an MCP call, and it must not
    send the `Authorization` header). A complete agent with the upload and
    wait helpers is in the
    [Unstructured Transform ADK guide](https://docs.unstructured.io/transform/install/google-adk).

## Available tools

Tool | Description
---- | -----------
`request_file_upload_url` | Returns a pre-signed upload URL and file reference for a local file.
`transform_files` | Starts a parsing job for uploaded files or public HTTP(S) URLs; returns a `job_id`.
`check_transform_status` | Reports whether a job is `SCHEDULED`, `IN_PROGRESS`, or `COMPLETED`.
`get_transform_results` | Returns the parsed output and pre-signed download URLs for a completed job.

## Resources

- [Unstructured Transform documentation](https://docs.unstructured.io/transform/overview)
- [ADK installation guide for Unstructured Transform](https://docs.unstructured.io/transform/install/google-adk)
- [Supported file types](https://docs.unstructured.io/transform/supported-file-types)
