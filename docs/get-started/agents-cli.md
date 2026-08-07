# Agents CLI Quickstart for ADK

[Agents CLI in Agent Platform](https://google.github.io/agents-cli/) is a CLI
and skills package that supports **the end-to-end lifecycle of your agents on
Google Cloud**: scaffolding, evaluation, deployment, and observability. Your
agents are built with the Agent Development Kit (ADK).

![The ten stages of the agent development lifecycle](/assets/agents-cli-lifecycle.png)

**Agents CLI is designed to be used through a coding agent.** It installs ADK
skills into Antigravity, Claude Code, Codex, and others, and your coding agent
uses them to make the right decisions at each step. This guide takes the coding
agent path. Every command also works standalone, so you can run them yourself
from a terminal instead: see the
[manual workflow tutorial](https://google.github.io/agents-cli/guide/hands-on-tutorial/).

Agents CLI is optional, and the agents it creates are ordinary ADK agents. To
learn ADK itself, start with one of the
[language quickstarts](index.md).

Agents CLI provides more than 25 commands spanning that lifecycle, and bundles
seven skills that teach your coding agent when to reach for each one:

| Skill | What your coding agent learns |
| --- | --- |
| `google-agents-cli-workflow` | Development lifecycle, code preservation, model selection |
| `google-agents-cli-adk-code` | ADK Python API: agents, tools, orchestration, callbacks |
| `google-agents-cli-scaffold` | Project scaffolding: `create`, `enhance`, `upgrade` |
| `google-agents-cli-eval` | Evaluation lifecycle: datasets, metrics, generate and grade, compare, analyze, optimize |
| `google-agents-cli-deploy` | Deployment: Agent Runtime, Cloud Run, GKE, CI/CD |
| `google-agents-cli-publish` | Gemini Enterprise registration |
| `google-agents-cli-observability` | Cloud Trace, logging, third-party integrations |

## Prerequisites

Required:

*   Python 3.11 or later
*   [`uv`](https://docs.astral.sh/uv/getting-started/installation/), which
    Agents CLI uses to manage environments and dependencies
*   [Node.js](https://nodejs.org/en/download), for installing the skills
*   A coding agent, such as [Antigravity](https://antigravity.google/),
    [Claude Code](https://docs.anthropic.com/en/docs/claude-code), or
    [Codex](https://github.com/openai/codex)

Optional, for deployment:

*   [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
*   [Terraform](https://developer.hashicorp.com/terraform/downloads)

Agents CLI currently supports Python agents.

## Installation

Install Agents CLI by running the following command. This is the only command
you run yourself; the rest of this guide goes through your coding agent.

```shell
uvx google-agents-cli setup
```

This command installs the `agents-cli` command, and the ADK skills into any
coding agents it finds on your machine.

??? tip "Alternative installation methods"

    **pipx:**

    ```shell
    pipx install google-agents-cli && agents-cli setup
    ```

    **pip:**

    ```shell
    pip install google-agents-cli && agents-cli setup
    ```

    **Skills only:**

    ```shell
    npx skills add google/agents-cli
    ```

## Authenticate

If you are already authenticated with the Google Cloud CLI, Agents CLI picks up
your Application Default Credentials and needs no further setup:

```shell
gcloud auth application-default login
```

??? tip "Using a Gemini API key instead"

    Create a key in Google AI Studio on the
    [API Keys](https://aistudio.google.com/app/apikey) page. After you scaffold
    a project in the next step, open its `.env` file, comment out the three
    Google Cloud lines, and add your key:

    ```env title="Update: .env"
    # GOOGLE_GENAI_USE_VERTEXAI=true
    # GOOGLE_CLOUD_PROJECT=your-project-id
    # GOOGLE_CLOUD_LOCATION=global

    GEMINI_API_KEY=YOUR_API_KEY
    ```

    Setting `GEMINI_API_KEY` as a shell variable is not enough on its own,
    because the generated `.env` file selects Google Cloud by default.

## Build your agent

Open your coding agent and confirm it can see the skills:

=== "Antigravity"

    Launch Antigravity from your IDE or terminal, then check that the Agents CLI
    skills are available in your environment.

=== "Claude Code"

    ```shell
    claude
    ```

    Run `/skills`. You should see `google-agents-cli-workflow` and the other
    Agents CLI skills listed.

=== "Codex"

    ```shell
    codex
    ```

    Check that the Agents CLI skills are available in your environment.

=== "Any other agent"

    Agents CLI works with any coding agent that supports
    [skills](https://agentskills.io/what-are-skills). Most agents list them
    through a `/skills` command or a settings panel.

Then tell it what you want to build:

> *"Use agents-cli to build an agent that turns long text into short
> bullet-point summaries"*

Your coding agent activates the `google-agents-cli-workflow` and
`google-agents-cli-scaffold` skills. It asks clarifying questions about the
tools your agent calls, the inputs and outputs you expect, and the success
criteria to evaluate against, then scaffolds the project:

```shell
agents-cli create my-agent --prototype --yes
cd my-agent && agents-cli install
```

It then uses the `google-agents-cli-adk-code` skill to write your agent into
`app/agent.py`. You now have a working project with agent code, tests, and an
eval dataset:

```none
my-agent/
    app/
        agent.py                # main agent code
        fast_api_app.py         # server, telemetry, and routes
        app_utils/              # session and artifact services
    tests/
        eval/                   # evaluation datasets and metrics
        integration/            # end-to-end agent tests
        unit/
    pyproject.toml              # project config and dependencies
    agents-cli-manifest.yaml    # Agents CLI configuration
    Dockerfile                  # container image for deployment
    GEMINI.md                   # project guidance for coding agents
    .env                        # API keys or project IDs
```

Use `adk create` when you want a single-file agent for learning ADK. Use this
project layout when you plan to test, evaluate, and deploy an agent.

## Run your agent

Ask your coding agent to start the local playground, or run it yourself:

```console
agents-cli playground
```

This command starts the ADK web interface with hot reload, so it picks up your
changes as you edit. You can access the playground at (http://localhost:8080).
Select the agent at the upper left corner and paste in a few paragraphs of
text. The agent replies with a short bullet-point summary.

## Next: Evaluate and deploy your agent

Now that you have Agents CLI installed and your first agent running, evaluate
and deploy it:

*   *"Write evals for this agent and run them"* to
    [evaluate your agent](https://google.github.io/agents-cli/guide/evaluation/)
    against the success criteria you set when you scoped it. Your coding agent
    grades the results, groups the failures by cause, and tunes the agent's
    instructions until it passes
*   *"Deploy this to Cloud Run"* to
    [deploy your agent](/deploy/agent-runtime/agents-cli/) to Agent Runtime,
    Cloud Run, or GKE
*   *"Set up observability infrastructure for my agent"* to add prompt-response
    logging and content logs

For the full walkthrough, including evaluation, deployment, and observability,
see
[Tutorial: Build your first agent](https://google.github.io/agents-cli/guide/quickstart-tutorial/).
