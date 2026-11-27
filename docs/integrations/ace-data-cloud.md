---
catalog_title: Ace Data Cloud
catalog_description: Search the web and work with music, images, video, and 3D assets
catalog_icon: /integrations/assets/ace-data-cloud.png
catalog_tags: ["mcp"]
---

# Ace Data Cloud MCP tools for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Ace Data Cloud](https://github.com/AceDataCloud/MCPs) publishes separate MCP
servers for its search, chat, and media APIs. Choose a server for each service
your agent uses. For example, a video editor can use Suno to check a soundtrack
and Seedance to check a video clip without giving the agent tools to create
new jobs.

## Prerequisites

Install [ADK for Python](../get-started/python.md), its MCP extra
(`pip install "google-adk[mcp]"`), and [uv](https://docs.astral.sh/uv/).
In [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen),
create application keys with access to the services you intend to use.
For the example, set `SUNO_ACE_TOKEN` and `SEEDANCE_ACE_TOKEN` to keys with
the corresponding task lookup permission.

## Use with an agent

Save the following as `media_assistant/agent.py`. Each toolset starts its own
stdio server and receives the credential for that service.

```python
import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters


def service_tools(package, version, token_env, tools):
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="uvx",
                args=["--from", f"{package}=={version}", package],
                env={"ACEDATACLOUD_API_TOKEN": os.environ[token_env]},
            ),
            timeout=60,
        ),
        tool_filter=tools,
    )


root_agent = Agent(
    model="gemini-flash-latest",
    name="media_assistant",
    instruction=(
        "List music or video models, or check an existing task. "
        "Ask which service created the task and use that service's lookup."
    ),
    tools=[
        service_tools(
            "mcp-suno", "2026.11.25.0", "SUNO_ACE_TOKEN",
            ["suno_list_models", "suno_get_task"],
        ),
        service_tools(
            "mcp-seedance", "2026.11.24.0", "SEEDANCE_ACE_TOKEN",
            ["seedance_list_models", "seedance_get_task"],
        ),
    ],
)
```

Configure [authentication for the ADK model](../get-started/python.md), then run
`adk run media_assistant` from the directory containing `media_assistant`.
Try “Which Suno models are available?” to read model names from the installed
server. To check a previous job, provide the service and its task ID. A pending
task may have no output yet.

## Choose a service

| Task | Service packages |
| --- | --- |
| Search and recognition | [Google Search](https://pypi.org/project/mcp-serp/), [Image to Text](https://pypi.org/project/mcp-image2text/) |
| Text and multimodal chat | [AI Chat](https://pypi.org/project/mcp-aichat/), [Grok](https://pypi.org/project/mcp-grok/), [GLM](https://pypi.org/project/mcp-glm/) |
| Music and speech | [Suno](https://pypi.org/project/mcp-suno/), [ACE Music](https://pypi.org/project/mcp-acemusic/), [Fish Audio](https://pypi.org/project/mcp-fish/), [Producer](https://pypi.org/project/mcp-producer/) |
| Image creation and editing | [Nano Banana](https://pypi.org/project/mcp-nanobanana-pro/), [GPT Image](https://pypi.org/project/mcp-openai-pro/), [Seedream](https://pypi.org/project/mcp-seedream-pro/), [FLUX](https://pypi.org/project/mcp-flux-pro/), [Qwen Image](https://pypi.org/project/mcp-qwen-image/) |
| Video | [Seedance](https://pypi.org/project/mcp-seedance/), [Kling](https://pypi.org/project/mcp-kling/), [Veo](https://pypi.org/project/mcp-veo/), [HappyHorse](https://pypi.org/project/mcp-happyhorse/), [Wan](https://pypi.org/project/mcp-wan/), [MiniMax](https://pypi.org/project/mcp-minimax/), [Hailuo](https://pypi.org/project/mcp-hailuo/), [Luma](https://pypi.org/project/mcp-luma/) |
| 3D models | [Tripo](https://pypi.org/project/mcp-tripo/) |

The example exposes two tools per server. To enable music creation, for example,
add `suno_generate_music` to the Suno filter only after configuring a key with
generation access. Generation and search can spend Ace Data Cloud credits.
Ask the user before starting a paid operation, save the returned task ID, and
poll that ID for results. ADK model usage is billed separately.

For GPT Image, the linked distribution is `mcp-openai-pro`. Launch it with
`--profile gpt-image` after the executable name to select its five image and
task tools. See the [GPT Image profile](https://github.com/AceDataCloud/OpenAIMCP/blob/main/GPT_IMAGE.md)
and the [per-service tool and setup guides](https://github.com/AceDataCloud/MCPs#readme).
