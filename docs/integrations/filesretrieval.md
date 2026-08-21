---
catalog_title: Files Retrieval Tool
catalog_description: Index and search local documents using vector similarity search
catalog_icon: /integrations/assets/fileretrieval.png
catalog_tags: ["google", "data"]
---

# Files Retrieval tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The `FilesRetrieval` tool enables ADK agents to index and query local documents using retrieval-augmented generation (RAG). Backed by LlamaIndex's `VectorStoreIndex` and Google's `gemini-embedding-2-preview` embedding model, this integration allows agents to retrieve relevant excerpts from local text files, markdown documents, and source files to answer questions accurately with project-specific context.

## Use cases

- **Codebase and Documentation Search**: Retrieve relevant functions, architecture diagrams, and documentation notes from a local repository to answer technical questions.
- **Local Knowledge Base Grounding**: Provide agents with access to internal markdown files, technical specifications, and guides without uploading data to external third-party services.
- **Context-Augmented Assistance**: Retrieve relevant domain-specific data from reports, logs, or text files to ground agent responses in verified source material.

## Prerequisites

To use `FilesRetrieval`, configure credentials for either Google AI Studio or Agent Platform:

=== "Google AI Studio"

    Generate an API key in [Google AI Studio](https://aistudio.google.com/) and set the environment variable:

    ```bash
    export GOOGLE_API_KEY="your-api-key"
    ```

=== "Agent Platform"

    Configure the Agent Platform access with Google Cloud credentials:

    ```bash
    export GOOGLE_GENAI_USE_ENTERPRISE=1
    export GOOGLE_CLOUD_PROJECT="your-project-id"
    export GOOGLE_CLOUD_LOCATION="us-central1"
    ```

!!! note
    The default `gemini-embedding-2-preview` model is currently hosted in the `us-central1` region.

## Installation

Install the ADK extensions package and the Google GenAI embedding provider for LlamaIndex:

```bash
pip install "google-adk[extensions]"
pip install llama-index-embeddings-google-genai
```

## Use with agent

The following example demonstrates how to configure `FilesRetrieval` for a local data directory and attach it to an ADK agent:

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

When initialized, `FilesRetrieval` registers a function tool with the agent:

Tool | Description
---- | -----------
`search_documents` (configurable via `name`) | Performs semantic vector search over documents in the indexed directory and returns the most relevant content chunk for a given natural language query.

## Configuration

The `FilesRetrieval` constructor accepts the following parameters:

Parameter | Type | Required | Default | Description
--------- | ---- | -------- | ------- | -----------
`name` | `str` | **Yes** | — | Unique identifier for the tool, used by the model for function calling.
`description` | `str` | **Yes** | — | Explanation of when and how the agent should invoke the retrieval tool.
`input_dir` | `str` | **Yes** | — | Local filesystem directory path containing the documents to load and index.
`embedding_model` | `Optional[BaseEmbedding]` | No | `None` (`gemini-embedding-2-preview`) | Custom LlamaIndex `BaseEmbedding` instance. When omitted, defaults to `GoogleGenAIEmbedding(model_name="gemini-embedding-2-preview", embed_batch_size=1)`.

### Custom embedding models

You can customize the embedding model by passing an instance conforming to LlamaIndex's `BaseEmbedding` interface:

```python
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

custom_embedding = GoogleGenAIEmbedding(
    model_name="text-embedding-004",
    embed_batch_size=10,
)

files_retrieval = FilesRetrieval(
    name="search_documents",
    description="Search local knowledge base files.",
    input_dir="./data",
    embedding_model=custom_embedding,
)
```
