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