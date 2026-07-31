---
catalog_title: Bash Tool
catalog_description: Execute bash commands within a secure, resource-limited local sandbox
catalog_icon: /integrations/assets/bash.png
catalog_tags: ["code", "google"]
---

# Bash Tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span>
  <span class="lst-python">Python</span>
</div>

!!! warning "Warning: Experimental feature"

    The Bash Tool is currently an experimental feature. The API is subject to change.

The `ExecuteBashTool` allows an ADK agent to execute bash commands within a local workspace directory. This tool is useful for file system operations, running scripts, or interacting with the local environment directly through the agent.
The tool is only available for Python ADK.

## Installation

The Bash Tool is included by default in the core Agent Development Kit (ADK). You don't need to install any separate integration packages; simply install the main library:

```bash
pip install google-adk
```

## Configure the Bash Tool

To use the Bash Tool, instantiate `ExecuteBashTool` and include it in your agent's `tools` list: 

```python
from google.adk.tools.bash_tool import ExecuteBashTool, BashToolPolicy
from google.adk.agents import LlmAgent
import pathlib

bash_tool = ExecuteBashTool(
    workspace=pathlib.Path("/path/to/workspace"),
    policy=BashToolPolicy(
        allowed_command_prefixes=("ls", "cat", "grep", "echo"),
        blocked_operators=(">", ">>", "|"),
        timeout_seconds=15,
        max_memory_bytes=1024 * 1024 * 100,
        max_file_size_bytes=1024 * 1024 * 10,
        max_child_processes=5
    )
)

root_agent = LlmAgent(
    name="system_helper",
    model="gemini-flash-latest",
    tools=[bash_tool],
    instruction="You can execute bash commands to help the user."
)
```

## Security and execution safeguards

Because executing arbitrary code carries inherent risks, the `ExecuteBashTool` includes several mandatory and optional security features enforced upon the spawned subprocess:

1. **User Confirmation:** The tool **always** requests user confirmation before executing a command. The framework pauses execution and waits for the user or client application to approve the command via the `adk_request_confirmation` flow.
2. **Command Validation:** You can whitelist specific commands using `allowed_command_prefixes` and strictly forbid certain string patterns using `blocked_operators`.
3. **Resource Limits:** OS-level limits,`setrlimit`, are applied to restrict memory consumption, file sizes, and the number of child processes to prevent fork bombs or memory exhaustion. 
4. **Core Dumps Disabled:** To prevent sensitive memory leaks, core dumps are strictly disabled, `RLIMIT_CORE` set to `0`, for the executing subprocess.
5. **Process Group Termination:** If a command exceeds the `timeout_seconds`, the tool issues a `SIGKILL` to the entire process group to ensure no orphan background processes are left running.
