---
catalog_title: Bash Tool
catalog_description: Run approved commands in a local workspace with resource limits
catalog_icon: /integrations/assets/bash.png
catalog_tags: ["code", "google"]
---

# Bash Tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.27.0</span>
</div>

The `ExecuteBashTool` allows an ADK agent to execute bash commands within a local workspace directory. This tool is useful for file system operations, running scripts, or interacting with the local environment directly through the agent.
The tool is only available for Python ADK.

## Installation

The Bash Tool is included by default in the core Agent Development Kit (ADK). You don't need to install any separate integration packages; simply install the main library:

```bash
pip install google-adk
```

## Use with agent

!!! warning "POSIX-only"

    `ExecuteBashTool` is currently supported **only on POSIX systems** such as Linux or macOS. On Windows, the tool returns an error response.

To use the Bash Tool, create a workspace and include `ExecuteBashTool` in your
agent's `tools` list:

```python
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools.bash_tool import ExecuteBashTool, BashToolPolicy

workspace = Path("workspace")
workspace.mkdir(exist_ok=True)

policy = BashToolPolicy(
    allowed_command_prefixes=("ls", "cat", "grep"),
    timeout_seconds=30,
    max_memory_bytes=1024 * 1024 * 512,   # 512MB
    max_file_size_bytes=1024 * 1024 * 10, # 10MB
    max_child_processes=5
)

root_agent = Agent(
    name="workspace_agent",
    model="gemini-flash-latest",
    instruction="Inspect files in the workspace using approved commands.",
    tools=[ExecuteBashTool(workspace=workspace, policy=policy)],
)
```

## Security and execution safeguards

Because executing arbitrary code carries inherent risks, the `ExecuteBashTool` includes several mandatory and optional security features enforced upon the spawned subprocess.

### Default policy allows all commands

By default, `BashToolPolicy` is initialized with `allowed_command_prefixes=("*",)`. This means that **all commands are permitted by default**. To secure your application, you must explicitly restrict the allowed commands when initializing the policy:

```python
from google.adk.tools.bash_tool import BashToolPolicy

strict_policy = BashToolPolicy(
    allowed_command_prefixes=("ls", "cat", "git status")
)
```

Entries match whole command tokens. For example, `"ls"` permits `ls -la`, but
not `lsof`, `./ls`, or `/bin/ls`. To allow an absolute executable path, list it
explicitly. The `"git status"` entry permits `git status --short`, but not
`git commit`.

Commands run directly without a shell. Pipes, redirection, wildcard expansion,
and command substitution are not evaluated. For example, `ls *.txt` passes
the literal argument `*.txt` to `ls`. To reject specific strings before
execution, set `blocked_operators`; it is empty by default.

The workspace sets the working directory, but does not isolate the process
from the rest of the filesystem. Allowing an interpreter such as `bash` or
`python` also allows it to run scripts or code. Use an isolated execution
environment when commands need stronger separation from the host.

### Built-in protections

1. **User Confirmation:** The tool **always** requests user confirmation before executing a command. The framework pauses execution and waits for the user or client application to approve the command via the `adk_request_confirmation` flow.
2. **Command Validation:** You can whitelist specific commands using `allowed_command_prefixes` and strictly forbid certain string patterns using `blocked_operators`.
3. **Resource Limits:** OS-level limits,`setrlimit`, are applied to restrict memory consumption, file sizes, and the number of child processes to prevent fork bombs or memory exhaustion. 
4. **Core Dumps Disabled:** To prevent sensitive memory leaks, core dumps are strictly disabled, `RLIMIT_CORE` set to `0`, for the executing subprocess.
5. **Process Group Termination:** If a command exceeds the `timeout_seconds`, the tool issues a `SIGKILL` to the entire process group to ensure no orphan background processes are left running.

## Command results

After a confirmed command finishes, the tool returns a dictionary containing
`stdout`, `stderr`, and the process `returncode`. For example:

```json
{
  "stdout": "report.txt\n",
  "stderr": "<no stderr captured>",
  "returncode": 0
}
```

An empty output stream is represented by `<no stdout captured>` or
`<no stderr captured>`. A nonzero exit code is returned in `returncode` without
adding an `error` field, so check the exit code as well as any error message.

Validation failures, pending or rejected confirmation, and unsupported
platforms return an `error` message without the process fields. A timeout
returns `error` together with the captured output and `returncode`. Other
execution exceptions return `error` and the output fields, but may omit
`returncode`.

## Available tools

| Tool Name | Class Name | Description |
| :--- | :--- | :--- |
| `execute_bash` | `ExecuteBashTool` | Executes a bash command within a workspace. POSIX only |
