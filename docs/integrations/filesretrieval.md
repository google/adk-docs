---
catalog_title: Files Retrieval Tool
catalog_description: Index and search local documents using vector similarity search
catalog_icon: /integrations/assets/filesretrieval.png
catalog_tags: ["google", "data"]
---

# Files Retrieval tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The `FilesRetrieval` tool lets your ADK agent index and query local documents
using retrieval-augmented generation (RAG). It builds a LlamaIndex
`VectorStoreIndex` over a directory you specify, using Google's
`gemini-embedding-2-preview` embedding model. Your agent can then retrieve
relevant excerpts from local text files, Markdown documents, and source files
to ground its answers in project-specific context.

## Use cases

- **Codebase and Documentation Search**: Retrieve relevant functions, design notes and documentation from a local repository to answer technical questions.
- **Local Knowledge Base Grounding**: Index internal markdown files, technical specifications, and guides straight from your own filesystem, without first loading them into a hosted document store. Document content is sent to the configured embedding model for indexing, so review the data handling terms for Google AI Studio or Agent Platform before indexing sensitive material.
- **Context-Augmented Assistance**: Retrieve relevant domain-specific data from reports, logs, or text files to ground agent responses in verified source material.

## Prerequisites

To use `FilesRetrieval`, configure credentials for either Google AI Studio or Agent Platform:

=== "Google AI Studio"

    Generate an API key in [Google AI Studio](https://aistudio.google.com/) and set the environment variable:

    ```bash
    export GOOGLE_API_KEY="your-api-key"
    ```

=== "Agent Platform"

    Configure Agent Platform access with your Google Cloud credentials:

    ```bash
    export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
    export GOOGLE_CLOUD_PROJECT="your-project-id"
    export GOOGLE_CLOUD_LOCATION="global"
    ```

!!! note
    
    ADK's default embedding model, `gemini-embedding-2-preview`, is a preview endpoint; on Agent Platform it is served from the `us-central1` region and may be removed in the future. For production, pass the GA model explicitly with `embedding_model=GoogleGenAIEmbedding(model_name="gemini-embedding-2", embed_batch_size=1)`.
    
## Use with agent

This example configures `FilesRetrieval` for a local data directory and
attaches it to an ADK agent. Before running it, create a `data/` directory next to your agent module and add the `.txt` or `.md` files you want indexed: `FilesRetrieval` loads and embeds the entire directory when it is constructed, so the directory must already exist, and the content is re-indexed each time the agent module is imported.

```python
import os
from google.adk.agents import Agent
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval

# Path to the directory containing your source documents
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Initialize the FilesRetrieval tool
files_retrieval = FilesRetrieval(
    name="search_documents",
    description=(
        "Search through local documentation files to find relevant"
        " information. Use this tool when the user asks questions about"
        " architecture, project structure, or tools."
    ),
    input_dir=DATA_DIR,
)

# Create an agent equipped with the retrieval tool
root_agent = Agent(
    model="gemini-flash-latest",
    name="files_retrieval_agent",
    instruction=(
        "You are a helpful assistant that answers questions based on local"
        " documentation files. Always use the search_documents tool to retrieve"
        " relevant context before generating your answer."
    ),
    tools=[files_retrieval],
)
```

## Available tools

`FilesRetrieval` is itself a tool. Once attached with `tools=[...]`, the agent sees one function, which takes a single `query` string parameter:

Tool | Description
---- | -----------
`search_documents` | Performs semantic vector search over documents in the indexed directory and returns the most relevant content chunk for a given natural language query. Rename it with the `name` parameter.

## Configuration

The `FilesRetrieval` constructor accepts the following parameters:

Parameter | Type | Required | Default | Description
--------- | ---- | -------- | ------- | -----------
`name` | `str` | **Yes** | — | Unique identifier for the tool, used by the model for function calling.
`description` | `str` | **Yes** | — | Explanation of when and how the agent should invoke the retrieval tool.
`input_dir` | `str` | **Yes** | — | Local filesystem directory path containing the documents to load and index.
`embedding_model` | `Optional[BaseEmbedding]` | No | `None` | Custom LlamaIndex `BaseEmbedding` instance. When omitted, defaults to `GoogleGenAIEmbedding(model_name="gemini-embedding-2-preview", embed_batch_size=1)`.

### Custom embedding models

You can customize the embedding model by passing an instance conforming to LlamaIndex's `BaseEmbedding` interface:

```python
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

custom_embedding = GoogleGenAIEmbedding(
    model_name="gemini-embedding-2",
    embed_batch_size=1,
)

files_retrieval = FilesRetrieval(
    name="search_documents",
    description="Search local knowledge base files.",
    input_dir=os.path.join(os.path.dirname(__file__), "data"),
    embedding_model=custom_embedding,
)
```

## Additional resources

- [Using VectorStoreIndex (LlamaIndex)](https://docs.llamaindex.ai/en/stable/module_guides/indexing/vector_store_index/)
- [llama-index-embeddings-google-genai on PyPI](https://pypi.org/project/llama-index-embeddings-google-genai/)
