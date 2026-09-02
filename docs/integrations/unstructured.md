---
catalog_title: Unstructured
catalog_description: Parse PDFs, Office docs, images, and 40+ file types into structured, AI-ready data
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
emails, images, and scanned files (40+
[supported file types](https://docs.unstructured.io/transform/supported-file-types)
in total) into partitioned, enriched, chunked, and embedded output using
natural language. Transform is a hosted remote MCP server, so there is nothing
to install or run locally.

## Use cases

- **RAG ingestion**: Parse heterogeneous document collections into clean,
  chunked, embedding-ready output for vector stores and retrieval pipelines.

- **Document Q&A agents**: Let an agent fetch and parse a contract, report, or
  paper on demand, then answer questions grounded in the parsed content.

- **Format normalization**: Convert mixed inputs (scanned PDFs, spreadsheets,
  presentations, email threads) into one consistent structured representation.

- **OCR at agent runtime**: Extract text and structure from images and scanned
  documents as a step inside a larger agent workflow.

- **Structured data extraction**: Pull named fields out of forms, invoices, and
  contracts as JSON matching a schema, either one you supply or one the server
  drafts from the document.

## Prerequisites

- An [Unstructured account](https://transform.unstructured.io) and API key.
  See [Get your API key](https://docs.unstructured.io/transform/code#get-your-unstructured-api-key-and-url).
- A [Gemini API key](https://aistudio.google.com/apikey) for the agent's model.
- Python 3.10 or later.

## Installation

Install ADK with the `mcp` extra. The extra is required; without it, ADK's
MCP classes are not importable:

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

The server authenticates with your Unstructured API key as a bearer token on
every request, including the initial handshake. The `wait_seconds` helper lets
the agent pause between status checks, because parsing jobs run asynchronously:

=== "Python"

    === "Remote MCP Server"

        ```python
        --8<-- "examples/inline/python/integrations/unstructured/001-use-with-agent.py"
        ```

!!! note

    Transforming a document is asynchronous: `start_transform_job` starts a
    job, the agent polls `check_job_status`, and `get_job_results` returns
    pre-signed download URLs for the output. Instruct your agent to
    pause between status checks, as shown above, so a polling loop does not
    burn through model rate limits.

    Structured-data extraction is a second asynchronous job that runs on the
    element JSON of a completed parse, identified by the `output_ref` that
    `get_job_results` returns for each file. A prompt that parses and then
    extracts therefore runs two polling loops, so allow for the extra time and
    model steps.

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
`start_transform_job` | Starts a parsing job for uploaded files or public HTTP(S) URLs; returns a `job_id`.
`suggest_extraction_schema_for_file` | Drafts a JSON Schema from one parsed document's element JSON, for when you do not have a schema yet.
`start_extraction_job` | Starts a structured-data extraction job over parsed element JSON against a JSON Schema; returns a `job_id`.
`check_job_status` | Reports whether a job is `SCHEDULED`, `IN_PROGRESS`, or `COMPLETED`. Serves both parsing and extraction jobs.
`get_job_results` | Returns a completed job's output: pre-signed download URLs for a parsing job, or the extracted data inline for an extraction job.

## Resources

- [Unstructured Transform documentation](https://docs.unstructured.io/transform/overview)
- [ADK installation guide for Unstructured Transform](https://docs.unstructured.io/transform/install/google-adk)
- [Supported file types](https://docs.unstructured.io/transform/supported-file-types)
