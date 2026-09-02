from google.adk.agents.run_config import RunConfig, StreamingMode

config = RunConfig(
    streaming_mode=StreamingMode.SSE,
    max_llm_calls=200,
)

async for event in runner.run_async(
    ...,
    run_config=config,
):
    ...