---
catalog_title: Webcite
catalog_description: Parse documents to Markdown and verify claims with cited sources
catalog_icon: /integrations/assets/webcite.png
catalog_tags: ["mcp", "search"]
---

# Webcite MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [Webcite MCP Server](https://github.com/strategyconnect/webcite-mcp-server)
connects your ADK agent to [Webcite](https://webcite.co), an API for document
parsing and claim verification. Your agent can read PDFs, scans, spreadsheets
and office files into Markdown with page provenance, check claims against web
sources or uploaded documents, and return citations bound to the source
passages that support or contradict each claim. Webcite hosts the server at
`https://api.webcite.co/mcp`, so there is nothing to install or run locally.

## Use cases

- **Fact-check agent answers**: Verify a claim before the agent states it and
  report the verdict with the sources that support or contradict it.

- **Document parsing for RAG**: Turn PDFs, scanned pages and spreadsheets into
  Markdown with page-level provenance for indexing and retrieval.

- **Quote checking**: Confirm that quoted passages appear in the sources they
  are attributed to, in batches of up to 200 quotes.

- **Full document review**: Fact-check every claim in a report or deck and get
  a coverage report of which passages were checked.

- **Figure cross-checks**: Extract the figures in a financial document and find
  numbers that conflict with each other.

## Prerequisites

- A Webcite account and API key. Create a key at
  [webcite.co/api-keys](https://webcite.co/api-keys). Tool calls spend credits
  from your plan; see [pricing](https://webcite.co/pricing).
- A [Gemini API key](https://aistudio.google.com/apikey) for the agent's model.
- Python 3.10 or later.

## Installation

Install ADK with the `mcp` extra:

```bash
pip install "google-adk[mcp]"
```

## Use with agent

Set your API keys as environment variables:

```bash
export WEBCITE_API_KEY="<your-webcite-api-key>"
export GOOGLE_API_KEY="<your-gemini-api-key>"
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

The server accepts the API key as a bearer token. The `profile=core` query
parameter serves a 16-tool list that covers every main job; omit it to load
the full default list.

=== "Python"

    === "Remote MCP Server"

        ```python
        import os

        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="webcite_agent",
            instruction=(
                "Check factual claims with verify_claim and report the verdict "
                "with its citations. To read a document from a public URL, call "
                "upload_url and then extract_document with the returned asset_id."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.webcite.co/mcp?profile=core",
                        headers={
                            "Authorization": f"Bearer {os.environ['WEBCITE_API_KEY']}",
                        },
                        timeout=30.0,
                        sse_read_timeout=300.0,
                    ),
                )
            ],
        )
        ```

!!! note

    The `webcite_guide` tool returns the recommended order of tool calls for each
    workflow and costs no credits. Instruct your agent to call it first when
    a request does not map to a single tool.

## Available tools

The `core` profile serves these tools:

Tool | Description
---- | -----------
`webcite_guide` | Returns the workflow for verification, full-document review, source tracing or numeric checks.
`get_credit_balance` | Reads remaining, used and total credits.
`verify_claim` | Verifies a claim against web sources and returns a verdict, a stance for each source and citations.
`search_sources` | Finds sources for a query without a verdict.
`get_source_preview` | Resolves a citation to its source passage and checks that the quote matches it.
`verify_batch` | Checks up to 200 quotes against their sources in one call.
`upload_file` | Uploads a small file (base64) for extraction or as verification context.
`upload_url` | Stores the original file from a public HTTPS URL and returns an `asset_id`.
`extract_document` | Converts an uploaded file to Markdown with page provenance, including OCR for scans.
`extract_figures` | Extracts recognized financial metrics as figures tied to their source.
`analyze_conflicts` | Recomputes and cross-checks figures already extracted.
`review_document` | Starts a full fact-check of a document and returns a job ID.
`get_document_review_job` | Polls a document review job.
`get_document_review` | Pages through saved review results and unchecked source passages.
`list_citations` | Lists past verifications.
`get_citation` | Returns the details of one verification.

## Configuration

Option | Description
------ | -----------
`?profile=core` | A short tool list covering each main job. Other values: `docs`, `research`, `public` (the default).
`?read_only=true` | Serves only the tools marked read-only.
`Authorization: Bearer <key>` | API key authentication. An `x-api-key` header also works. Clients that support OAuth can sign in instead.

## Additional resources

- [Webcite API documentation](https://webcite.co/api-docs)
- [Webcite MCP Server repository](https://github.com/strategyconnect/webcite-mcp-server)
- [Webcite pricing](https://webcite.co/pricing)
