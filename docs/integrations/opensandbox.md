---
catalog_title: OpenSandbox
catalog_description: Run commands and edit files in a persistent remote sandbox workspace
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["code"]
---

# OpenSandbox environment for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.13.0</span><span class="lst-preview">Experimental</span>
</div>

The ***OpenSandboxEnvironment*** class connects an Agent Development Kit (ADK)
agent to an [OpenSandbox](https://open-sandbox.ai) sandbox, so the agent can run
shell commands and read and write files in an isolated remote workspace instead
of on your machine. The workspace persists across agent requests, so files the
agent writes and packages it installs stay available until the environment
closes the sandbox.
OpenSandbox is a sandbox runtime you host yourself, either locally on Docker or
as a remote deployment, such as a Kubernetes cluster.

You use ***OpenSandboxEnvironment*** with the
[Environment Toolset](/integrations/environment-toolset/), which provides the
agent tools for file operations and command execution.

!!! example "Experimental"
    The OpenSandbox environment feature is an experimental release.
    It may have limitations and is not recommended for production use.
    To share feedback,
    [open an issue](https://github.com/google/adk-python/issues/new?template=feature_request.md).

## Use cases

-   **Run generated code remotely:** Write a script, run it, and report the
    actual output, without running AI-generated code on your local machine.
-   **Work with data files:** Create data files, then process them with
    scripts in the sandbox.
-   **Control the runtime:** Choose the container image, environment variables,
    and network policy for the workspace.

## Prerequisites

-   An OpenSandbox server. To run a server locally on Docker, see the
    [OpenSandbox getting started guide](https://github.com/opensandbox-group/OpenSandbox#getting-started).
    A local server listens on `localhost:8080` by default.
-   For a remote OpenSandbox deployment, the server domain and an API key.

## Installation

Install ADK with the `opensandbox` extra:

```bash
pip install "google-adk[opensandbox]"
```

If you use a remote OpenSandbox deployment, set its domain and API key as
environment variables. You don't need these settings for a local server on
`localhost:8080`.

```bash
export OPEN_SANDBOX_DOMAIN="https://sandbox.example.com"
export OPEN_SANDBOX_API_KEY="your-api-key"
```

## Use with agent

Add an ***EnvironmentToolset*** with an ***OpenSandboxEnvironment*** instance to
your agent's tools. By default, the environment creates a sandbox from the
`python:3.11` image the first time the agent uses the toolset, and destroys
the sandbox when the toolset closes.

```python
from google.adk.agents import Agent
from google.adk.integrations.opensandbox import OpenSandboxEnvironment
from google.adk.tools.environment import EnvironmentToolset

root_agent = Agent(
    model="gemini-flash-latest",
    name="opensandbox_coding_agent",
    instruction="""
    You are a coding assistant. Work only through the environment tools,
    which run inside an isolated OpenSandbox workspace. Write the smallest
    script needed to solve the request, run it, and use its actual output
    in your answer. If a command fails, read stderr, fix the problem, and
    retry.
    """,
    tools=[
        EnvironmentToolset(
            environment=OpenSandboxEnvironment(
                image="python:3.11",
                timeout=300,
            ),
        ),
    ],
)
```

For a full implementation, see the
[OpenSandbox environment sample](https://github.com/google/adk-python/tree/main/contributing/samples/environment_and_skills/opensandbox_environment).

### Try with agent

Try the following prompt in an interactive session with the agent:

```none
Write a Python script that prints the first 20 Fibonacci numbers,
run it, and report the output.
```

The agent writes the script to the sandbox workspace, runs it with the
***Execute*** tool, and reports the output returned from the sandbox.

## Available tools

The ***EnvironmentToolset*** gives the agent the following tools, which operate
on the sandbox workspace:

Tool | Description
---- | -----------
`Execute` | Run shell commands in the sandbox
`ReadFile` | Read a file from the sandbox
`WriteFile` | Create or overwrite a file in the sandbox
`EditFile` | Edit an existing file in the sandbox

## Manage the sandbox lifecycle

How you configure the sandbox lifetime and ownership determines whether the
agent's workspace state survives between commands and after the agent stops.

### Sandbox lifetime

The `timeout` parameter sets the lifetime of a sandbox the environment creates,
in seconds. The default is 300 seconds, and the minimum is 60 seconds. Before
each command the agent runs, the environment renews the sandbox lifetime, so a
sandbox in active use does not expire. File reads and writes don't renew the
lifetime.

If the sandbox expires after a period without commands, the next command
creates a new sandbox. The new sandbox does not contain the files or installed
packages from the expired one. Set `timeout` longer than the idle periods you
expect, for example while a user reads results between requests, if the agent
needs to keep its workspace state.

### Attach to an existing sandbox

To reuse a sandbox you created and manage outside ADK, pass its ID with the
`sandbox_id` parameter. The environment connects to that sandbox instead of
creating one. When the toolset closes, the environment releases its connection
and leaves the sandbox running.

```python
environment = OpenSandboxEnvironment(sandbox_id="existing-sandbox-id")
```

When you attach to an existing sandbox, the environment does not renew its
lifetime or recreate it after it expires. You can't combine `sandbox_id` with
the `image`, `snapshot_id`, `network_policy`, or `secure_access` parameters,
because those settings only apply when the environment creates a sandbox.

### File paths

The agent's working directory in the sandbox is `/workspace`. Relative file
paths resolve under `/workspace`, and commands run from that directory. When
the agent writes a file, the environment creates any missing parent
directories.

## Configuration

The ***OpenSandboxEnvironment*** class supports the following parameters:

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `image` | `str` or `SandboxImageSpec` | `"python:3.11"` | Container image for a new sandbox. Can't be used with `snapshot_id`. |
| `snapshot_id` | `str` | `None` | Snapshot to create a new sandbox from, instead of an image. |
| `sandbox_id` | `str` | `None` | ID of an existing sandbox to attach to, instead of creating one. |
| `timeout` | `int` | `300` | Lifetime in seconds of a sandbox the environment creates. Must be at least 60. |
| `ready_timeout` | `float` | `30` | Maximum seconds to wait for a sandbox to be ready when creating or connecting to it. |
| `env_vars` | `dict[str, str]` | `None` | Environment variables applied to new sandboxes and to each command. |
| `metadata` | `dict[str, str]` | `None` | Additional metadata for a new sandbox. |
| `connection_config` | `ConnectionConfig` | `None` | OpenSandbox SDK connection configuration. When omitted, the environment reads `OPEN_SANDBOX_DOMAIN` and `OPEN_SANDBOX_API_KEY`, and uses HTTP for a local or unset domain and HTTPS for a remote domain, unless the domain includes a scheme. |
| `network_policy` | `NetworkPolicy` | `None` | Network policy for a new sandbox. |
| `secure_access` | `bool` | `False` | Whether to enable secure access mode for a new sandbox. |

The following example creates a sandbox with custom environment variables and
a longer lifetime:

```python
environment = OpenSandboxEnvironment(
    image="python:3.11",
    timeout=900,
    env_vars={"LOG_LEVEL": "DEBUG"},
)
```

## Limitations

-   When a sandbox the environment created expires, the replacement sandbox
    starts empty. Files and installed packages from the expired sandbox are
    lost.
-   The ***Execute*** tool stops commands that run longer than 30 seconds.
    Long-running commands, such as large package installs, can time out.
-   The working directory is fixed at `/workspace`.

## Additional resources

-   [Environment Toolsets](/integrations/environment-toolset/): Learn about the
    tools available to agents in an environment and how to build custom
    environments.
-   [OpenSandbox documentation](https://open-sandbox.ai): Set up and deploy an
    OpenSandbox server.
