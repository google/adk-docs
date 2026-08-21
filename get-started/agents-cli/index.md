# Agents CLI Quickstart for ADK

This guide shows you how to get up and running with Agent Development Kit (ADK) using Agents CLI. You can use the Agents CLI tool set with coding agents like Antigravity, Claude Code, and Codex to build, evaluate, and deploy ADK agents. For more information, see the [Agents CLI](https://google.github.io/agents-cli/) documentation. Before you start, make sure you have the following installed:

- Python 3.11 or later: Agents CLI supports ADK agents in Python
- The [`uv`](https://docs.astral.sh/uv/getting-started/installation/) tool to manage environments and dependencies
- [Node.js](https://nodejs.org/en/download), for installing the skills
- Coding agent such as [Antigravity](https://antigravity.google/), [Claude Code](https://docs.anthropic.com/en/docs/claude-code), or [Codex](https://github.com/openai/codex)

If you want to deploy ADK agents to services like Google Cloud, make sure the following tools are also installed:

- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
- [Terraform](https://developer.hashicorp.com/terraform/downloads)

## Installation

Install Agents CLI by running the following command. This step installs the `agents-cli` command, the ADK Python packages, and the ADK skills into any coding agents already on your machine:

```shell
uvx google-agents-cli setup
```

Alternative installation methods

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

The installation command is the only one you have to run yourself. Once installed, you can use your coding agent to build and run an ADK agent.

## Authenticate

Agents CLI needs credentials for a generative AI API to run your agents. The simplest option is a Gemini API key from Google AI Studio. Create a key on the [API Keys](https://aistudio.google.com/app/apikey) page, then after you scaffold a project in the next step, open its `.env` file and set:

Update: .env

```text
GEMINI_API_KEY=YOUR_API_KEY
```

Comment out the three `GOOGLE_CLOUD_*` lines in the same file so the SDK uses your key instead of Vertex AI.

Using Google Cloud Agent Platform instead

If you already have a Google Cloud project, Agents CLI picks up your Application Default Credentials:

```shell
gcloud auth application-default login
```

Make sure the `GOOGLE_CLOUD_*` lines in the generated `.env` file are uncommented and set them to your project identifiers. For more information on connecting to Google Cloud services and projects with ADK, see the [Google Cloud setup guide](/get-started/google-cloud/) for ADK.

## Build your agent

Open your coding agent and confirm it can see the skills:

```shell
antigravity            # launch from your IDE or terminal
# then verify the Agents CLI skills are listed in your environment
```

```shell
claude
/skills                # expect google-agents-cli-* entries in the list
```

```shell
codex
/skills                # expect google-agents-cli-* entries in the list
```

Using other coding agents

Agents CLI works with any coding agent that supports [skills](https://agentskills.io/what-are-skills). Most agents list them through a `/skills` command or a settings panel.

Then tell the coding agent what you want to build:

Coding agent prompt

```shell
Use agents-cli to build an agent that turns long text into short
bullet-point summaries
```

Your coding agent activates the `google-agents-cli-workflow` and `google-agents-cli-scaffold` skills, asks clarifying questions about the tools your agent calls, the inputs and outputs you expect, and the success criteria to evaluate against, and then scaffolds the project.

Next, your coding agent uses the `google-agents-cli-adk-code` skill to write your agent into `app/agent.py`. You end up with a working project with the agent code, tests, and an eval dataset in the following file structure:

```text
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

Use this project structure when you plan to test, evaluate, and deploy an agent. If you want a create single-file agent for learning ADK, use the `adk create` command instead.

## Run your agent

Ask your coding agent to start the local playground, or run it yourself:

```console
agents-cli playground
```

This command starts the ADK web interface with hot reload, so your changes are reflected in the project as you edit. You can access the playground at (http://localhost:8080). Select the agent at the upper left corner and paste in a few paragraphs of text. The agent replies with a short bullet-point summary.

## Next: Evaluate and deploy your agent

Now that you have Agents CLI installed and your first agent running, you can evaluate and deploy it with your coding agent using instructions like the following:

- ***"Write evals for this agent and run them"*** to [evaluate your agent](https://google.github.io/agents-cli/guide/evaluation/) against the success criteria you set when you scoped it. Your coding agent grades the results, groups the failures by cause, and tunes the agent's instructions until it passes
- ***"Deploy this to Cloud Run"*** to [deploy your agent](/deploy/agent-runtime/agents-cli/) to Agent Runtime, Cloud Run, or GKE.
- ***"Set up observability infrastructure for my agent"*** to add prompt-response logging and content logs.

For the full walkthrough, including evaluation, deployment, and observability, see the Agents CLI [Tutorial: Build your first agent](https://google.github.io/agents-cli/guide/quickstart-tutorial/).
