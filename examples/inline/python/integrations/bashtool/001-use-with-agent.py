from google.adk.tools.bash_tool import ExecuteBashTool, BashToolPolicy

policy = BashToolPolicy(
    allowed_command_prefixes=("ls", "cat", "grep"),
    timeout_seconds=30,
    max_memory_bytes=1024 * 1024 * 512,   # 512MB
    max_file_size_bytes=1024 * 1024 * 10, # 10MB
    max_child_processes=5
)

tool = ExecuteBashTool(workspace=my_workspace_path, policy=policy)