---
catalog_title: apowerb
catalog_description: Run, govern, and schedule agents from a web UI and REST API
catalog_icon: /integrations/assets/apowerb.png
catalog_tags: ["mcp", "connectors", "data"]
---

# apowerb platform for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[apowerb](https://github.com/apowerb/apowerb) is an open source platform
(Apache-2.0) that builds and runs ADK agents from definitions stored in a
database. You define an agent in a web interface or through a REST API, and
apowerb turns that definition into an ADK `LlmAgent`, or into a
`SequentialAgent`, `ParallelAgent`, or `LoopAgent` for multi-agent workflows.
It connects agents to MCP servers as a client, adds its own tools such as
Text-to-SQL and RAG, and provides sessions, traces, schedules, and per-user
token quotas around the ADK runtime.

This page shows how to start apowerb, create an ADK agent with an MCP server
attached, and run it. apowerb is a platform you deploy and operate, not a
library of tools to import into an existing ADK project.

## Use cases

- **Operate agents without writing agent code**: Define the model, instruction,
  tools, and sub-agents in a web interface or with a REST call, and let the
  server build the ADK agent.
- **Connect MCP servers**: Attach remote MCP servers to an agent, or register
  them once and reuse them across agents.
- **Query business data**: Give agents Text-to-SQL, RAG over files, URLs, and
  databases, and connectors for Google Workspace, Microsoft 365, and CRM or ERP
  systems.
- **Run agents unattended**: Start runs on a schedule or from an incoming
  e-mail, and review the session trace afterwards.
- **Control usage**: Apply per-user token quotas, user permissions, and
  encrypted secrets on a self-hosted deployment.

## Prerequisites

- Docker with Docker Compose, to run the stack described in the apowerb
  [quickstart](https://docs.apowerb.com/quickstart)
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- A user account on the apowerb instance (the examples use its e-mail address
  and password)
- Python with the `requests` package, for the example scripts below
- Optional: the URL of a remote MCP server that supports streamable HTTP

## Installation

The quickstart uses the `apowerb-hosting` repository, which runs Postgres, the
API, and the web interface with Docker Compose:

```bash
git clone https://github.com/apowerb/apowerb-hosting.git
cd apowerb-hosting
cp .env.example .env
./scripts/generate-secrets.sh
docker compose -f docker-compose/docker-compose.yml --env-file .env up -d
```

Name the compose file as shown. The `docker-compose.yml` at the root of that
repository targets a different platform and does not start Postgres. Ports 3000
(interface) and 8000 (API) must be free.

The package is also published on PyPI for source or custom deployments. See the
[installation guide](https://docs.apowerb.com/installation) for the supported
Python version and the `apowerb serve` command:

```bash
pip install apowerb
```

## Use with agent

### 1. Check the API

```bash
curl -s http://localhost:8000/health
```

The interface is at `http://localhost:3000` and the interactive API reference is
at `http://localhost:8000/docs`.

### 2. Sign in

Request an access token with your user's e-mail address and password. The
token endpoint takes a form body:

```python title="auth.py"
import requests

BASE_URL = "http://localhost:8000"
EMAIL = "you@example.com"
PASSWORD = "YOUR_PASSWORD"

response = requests.post(
    f"{BASE_URL}/api/auth/token",
    data={"username": EMAIL, "password": PASSWORD},
)
response.raise_for_status()
TOKEN = response.json()["access_token"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
```

### 3. Create an agent with an MCP server

Create the agent with `POST /api/agents`. The `agent_model` field is a LiteLLM
model string, so Gemini models take the `gemini/` prefix. The Gemini API key goes
in `agent_model_params`. The `mcp_servers` field attaches MCP servers directly
to the agent:

```python title="create_agent.py"
agent = requests.post(
    f"{BASE_URL}/api/agents",
    headers=HEADERS,
    json={
        "agent_name": "docs_assistant",
        "agent_description": "Answers questions with the tools of an MCP server",
        "agent_instruction": "You are a helpful assistant. Use the MCP tools when they fit the request.",
        "agent_model": "gemini/gemini-flash-latest",
        "agent_model_params": {"model_api_key": "YOUR_GEMINI_API_KEY"},
        "agent_type": "llm",
        "agent_tools": [],
        "mcp_servers": [
            {
                "name": "my_mcp_server",
                "transport": "http",
                "url": "https://mcp.example.com/mcp",
                "headers": {"Authorization": "Bearer YOUR_MCP_TOKEN"},
            }
        ],
    },
)
agent.raise_for_status()
print(agent.json())
```

To reuse a server across agents, save it with `POST /api/mcp_configs` and call
`POST /api/mcp_configs/reload` so the toolsets are rebuilt. The `http`
transport is the default. The `stdio` transport launches a local command, so it
is disabled unless the deployment sets `MCP_STDIO_ENABLED=1`, and it is
restricted to administrators.

### 4. Run the agent

Send a message with `POST /api/adk/run`. The `user_id` must be the e-mail address
of the signed-in user, and `agent_name` is the name given at creation. The
server creates the session if it does not exist:

```python title="run_agent.py"
result = requests.post(
    f"{BASE_URL}/api/adk/run",
    headers=HEADERS,
    json={
        "agent_name": "docs_assistant",
        "user_id": EMAIL,
        "session_id": "session_001",
        "new_message": {
            "role": "user",
            "parts": [{"text": "Which tools do you have access to?"}],
        },
    },
)
result.raise_for_status()
print(result.json())
```

Post the same body to `/api/adk/run_sse` for a streamed response. The
conversation history and the execution trace are available at
`/api/adk/sessions/{agent}/{user}/{session}` and
`/api/adk/sessions/{agent}/{user}/{session}/trace`.

## How it works

apowerb stores each agent as a database record. When the server starts, and
whenever an agent changes, it generates an ADK agent module for each stored
agent under `agents_pool/` and mounts the ADK FastAPI application into its own
FastAPI app. Runs go through the ADK runner with the agent's folder name as the
application name, together with the user ID, session ID, and new message.

A function named `to_agent()` builds the ADK object for a stored agent:

- **Agent type**: `llm` and `router` agents become an `LlmAgent`. `sequential`,
  `parallel`, and `loop` agents become a `SequentialAgent`, `ParallelAgent`, or
  `LoopAgent` whose `sub_agents` are built recursively.
- **Model**: The `agent_model` string is wrapped in the ADK `LiteLlm` model, so
  any LiteLLM provider can be used, including Gemini with the `gemini/` prefix.
- **Tools**: Tool configurations stored for the agent are loaded as function
  tools. Each HTTP, SSE, or `stdio` entry in `mcp_servers` becomes an ADK `McpToolset`.
- **Callbacks**: Optional guardrail settings are attached as ADK model and tool
  callbacks.
- **Memory**: When `memory_enabled` is true, the ADK `load_memory` tool is added.

## Capabilities

Capability | Description
---------- | -----------
Agent types | `llm`, `router`, `sequential`, `parallel`, and `loop` agents with sub-agents
MCP client | Streamable HTTP and SSE servers; `stdio` servers when enabled by the operator
Tool portfolio | Built-in tool modules for Google Workspace, Microsoft 365, databases, RAG, Text-to-SQL, BI charts, and web search; list them with `GET /api/tools`
Sessions and traces | Create, list, inspect, and delete ADK sessions, and read the execution trace of a session
Scheduled runs | Schedule recurring runs with `POST /api/adk/schedule_run` or start one immediately with `POST /api/adk/run_now`
Model providers | Any LiteLLM provider, such as Gemini, Anthropic, OpenAI, and Mistral
Command line | The `apowerb` CLI starts the server and lists agents, tools, and runs

## Additional resources

- [apowerb documentation](https://docs.apowerb.com)
- [Quickstart](https://docs.apowerb.com/quickstart)
- [MCP guide](https://docs.apowerb.com/guides/mcp)
- [Architecture](https://docs.apowerb.com/concepts/architecture)
- [API reference](https://docs.apowerb.com/api-reference/introduction)
- [apowerb on GitHub](https://github.com/apowerb/apowerb)
- [apowerb-hosting on GitHub](https://github.com/apowerb/apowerb-hosting)
- [apowerb on PyPI](https://pypi.org/project/apowerb/)
