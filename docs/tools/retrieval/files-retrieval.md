# FilesRetrieval

Retrieving and indexing files from a directory is essential when you need to provide an AI agent with context from local text-based content. This allows the agent to perform Retrieval-Augmented Generation (RAG), enabling it to answer questions, summarize information, or perform analysis based on the contents of the files in the specified directory. For example, you could use this functionality to analyze a code project, query a local knowledge base of markdown documents, or understand the key themes across a collection of reports.

## What it does
This agent indexes local text files from the data/ directory using FilesRetrieval (backed by LlamaIndex's VectorStoreIndex and Google's gemini-embedding-2-preview embedding model), then answers user questions by retrieving relevant documents before generating a response.


## Configuration Parameters

### Source Settings
These options define which files are processed and indexed by the tool:
* **input_dir (Required)**: The local file path to the directory containing your source documents (e.g., "./data").
* **recursive**: A boolean value (default: False). If set to True, the tool will also index files in all subdirectories of the input_dir.
* **required_exts**: A list of file extensions to include (e.g., [".md", ".py", ".txt"]). If not specified, the tool typically processes all supported text-based formats.
* **exclude_hidden**: A boolean value (default: True) that determines whether to ignore hidden files and directories (like .git or .env).

### Indexing and Retrieval Settings
These options control the underlying RAG logic, including chunking and vector search:
* **embedding_model**: Specifies the model used to create vector representations of your files. As of ADK v1.28.0, the default is typically gemini-embedding-2-preview.
* **similarity_top_k**: The number of relevant document "chunks" the tool should retrieve to answer a single query. A higher value provides more context but uses more tokens.
* **vector_distance_threshold**: A float used to filter results based on their semantic relevance. Chunks that fall below this similarity score will be ignored.
* **chunk_size / chunk_overlap**: (Optional) These allow fine-grained control over how documents are split into smaller pieces before indexing.

### General Tool Settings
Like all ADK tools, FilesRetrieval includes standard metadata used by the LLM to understand its purpose:
* **name**: The unique identifier for the tool used in the agent's logic (e.g., "technical_docs_retriever").
* **description**: A concise explanation telling the agent when it should use this tool. For example: "Search this tool when the user asks questions about the internal project architecture or source code."

## Get started

The following example shows how to initialize and use the `FilesRetrieval` tool:

```python
from google.adk.tools.retrieval import FilesRetrieval

# Create an instance of the FilesRetrieval tool
files_retrieval_tool = FilesRetrieval(
    name="files_retrieval",
    description="Performs retrieval over a local directory of files.",
    input_dir="/path/to/your/files"
)
```

Now you can use the tool to retrieve information from the files in the specified directory.
