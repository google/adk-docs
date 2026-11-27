---
catalog_title: ACE Music by Ace Data Cloud
catalog_description: Generate music and retrieve audio from existing tasks
catalog_icon: /integrations/assets/ace-music.png
catalog_tags: ["mcp"]
---

# ACE Music tools for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [ACE Music MCP server](https://github.com/AceDataCloud/AceMusicMCP) connects
an ADK agent to Ace Data Cloud. For example, an editor can generate a soundtrack,
save its task ID and use the same ID to retrieve the finished tracks later.

## Connect a Python agent

Install the [ADK CLI](../get-started/python.md), its MCP extra
(`pip install "google-adk[mcp]"`), and [uv](https://docs.astral.sh/uv/).
Create an [Ace Data Cloud application](https://platform.acedata.cloud/console/applications)
with ACE Music access and set `ACEDATACLOUD_API_TOKEN` in your local environment.
Keep that key out of prompts and source control.

Create `music_agent/agent.py`:

```python
import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

music = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uvx",
            args=["--from", "mcp-acemusic==2026.11.25.0", "mcp-acemusic"],
            env={"ACEDATACLOUD_API_TOKEN": os.environ["ACEDATACLOUD_API_TOKEN"]},
        ),
        timeout=30,
    ),
    tool_filter=["acemusic_list_models", "acemusic_get_task"],
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="music_agent",
    instruction="List available music models or look up a task ID supplied by the user.",
    tools=[music],
)
```

With the [authentication for your ADK model](../get-started/python.md) configured,
run `adk run music_agent` from the directory containing `music_agent`. Ask
“Which ACE Music models are available?” to exercise the local model-list tool.

## Tools and billing

| Tool | Purpose |
| --- | --- |
| `acemusic_list_models` | Read model IDs and the default from the installed package. |
| `acemusic_get_task` | Retrieve an existing task owned by the application, using its original ID. |
| `acemusic_generate_music` | Submit a paid music-generation task from a prompt. |
| `acemusic_generate_custom_music` | Submit a paid generation using lyrics, a style and a title. |

The example exposes just the first two tools. To enable music creation, add
the desired generation tool to `tool_filter` and update the agent's instructions
to obtain the user's approval before submission. Generation spends Ace Data
Cloud credits. Retain the returned task ID and poll it for results; submitting the
prompt again can create a second billable task. ADK model usage is billed separately.

See the [server documentation and full tool list](https://github.com/AceDataCloud/AceMusicMCP)
and the [published Python package](https://pypi.org/project/mcp-acemusic/).
