---
catalog_title: Bash Tool
catalog_description: Execute bash commands with safeguards for ADK agents.
catalog_icon: /integrations/assets/bash-tool.png
catalog_tags: ["code", "security"]
---

# Bash Tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The ADK Bash Tool allows agents to execute arbitrary bash commands, providing powerful capabilities for system interaction and automation. Due to the inherent security risks of executing shell commands, the Bash Tool integrates with `BashToolPolicy` to define and enforce strict safeguards, preventing unintended or malicious operations.

## Use cases

- **System Automation**: Automate routine system tasks, such as file manipulation, process management, or data retrieval from the local environment.
- **Development and Debugging**: Aid in development workflows by allowing agents to run build commands, tests, or inspect system states.
- **Environment Interaction**: Enable agents to interact with the underlying operating system for tasks that require shell access.
- **Secure Command Execution**: Define granular policies to restrict which commands can be run, in which directories, and with what arguments, ensuring safe operation in sensitive environments.

## Prerequisites

- Python environment with ADK installed.
- Understanding of bash commands and their potential impact.

## Installation

The Bash Tool is part of the `google-adk-tools` package.

```bash
pip install google-adk-tools
```

## Use with agent

The `ExecuteBashTool` is the primary tool for running bash commands. It can be configured with a `BashToolPolicy` to enforce security constraints.

### Basic Usage

Without a policy, `ExecuteBashTool` can run any command. **This is generally not recommended for production environments due to security risks.**

```python
from google.adk.agents import Agent
from google.adk.tools.bash import ExecuteBashTool

# Initialize the Bash Tool without a policy (use with caution!)
bash_tool = ExecuteBashTool()

agent = Agent(
    model="gemini-2.5-pro",
    name="bash_agent",
    instruction="Execute bash commands to interact with the system.",
    tools=[bash_tool],
)

# Example interaction:
# result = agent.generate_response("Run 'ls -l /tmp'")
# print(result.text)
```

### Using BashToolPolicy for Safeguards

`BashToolPolicy` allows you to define rules that restrict the behavior of `ExecuteBashTool`. This is crucial for preventing unintended actions and securing your agent.

A policy can specify:
- `allowed_commands`: A list of command patterns that are explicitly allowed.
- `disallowed_commands`: A list of command patterns that are explicitly disallowed.
- `allowed_directories`: A list of directory patterns where commands are allowed to execute.
- `disallowed_directories`: A list of directory patterns where commands are disallowed to execute.
- `allowed_arguments`: A list of argument patterns that are allowed for specific commands.
- `disallowed_arguments`: A list of argument patterns that are disallowed for specific commands.

Policies are evaluated in order, and the first matching rule determines the outcome.

```python
from google.adk.agents import Agent
from google.adk.tools.bash import ExecuteBashTool, BashToolPolicy

# Define a BashToolPolicy
# This policy allows 'ls' and 'cat' in '/tmp' and '/var/log',
# but disallows 'rm' and any command in '/etc'.
bash_policy = BashToolPolicy(
    allowed_commands=[
        "ls",
        "cat",
    ],
    disallowed_commands=[
        "rm",  # Disallow 'rm' command
        "sudo", # Disallow 'sudo'
    ],
    allowed_directories=[
        "/tmp",
        "/var/log",
    ],
    disallowed_directories=[
        "/etc", # Disallow execution in /etc
        "/root", # Disallow execution in /root
    ],
    # Example of command-specific argument policies
    command_policies={
        "cat": {
            "disallowed_arguments": ["/etc/passwd", "/etc/shadow"] # Disallow reading sensitive files
        }
    }
)

# Initialize the Bash Tool with the defined policy
secure_bash_tool = ExecuteBashTool(policy=bash_policy)

agent = Agent(
    model="gemini-2.5-pro",
    name="secure_bash_agent",
    instruction="Execute bash commands safely with defined policies.",
    tools=[secure_bash_tool],
)

# Example interactions:

# This should work (ls in /tmp)
# result = agent.generate_response("List files in /tmp")
# print(result.text)

# This should be blocked (rm is disallowed)
# result = agent.generate_response("Delete a file in /tmp using rm")
# print(result.text)

# This should be blocked (execution in /etc is disallowed)
# result = agent.generate_response("List files in /etc")
# print(result.text)

# This should be blocked (cat /etc/passwd is disallowed by command_policies)
# result = agent.generate_response("Show content of /etc/passwd")
# print(result.text)
```

## Available tools

Tool | Description
---- | -----------
`execute_bash` | Executes a bash command with optional policy enforcement.

## Resources

- [ADK Tools GitHub Repository](https://github.com/google/adk-tools)
- [Blog Post: Building a Git History Analyzer with Google ADK and LLMs](https://medium.com/@shah.sohil123/building-a-git-history-analyzer-with-google-adk-and-llms-the-hard-parts-nobody-talks-about-770a139840d4?postPublishedType=repub)

## Contributing

Please refer to the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines on how to contribute to the ADK documentation.
