from google.adk.agents.run_config import RunConfig

# VAD is enabled by default - no explicit configuration needed
run_config = RunConfig(
    response_modalities=["AUDIO"]
)