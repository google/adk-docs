# Agents CLI Quickstart for ADK

[Agents CLI](https://google.github.io/agents-cli/) sets up and installs ADK,
scaffolds a project you can evaluate and deploy, and teaches your coding agent
how to use ADK through a bundled set of skills. It works with Antigravity,
Claude Code, Codex, and any other skill-aware coding agent. Use it when you
want to go from empty directory to a deployable ADK agent quickly.

![The ten stages of the agent development lifecycle](/assets/agents-cli-lifecycle.png)

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

Install Agents CLI by running the following command. This installs the
`agents-cli` command, the ADK Python packages your project will need, and the
ADK skills into any coding agents already on your machine. This is the only
command you run yourself; the rest of this guide goes through your coding
agent.

```shell
uvx google-agents-cli setup
```

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

Agents CLI needs credentials for a generative AI API to run your agents. The
simplest option is a Gemini API key from Google AI Studio. Create a key on the
[API Keys](https://aistudio.google.com/app/apikey) page, then after you
scaffold a project in the next step, open its `.env` file and set:

```env title="Update: .env"
GEMINI_API_KEY=YOUR_API_KEY
```

Comment out the three `GOOGLE_CLOUD_*` lines in the same file so the SDK uses
your key instead of Vertex AI.

??? note "Using Google Cloud (Vertex AI) instead"

    If you already have a Google Cloud project, Agents CLI picks up your
    Application Default Credentials:

    ```shell
    gcloud auth application-default login
    ```

    Leave the `GOOGLE_CLOUD_*` lines in the generated `.env` file uncommented
    and set them to your project. For the full setup — including quotas,
    regions, and enterprise auth — see the
    [Google Cloud setup guide](google-cloud.md).

## Build your agent

Open your coding agent and confirm it can see the skills:

=== "Antigravity"

    ```shell
    antigravity            # launch from your IDE or terminal
    # then verify the Agents CLI skills are listed in your environment
    ```

=== "Claude Code"

    ```shell
    claude
    /skills                # expect google-agents-cli-* entries in the list
    ```

=== "Codex"

    ```shell
    codex
    /skills                # expect google-agents-cli-* entries in the list
    ```

??? note "Using other coding agents"

    Agents CLI works with any coding agent that supports
    [skills](https://agentskills.io/what-are-skills). Most agents list them
    through a `/skills` command or a settings panel.

Then tell the coding agent what you want to build:

> *"Use agents-cli to build an agent that turns long text into short
> bullet-point summaries"*

Your coding agent activates the `google-agents-cli-workflow` and
`google-agents-cli-scaffold` skills, asks clarifying questions about the
tools your agent calls, the inputs and outputs you expect, and the success
criteria to evaluate against, and then scaffolds the project. It runs the
commands below on your behalf — you can also run them directly in a terminal
if you prefer:

```shell
agents-cli create my-agent --prototype --yes
cd my-agent && agents-cli install
```

Next, your coding agent uses the `google-agents-cli-adk-code` skill to write
your agent into `app/agent.py`. You end up with a working project — agent
code, tests, and an eval dataset — laid out like this:

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
