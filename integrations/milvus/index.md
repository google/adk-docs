# Milvus integration for ADK

Supported in ADKPython

The [`adk-milvus`](https://github.com/zilliztech/adk-milvus) package connects ADK Python agents to [Milvus](https://milvus.io/), an open-source vector database. Use it for persistent semantic memory through `MilvusMemoryService`, or expose a `milvus_similarity_search` retrieval tool for RAG workflows through `MilvusToolset`.

Milvus can run locally with Milvus Lite, as a self-hosted Milvus server, or as a managed [Zilliz Cloud](https://zilliz.com/cloud) deployment using the same configuration fields.

## Use cases

- **Semantic memory for agents**: Persist session events in Milvus and retrieve relevant memories in later conversations.
- **RAG over private content**: Index documents or snippets and let the agent retrieve relevant context through a tool call.
- **Local-to-cloud development**: Start with Milvus Lite for local development, then switch to a Milvus server or Zilliz Cloud by changing the URI and token.

## Prerequisites

- Python 3.10 or later
- ADK for Python and `adk-milvus`
- An embedding function that returns one vector per input text
- One Milvus deployment:
  - Milvus Lite for local development
  - Milvus server, such as `http://localhost:19530`
  - Zilliz Cloud endpoint and token

## Installation

```bash
pip install adk-milvus
```

This installs the ADK runtime dependencies, PyMilvus, and Milvus Lite support.

## Configuration

Use `MILVUS_URI` and `MILVUS_TOKEN` for all deployment modes:

```bash
# Milvus Lite
export MILVUS_URI="./adk_milvus.db"

# Milvus server
export MILVUS_URI="http://localhost:19530"

# Zilliz Cloud
export MILVUS_URI="https://your-endpoint.api.gcp-us-west1.zillizcloud.com"
export MILVUS_TOKEN="your-token"
```

`MILVUS_TOKEN` is only needed for authenticated deployments such as Zilliz Cloud. If you use a non-default Milvus database, set `MILVUS_DB_NAME`.

## Use with agent

Plug `MilvusMemoryService` into a `Runner` to persist and search cross-session memory.

```python
from adk_milvus import MilvusMemoryService
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import Client

genai_client = Client()

def embedding_function(texts):
    response = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=list(texts),
    )
    return [list(embedding.values) for embedding in response.embeddings]

memory_service = MilvusMemoryService(
    embedding_function=embedding_function,
    dimension=3072,
    collection_name="adk_memory",
)

agent = Agent(
    name="memory_agent",
    model="gemini-flash-latest",
    instruction="Use memory to personalize responses when relevant.",
)

runner = Runner(
    app_name="milvus_memory_app",
    agent=agent,
    session_service=InMemorySessionService(),
    memory_service=memory_service,
)
```

After a useful session, add it to memory and search it later:

```python
session = await runner.session_service.get_session(
    app_name="milvus_memory_app",
    user_id="user-1",
    session_id="session-1",
)
await memory_service.add_session_to_memory(session)

result = await memory_service.search_memory(
    app_name="milvus_memory_app",
    user_id="user-1",
    query="what did the user say about database preferences?",
)
for memory in result.memories:
    print(memory.content.parts[0].text)
```

Use `MilvusVectorStore` to index text, then expose it through `MilvusToolset`.

```python
from adk_milvus import MilvusToolset
from adk_milvus import MilvusVectorStore
from adk_milvus import MilvusVectorStoreSettings
from google.adk.agents import Agent
from google.genai import Client

genai_client = Client()

def embedding_function(texts):
    response = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=list(texts),
    )
    return [list(embedding.values) for embedding in response.embeddings]

vector_store = MilvusVectorStore(
    embedding_function=embedding_function,
    settings=MilvusVectorStoreSettings(
        collection_name="adk_rag",
        dimension=3072,
    ),
)

vector_store.add_texts(
    [
        "Milvus Lite is useful for local RAG development.",
        "Zilliz Cloud provides managed Milvus for production workloads.",
    ],
    metadatas=[
        {"source": "milvus-lite"},
        {"source": "zilliz-cloud"},
    ],
)

milvus_toolset = MilvusToolset(vector_store=vector_store)
tools = await milvus_toolset.get_tools_with_prefix()

agent = Agent(
    name="rag_agent",
    model="gemini-flash-latest",
    instruction="Use retrieval context when answering questions.",
    tools=tools,
)
```

## Available tools and operations

### RAG toolset

| Tool                       | Description                                                                                          |
| -------------------------- | ---------------------------------------------------------------------------------------------------- |
| `milvus_similarity_search` | Search indexed text in Milvus and return matching rows with content, source, metadata, and distance. |

### Memory service

| Method                                    | Description                                      |
| ----------------------------------------- | ------------------------------------------------ |
| `add_session_to_memory(session)`          | Persist text-bearing events from an ADK session. |
| `search_memory(app_name, user_id, query)` | Search memories scoped to an ADK app and user.   |

## Notes

- `dimension` must match the embedding model output dimension.
- `MilvusMemoryService` scopes search by `app_name` and `user_id`.
- `MilvusVectorStore` creates the collection if it does not already exist and validates the existing schema before reuse.
- The collection consistency level and database name can be configured for deployments that need stronger read-after-write behavior or multiple Milvus databases.

## Resources

- [ADK Milvus package](https://github.com/zilliztech/adk-milvus)
- [ADK Milvus on PyPI](https://pypi.org/project/adk-milvus/)
- [Milvus documentation](https://milvus.io/docs)
- [Milvus Lite documentation](https://milvus.io/docs/milvus_lite.md)
- [Zilliz Cloud](https://zilliz.com/cloud)
