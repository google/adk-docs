---
catalog_title: boxd
catalog_description: Run agent code in persistent Linux microVMs with checkpoints and forks
catalog_icon: /integrations/assets/boxd.png
catalog_tags: ["code"]
---

# boxd plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [boxd ADK plugin](https://github.com/boxd-sh/boxd-adk) connects your ADK
agent to [boxd](https://boxd.sh/?ref=adk) machines. A boxd machine is a full
Ubuntu computer in a KVM microVM. It boots in about a second, keeps its disk,
installed packages and running processes until you delete it, and sleeps when
idle. The agent can **checkpoint** the whole machine, memory included, before a
risky change and roll back if it goes wrong.

## Use cases

- **Secure code execution**: Run agent-generated Python, JavaScript, or bash in
  an isolated microVM instead of on the host machine.

- **Persistent development environments**: A named machine is reused across
  sessions. Packages, files, and services from earlier runs are still there,
  and the machine wakes on the next command.

- **Safe experimentation**: Checkpoint the machine's disk, memory, and
  processes before upgrades, migrations, or bulk edits, then restore it if the
  change breaks things.

- **Parallel attempts**: Fork a running machine from your code and give each
  copy to a different agent to try several approaches from the same state.

## Prerequisites

- A [boxd](https://boxd.sh/?ref=adk) account
- A boxd API key (set as the `BOXD_API_KEY` environment variable)

## Installation

```bash
pip install boxd-adk
```

## Use with agent

```python
from boxd_adk import BoxdPlugin
from google.adk.agents import Agent
from google.adk.apps import App

# BoxdPlugin() gives each run a fresh machine that is deleted on close;
# BoxdPlugin(machine_name="my-project") reuses one persistent machine.
plugin = BoxdPlugin(
    # api_key="your-boxd-api-key"  # Or set the BOXD_API_KEY environment variable
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="boxd_agent",
    instruction="Run code and commands in the boxd machine, not locally.",
    tools=plugin.get_tools(),
)

# Register the plugin on the app so its lifecycle callbacks and cleanup run.
app = App(name="boxd_app", root_agent=root_agent, plugins=[plugin])
```

## Available tools

Tool | Description
---- | -----------
`execute_command_in_boxd` | Run a shell command in the machine
`execute_code_in_boxd` | Execute Python, JavaScript, or bash code
`write_file_to_boxd` | Write a text file into the machine
`read_file_from_boxd` | Read a text file from the machine
`create_boxd_checkpoint` | Checkpoint the entire machine (disk, memory, processes)
`list_boxd_checkpoints` | List available checkpoints
`restore_boxd_checkpoint` | Roll back to a checkpoint (destructive; requires confirmation)

## Configuration

The plugin reads `BOXD_API_KEY` and, optionally, `BOXD_REGION`. Options for
new machines include `vcpu`, `from_snapshot`, `labels`, and `delete_after`
(seconds until boxd deletes the machine, even if your process never closes the
plugin). The plugin also has two methods that create new machines:
`plugin.fork()` returns a plugin bound to a live copy of the machine, and
`plugin.save_snapshot(name)` saves a snapshot that `BoxdPlugin(from_snapshot=name)`
starts from.

## Additional resources

- [boxd-adk on PyPI](https://pypi.org/project/boxd-adk/)
- [boxd-adk on GitHub](https://github.com/boxd-sh/boxd-adk)
- [boxd documentation](https://docs.boxd.sh/?ref=adk)
