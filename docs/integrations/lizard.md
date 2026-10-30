---
catalog_title: Lizard Sandboxes
catalog_description: Run Python and shell commands in isolated cloud sandboxes
catalog_icon: /integrations/assets/lizard.svg
catalog_tags: ["code"]
---

# Lizard Sandboxes plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Lizard (lizard.build)](https://lizard.build/sandboxes) provides cloud sandboxes for agent code. The plugin gives each ADK invocation its own sandbox and deletes it when the invocation ends.

## Use cases

- **Run Python**: Keep variables between tool calls within one invocation.
- **Run commands**: Execute shell commands and inspect their output and exit code.
- **Work with files**: Read and write UTF-8 files in the sandbox.

## Prerequisites

- Python 3.11 or later and ADK 2.12 or later.
- A [Lizard account](https://lizard.build/), project ID, and API key. See the [sandbox quickstart](https://lizard.build/docs/sandboxes/quickstart/).
- A Gemini API key for the example below.

Set `LIZARD_API_KEY`, `LIZARD_PROJECT_ID`, and `GOOGLE_API_KEY` in your host environment. Keep keys out of source code and agent prompts.

## Installation

```bash
pip install lizard-adk
```

## Use with agent

Register the tools on the agent and the plugin on the ADK App. Close the runner in a `finally` block so failed or cancelled invocations also release their resources.

```python
import asyncio

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types

from lizard_adk import LizardPlugin


async def main() -> None:
    plugin = LizardPlugin()
    root_agent = Agent(
        model="gemini-flash-latest",
        name="sandbox_agent",
        instruction="Use the sandbox tools to run Python and check your answer.",
        tools=plugin.get_tools(),
    )
    runner = InMemoryRunner(
        app=App(name="sandbox_example", root_agent=root_agent, plugins=[plugin]),
        plugin_close_timeout=120,
    )
    try:
        session = await runner.session_service.create_session(
            app_name="sandbox_example", user_id="example"
        )
        async for event in runner.run_async(
            user_id="example",
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text="Use Python to sum the integers from 1 to 100.")],
            ),
        ):
            if event.content:
                for part in event.content.parts or []:
                    if part.text:
                        print(part.text)
    finally:
        await runner.close()


if __name__ == "__main__":
    asyncio.run(main())

```

## Available tools

Tool | Description
---- | -----------
`lizard_execute_command` | Run a shell command and return stdout, stderr, and exit code.
`lizard_execute_code` | Run Python in a persistent kernel and return output or a structured error.
`lizard_read_file` | Read a UTF-8 file of up to 1 MiB.
`lizard_write_file` | Write a UTF-8 file of up to 1 MiB.

## Configuration

The `LizardPlugin` constructor accepts `project_id`, `api_key`, `api_url`, `size`, `lifetime_ms`, and `command_timeout_ms`. Defaults are the small interpreter template, a 15-minute lifetime, and a 60-second command timeout. The command timeout cannot exceed 120 seconds.

Python variables and files persist within one invocation. A later user message gets a fresh sandbox. The plugin does not build custom Docker images. Cloud usage follows Lizard's published pricing.

## Additional resources

- [Lizard Sandboxes documentation](https://lizard.build/docs/sandboxes/)
- [Package on PyPI](https://pypi.org/project/lizard-adk/)
- [Source, tests, and examples](https://github.com/lizard-build/integrations/tree/main/packages/lizard-adk)
