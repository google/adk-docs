from google.adk.agents.run_config import RunConfig, ToolThreadPoolConfig

config = RunConfig(
    save_live_blob=True,
    tool_thread_pool_config=ToolThreadPoolConfig(max_workers=8),
)