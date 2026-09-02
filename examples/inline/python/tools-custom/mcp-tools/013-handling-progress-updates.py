async def my_progress_callback(progress: float, total: float, message: str):
    print(f"Progress: {progress}/{total} - {message}")

toolset = McpToolset(
    connection_params=...,
    progress_callback=my_progress_callback
)