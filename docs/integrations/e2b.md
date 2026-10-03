---
catalog_title: E2B
catalog_description: Execute code and manage files in secure, stateful sandboxes
catalog_icon: /integrations/assets/e2b.png
catalog_tags: ["code"]
---

# E2B plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [e2b-adk](https://github.com/e2b-dev/e2b-adk-plugin) plugin connects an ADK
agent to [E2B](https://e2b.dev) sandboxes. It exposes tools for code execution,
shell commands, file operations, and long-running processes while managing the
sandbox lifecycle for the agent.

## Use cases

- **Secure code execution**: Run agent-generated code in an isolated,
  stateful sandbox instead of on the host machine.
- **Shell command automation**: Install packages, run builds, and inspect the
  sandbox filesystem with configurable timeouts and working directories.
- **File workflows**: Write scripts or datasets, run them, and read generated
  results back into the agent.
- **Background processes**: Start long-running commands such as development
  servers and optionally return a preview URL for an exposed port.

## Prerequisites

- Python 3.10 or later
- An [E2B account and API key](https://docs.e2b.dev/api-key)
- A [Gemini API key](https://aistudio.google.com/app/api-keys)

Set both API keys before running the example:

```bash
export E2B_API_KEY="your-e2b-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

## Installation

```bash
pip install e2b-adk
```

## Use with agent

```python
import asyncio

from e2b_adk import E2BPlugin
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner


async def main() -> None:
    plugin = E2BPlugin()
    root_agent = Agent(
        model="gemini-flash-latest",
        name="sandbox_agent",
        instruction="Use the sandbox to run and verify code before answering.",
        tools=plugin.get_tools(),
    )
    app = App(name="e2b_app", root_agent=root_agent, plugins=[plugin])

    async with InMemoryRunner(app=app) as runner:
        await runner.run_debug(
            "Write and run Python code that calculates the 20th Fibonacci number."
        )


if __name__ == "__main__":
    asyncio.run(main())
```

The plugin creates a sandbox lazily on the first E2B tool call and closes it
when the runner exits.

## Available tools

Tool | Description
---- | -----------
`run_code` | Execute code in a stateful kernel
`run_command` | Run a shell command in the sandbox
`write_file` | Write a file to the sandbox filesystem
`read_file` | Read a file from the sandbox filesystem
`list_files` | List files and directories at a path
`start_background_command` | Start a long-running process and optionally return a preview URL

## Configuration

The `E2BPlugin` constructor accepts optional settings such as `template`,
`envs`, `timeout`, and `lifecycle`. Other supported E2B sandbox creation options
are forwarded to the E2B SDK. See the
[configuration reference](https://github.com/e2b-dev/e2b-adk-plugin#configuration)
for the full option list.

## Additional resources

- [Build ADK agents with E2B](https://docs.e2b.dev/agents/google-adk)
- [E2B documentation](https://docs.e2b.dev/)
- [e2b-adk on PyPI](https://pypi.org/project/e2b-adk/)
- [e2b-adk on GitHub](https://github.com/e2b-dev/e2b-adk-plugin)
- [Data analysis agent example](https://github.com/e2b-dev/e2b-adk-plugin/blob/main/examples/data_analysis.py)
- [Code generator agent example](https://github.com/e2b-dev/e2b-adk-plugin/blob/main/examples/code_generator.py)
