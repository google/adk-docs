# Bash Tool

The `ExecuteBashTool` allows an agent to execute bash commands within a local workspace directory. This tool is useful for file system operations, running scripts, or interacting with the local environment.

## Usage

To use the Bash tool, instantiate `ExecuteBashTool` and add it to your agent's tools.

```python
from google.adk.tools.bash_tool import ExecuteBashTool, BashToolPolicy
from google.adk.agents import LlmAgent

# Create the tool with a policy
bash_tool = ExecuteBashTool(
    workspace="/path/to/workspace", # Defaults to current working directory
    policy=BashToolPolicy(allowed_command_prefixes=("ls", "cat", "grep")) # Whitelist commands
)

agent = LlmAgent(
    name="system_helper",
    model="gemini-2.0-flash",
    tools=[bash_tool],
    instruction="You can execute bash commands to help the user."
)
```

## Security

The `ExecuteBashTool` includes several security features:

1.  **Prefix Policy:** You can restrict which commands are allowed using `BashToolPolicy(allowed_command_prefixes=...)`. By default, all commands are allowed (`("*",)`).
2.  **User Confirmation:** The tool **always** requests user confirmation before executing a command. The framework will pause execution and wait for the user (or client application) to approve the command via the `adk_request_confirmation` flow.

## Configuration

*   **`workspace`** (`pathlib.Path | None`): The directory where commands will be executed. Defaults to the current working directory.
*   **`policy`** (`BashToolPolicy | None`): Configuration for allowed command prefixes.
