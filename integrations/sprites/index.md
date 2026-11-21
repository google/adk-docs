# Sprites plugin for ADK

Supported in ADKPython

The [Sprites ADK plugin](https://github.com/superfly/sprites-adk) connects your ADK agent to [Sprites](https://sprites.dev) — persistent, stateful Linux sandboxes from [Fly.io](https://fly.io). Unlike ephemeral sandboxes, a Sprite keeps its filesystem, installed packages, and running processes between sessions, and it can **checkpoint and restore** its entire state — so your agent can snapshot the environment before a risky change and roll back if it goes wrong.

## Use cases

- **Persistent development environments**: A named Sprite is reused across sessions — packages and files from earlier runs are still there, so long-running projects don't rebuild the environment from scratch each time.
- **Secure code execution**: Run agent-generated Python, JavaScript, or bash in an isolated microVM instead of on the host machine.
- **Safe experimentation**: Checkpoint the whole environment before package upgrades, migrations, or bulk edits, then restore it if the change breaks things.
- **File workflows**: Write scripts and data into the sandbox, run them, and read the results back.

## Prerequisites

- A [Sprites](https://sprites.dev) account
- A Sprites API token (set as the `SPRITES_TOKEN` environment variable)

## Installation

```bash
pip install sprites-adk
```

## Use with agent

```python
from sprites_adk import SpritesPlugin
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

# SpritesPlugin() gives each run a fresh sandbox; SpritesPlugin(sprite_name="my-project")
# reuses one persistent environment across sessions.
plugin = SpritesPlugin(
  # token="your-sprites-token"  # Or set the SPRITES_TOKEN environment variable
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="sandbox_agent",
    instruction="Run code and commands in the Sprite sandbox, not locally.",
    tools=plugin.get_tools(),
)

# Register the plugin on the runner so its lifecycle callbacks and cleanup run.
runner = InMemoryRunner(agent=root_agent, plugins=[plugin])
```

## Available tools

| Tool                        | Description                                                       |
| --------------------------- | ----------------------------------------------------------------- |
| `execute_command_in_sprite` | Run a shell command in the sandbox                                |
| `execute_code_in_sprite`    | Execute Python, JavaScript, or bash code                          |
| `write_file_to_sprite`      | Write a text file into the sandbox                                |
| `read_file_from_sprite`     | Read a text file from the sandbox                                 |
| `create_sprite_checkpoint`  | Snapshot the entire environment (filesystem, packages, processes) |
| `list_sprite_checkpoints`   | List available checkpoints                                        |
| `restore_sprite_checkpoint` | Roll back to a checkpoint (destructive; requires confirmation)    |

## Additional resources

- [sprites-adk on PyPI](https://pypi.org/project/sprites-adk/)
- [sprites-adk on GitHub](https://github.com/superfly/sprites-adk)
- [Sprites documentation](https://docs.sprites.dev)
