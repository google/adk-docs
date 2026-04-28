# FilesRetrieval

The `FilesRetrieval` tool allows an agent to perform retrieval over a local directory of files.

## Initialization

To use the `FilesRetrieval` tool, you need to initialize it by providing the path to the directory containing the files you want to use for retrieval. You specify this directory using the `input_dir` parameter.

The default embedding model used by the `FilesRetrieval` tool is `gemini-embedding-2-preview`.

## Example

The following example shows how to initialize and use the `FilesRetrieval` tool:

```python
from google.adk.tools.retrieval import FilesRetrieval

# Create an instance of the FilesRetrieval tool
files_retrieval_tool = FilesRetrieval(
    name="files_retrieval",
    description="Performs retrieval over a local directory of files.",
    input_dir="/path/to/your/files"
)

# Now you can use the tool to retrieve information from the files
# in the specified directory.
```
