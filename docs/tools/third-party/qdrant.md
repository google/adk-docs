# Qdrant

The [Qdrant MCP Server](https://github.com/qdrant/mcp-server-qdrant) connects
your ADK agent to [Qdrant](https://qdrant.tech/), an AI-native vector database
and a semantic search engine. This integration equips your agent with semantic
memory capabilities, allowing it to store and retrieve information based on
meaning rather than exact keywords. By using vector search, your agent can
maintain long-term context, manage dynamic knowledge collections, and recall
relevant details using natural language queries.

## Use cases

- **Semantic Memory**: Give agents long-term memory by storing conversation
  context or facts.
- **RAG (Retrieval-Augmented Generation)**: Connect agents to external knowledge
  bases.
- **Dynamic Knowledge Management**: Allow agents to organize data into different
  collections on the fly.

## Prerequisites

- A running Qdrant instance. You can use the fully managed
  [Qdrant Cloud](https://qdrant.tech/documentation/cloud-intro/) or run a local
  instance.
- A Qdrant API Key (if using Qdrant Cloud). You can generate one in the
  [Qdrant Dashboard](https://cloud.qdrant.tech/). Refer to the
  [documentation](https://qdrant.tech/documentation/cloud/authentication/) for
  more information.
- The [uv tool](https://docs.astral.sh/uv/) installed to start the MCP server
  with `uvx`.

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    QDRANT_URL = "YOUR_QDRANT_URL"
    QDRANT_API_KEY = "YOUR_QDRANT_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="qdrant_agent",
        instruction="Store and retrieve information using Qdrant",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="uvx",
                        args=[
                            "mcp-server-qdrant",
                        ],
                        env={
                            "QDRANT_URL": QDRANT_URL,
                            "QDRANT_API_KEY": QDRANT_API_KEY,
                        }
                    ),
                    timeout=30,
                ),
            )
        ],
    )
    ```

## Example usage

Once your agent is set up and running, you can interact with it through the
command-line interface or web interface. Here are some sample agent prompts:

**Sample agent prompts:**

> Remember that the staging API endpoint is https://api.stage.example.com and store it in the dev_notes collection.

<!-- -->

> What was the API endpoint I told you about earlier? Check the dev_notes collection.

<!-- -->

> Store a note in the dev_notes collection that we decided to migrate the database to v2 next week.

The agent automatically calls Qdrant tools to store and retrieve information:

<img src="../../../assets/tools-qdrant-screenshot.png">

## Available tools

Tool | Description
---- | -----------
`qdrant-store` | Store some information in the Qdrant database
`qdrant-find` | Retrieve relevant information from the Qdrant database

## Configuration

The Qdrant MCP server can be configured using the following environment variables:

Variable <img width="150px"/> | Description | Default
-------- | ----------- | -------
`QDRANT_URL` | URL of the Qdrant server (e.g., Qdrant Cloud URL) | None
`QDRANT_API_KEY` | API key for the Qdrant server | None
`COLLECTION_NAME` | Name of the default collection to use | None
`QDRANT_LOCAL_PATH` | Path to a local Qdrant database (alternative to `QDRANT_URL`) | None
`EMBEDDING_PROVIDER` | Embedding provider to use (currently only `fastembed` is supported) | `fastembed`
`EMBEDDING_MODEL` | Name of the embedding model to use | `sentence-transformers/all-MiniLM-L6-v2`
`TOOL_STORE_DESCRIPTION` | Custom description for the qdrant-store tool | Refer to [docs](https://github.com/qdrant/mcp-server-qdrant)
`TOOL_FIND_DESCRIPTION` | Custom description for the qdrant-find tool | Refer to [docs](https://github.com/qdrant/mcp-server-qdrant)

## Additional resources

- [Qdrant MCP Server Repository](https://github.com/qdrant/mcp-server-qdrant)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
