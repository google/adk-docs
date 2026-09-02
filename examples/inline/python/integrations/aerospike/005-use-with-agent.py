from adk_aerospike import (
    AerospikeArtifactService,
    AerospikeMemoryService,
    AerospikeSessionService,
)
from google.adk.agents import LlmAgent
from google.adk.runners import Runner

uri = "aerospike://localhost:3000/adk"

session_service = AerospikeSessionService.from_uri(uri)
artifact_service = AerospikeArtifactService.from_uri(uri)
memory_service = AerospikeMemoryService.from_uri(uri)

agent = LlmAgent(name="assistant", model="gemini-flash-latest")
runner = Runner(
    agent=agent,
    app_name="myapp",
    session_service=session_service,
    artifact_service=artifact_service,
    memory_service=memory_service,
)