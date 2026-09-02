---
catalog_title: Bash Tool
catalog_description: Execute bash commands within a secure, resource-limited local sandbox
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

    `ExecuteBashTool` is currently supported **only on POSIX systems** such as Linux or macOS. Executing this tool on a Windows system will result in a hard error.

To use the Bash Tool, instantiate `ExecuteBashTool` and include it in your agent's `tools` list. Ensure `my_workspace_path` is defined prior to running the snippet as a valid directory path string:

```python
--8<-- "examples/inline/python/integrations/bashtool/001-use-with-agent.py"
```

## Security and execution safeguards

Because executing arbitrary code carries inherent risks, the `ExecuteBashTool` includes several mandatory and optional security features enforced upon the spawned subprocess.

### Default policy allows all commands

By default, `BashToolPolicy` is initialized with `allowed_command_prefixes=("*",)`. This means that **all commands are permitted by default**. To secure your application, you must explicitly restrict the allowed commands when initializing the policy:

```python
--8<-- "examples/inline/python/integrations/bashtool/002-default-policy-allows-all-commands.py"
```

### Built-in protections

1. **User Confirmation:** The tool **always** requests user confirmation before executing a command. The framework pauses execution and waits for the user or client application to approve the command via the `adk_request_confirmation` flow.
2. **Command Validation:** You can whitelist specific commands using `allowed_command_prefixes` and strictly forbid certain string patterns using `blocked_operators`.
3. **Resource Limits:** OS-level limits,`setrlimit`, are applied to restrict memory consumption, file sizes, and the number of child processes to prevent fork bombs or memory exhaustion. 
4. **Core Dumps Disabled:** To prevent sensitive memory leaks, core dumps are strictly disabled, `RLIMIT_CORE` set to `0`, for the executing subprocess.
5. **Process Group Termination:** If a command exceeds the `timeout_seconds`, the tool issues a `SIGKILL` to the entire process group to ensure no orphan background processes are left running.

## Available tools

| Tool Name | Class Name | Description |
| :--- | :--- | :--- |
| `execute_bash` | `ExecuteBashTool` | Executes a bash command within a workspace. POSIX only |
