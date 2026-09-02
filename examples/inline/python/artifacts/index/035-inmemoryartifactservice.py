from google.adk.artifacts import InMemoryArtifactService

# Simply instantiate the class
in_memory_service_py = InMemoryArtifactService()

# Then pass it to the Runner
# runner = Runner(..., artifact_service=in_memory_service_py)