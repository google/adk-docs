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