# Daytona plugin for ADK

Supported in ADKPython

The [Daytona ADK plugin](https://github.com/daytonaio/daytona-adk-plugin) connects your ADK agent to [Daytona](https://www.daytona.io/) sandboxes. This integration gives your agent the ability to execute code, run shell commands, and manage files in isolated environments, enabling secure execution of AI-generated code.

## Use cases

- **Secure Code Execution**: Run Python, JavaScript, and TypeScript code in isolated sandboxes without risking your local environment.
- **Shell Command Automation**: Execute shell commands with configurable timeouts and working directories for build tasks, installations, or system operations.
- **File Management**: Upload scripts and datasets to sandboxes, then retrieve generated outputs and results.

## Prerequisites

- A [Daytona](https://www.daytona.io/) account
- Daytona API key

## Installation

```bash
pip install daytona-adk
```

## Use with agent

```python
from daytona_adk import DaytonaPlugin
from google.adk.agents import Agent

plugin = DaytonaPlugin(
  api_key="your-daytona-api-key" # Or set DAYTONA_API_KEY environment variable
)

root_agent = Agent(
    model="gemini-2.5-pro",
    name="sandbox_agent",
    instruction="Help users execute code and commands in a secure sandbox",
    tools=plugin.get_tools(),
)
```

## Available tools

| Tool                                 | Description                                    |
| ------------------------------------ | ---------------------------------------------- |
| `execute_code_in_daytona`            | Execute Python, JavaScript, or TypeScript code |
| `execute_command_in_daytona`         | Run shell commands                             |
| `upload_file_to_daytona`             | Upload scripts or data files to the sandbox    |
| `read_file_from_daytona`             | Read script outputs or generated files         |
| `start_long_running_command_daytona` | Start background processes (servers, watchers) |

## Learn more

For a detailed guide on building a code generator agent that writes, tests, and verifies code in secure sandboxes, check out [this guide](https://www.daytona.io/docs/en/google-adk-code-generator).

## Additional resources

- [Code Generator Agent Guide](https://www.daytona.io/docs/en/google-adk-code-generator)
- [Daytona ADK on PyPI](https://pypi.org/project/daytona-adk/)
- [Daytona ADK on GitHub](https://github.com/daytonaio/daytona-adk-plugin)
- [Daytona Documentation](https://www.daytona.io/docs)
