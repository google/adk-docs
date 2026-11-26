---
catalog_title: OpenDocKit
catalog_description: Read local PDF, Office, and HWP documents as Markdown
catalog_icon: /integrations/assets/opendockit.png
catalog_tags: ["mcp"]
---

# OpenDocKit MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [OpenDocKit MCP Server](https://github.com/hyeonsang010716/OpenDocKit)
lets your ADK agent read documents from the local file system as Markdown. It
reads PDF, Word, PowerPoint, Excel, CSV, HWP and HWPX, OpenDocument, RTF, EPUB,
HTML, and email (`.eml`) files. Tables are kept as tables, and equations in
Word, PowerPoint, HWP, and HTML files become LaTeX. The conversion runs on your
machine with rules rather than a model, so it needs no account or API key and
makes no network calls.

## Use cases

- **Answer questions from local files**: Let the agent read reports,
  contracts, slide decks, and spreadsheets on disk, with their tables kept as
  tables (Markdown, or HTML where cells are merged).

- **Read long documents in parts**: For a PDF, a slide deck, or a workbook, the
  agent asks for the outline first, then reads only the pages, slides, or sheets
  it needs, so a large file does not fill the context window.

- **Work with Korean documents**: Read HWP and HWPX files, the formats of the
  Hangul word processor, including their tables, footnotes, and equations.

- **Read files that must stay local**: Work with documents that should not be
  uploaded to a hosted parsing service.

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/), which starts
  the server with `uvx`. The first start installs OpenDocKit from
  [PyPI](https://pypi.org/project/opendockit-mcp/), and Python 3.12 or later if
  the machine has none.
- ADK with MCP support: `pip install "google-adk[mcp]"` for Python, or
  `npm install @google/adk @modelcontextprotocol/sdk` for TypeScript.
- A folder of documents for the agent to read.
- Optional: [LibreOffice](https://www.libreoffice.org/), to read legacy `.doc`
  and `.ppt` files. The other formats need nothing else.

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        DOCUMENTS_DIR = "/path/to/your/documents"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="opendockit_agent",
            instruction=(
                f"The user's documents are in {DOCUMENTS_DIR}. Answer from them with "
                "the OpenDocKit tools. For a long PDF, slide deck, or workbook, call "
                "document_outline first and read only the sections you need."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["opendockit-mcp", "--root", DOCUMENTS_DIR],
                            # File names the agent gives are read from this folder
                            cwd=DOCUMENTS_DIR,
                        ),
                        # Seconds to wait for the server to start and for each tool
                        # call. The first start installs the package, and the server
                        # stops a conversion after 2 minutes.
                        timeout=180,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const DOCUMENTS_DIR = "/path/to/your/documents";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "opendockit_agent",
            instruction:
                `The user's documents are in ${DOCUMENTS_DIR}. Answer from them with ` +
                "the OpenDocKit tools. For a long PDF, slide deck, or workbook, call " +
                "document_outline first and read only the sections you need.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["opendockit-mcp", "--root", DOCUMENTS_DIR],
                        // File names the agent gives are read from this folder
                        cwd: DOCUMENTS_DIR,
                    },
                    // Seconds to wait for the server to start and for each tool
                    // call. The first start installs the package, and the server
                    // stops a conversion after 2 minutes.
                    timeout: 180,
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

Tool | Description
---- | -----------
`document_outline` | Describes a document without returning its text: format, title, size, and its pages, slides, or sheets with their numbers, titles, and lengths
`convert_document` | Returns a document as Markdown, whole or only the pages, slides, or sheets given in `sections` (`"3"` or `"2-5"`). At most `max_chars` characters are returned (100,000 by default), followed by a note when the text is cut

The server does not list folders: the agent needs a file's name in the working
folder, or its full path. Pages, slides, and sheets exist in PDF, presentation,
and spreadsheet files. Other formats, such as Word and HWP, are one section,
and the note on a cut text tells the agent to ask for a larger `max_chars`.

## Configuration

Add these arguments after `opendockit-mcp` in `args`:

Argument | Description
-------- | -----------
`--root DIR` | Folder the server may read; repeat it for several folders. Folders in the `OPENDOCKIT_MCP_ROOTS` environment variable (separated like `PATH`) are added to them. Each must exist, or the server does not start. Without any, the server reads every file the user running it can read.
`--max-chars N` | Default limit on the characters one call returns (100,000)

!!! note

    Each file is converted in a separate process, which is stopped after 2
    minutes, and on Linux and Windows also at 2 GB of memory. Files larger than
    50 MB are refused. There is no OCR: a scanned page comes back without text,
    and the tool's answer says so.

!!! warning

    A document can contain sentences addressed to the agent. The server returns
    what the file says, so give it only the folders you would hand the agent
    yourself. The server changes no files in those folders.

## Additional resources

- [OpenDocKit Repository](https://github.com/hyeonsang010716/OpenDocKit)
- [OpenDocKit MCP Server Documentation](https://github.com/hyeonsang010716/OpenDocKit/blob/main/docs/integrations.md#mcp-server)
- [Supported Formats](https://github.com/hyeonsang010716/OpenDocKit/blob/main/docs/formats.md)
- [opendockit-mcp on PyPI](https://pypi.org/project/opendockit-mcp/)
