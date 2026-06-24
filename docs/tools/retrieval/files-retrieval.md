# FilesRetrieval

Retrieving and indexing files from a directory is essential when you need to provide an AI agent with context from local text-based content. This allows the agent to perform Retrieval-Augmented Generation (RAG), enabling it to answer questions, summarize information, or perform analysis based on the contents of the files in the specified directory. For example, you could use this functionality to analyze a code project, query a local knowledge base of markdown documents, or understand the key themes across a collection of reports.

## What it does
This agent indexes local text files from the data/ directory using FilesRetrieval (backed by LlamaIndex's VectorStoreIndex and Google's gemini-embedding-2-preview embedding model), then answers user questions by retrieving relevant documents before generating a response.


## Configuration Parameters

To use the `FilesRetrieval` tool, you need to initialize it by providing the path to the directory containing the files you want to use for retrieval. You specify this directory using the `input_dir` parameter.

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
