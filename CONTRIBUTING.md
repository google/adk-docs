# How to contribute

Thank you for your interest in contributing! We appreciate your willingness to
share your patches and improvements with the project.

## Before You Start

### Find Something to Work On

Check the [GitHub Issues](https://github.com/google/adk-docs/issues) for bug
reports or feature requests. Feel free to pick up an existing issue or open a
new one if you have an idea or find a bug.

### Sign the CLA

Contributions to this project must be accompanied by a
[Contributor License Agreement](https://cla.developers.google.com/about) (CLA).
You (or your employer) retain the copyright to your contribution; this simply
gives us permission to use and redistribute your contributions as part of the
project.

If you or your current employer have already signed the Google CLA (even if it
was for a different project), you probably don't need to do it again.

Visit <https://cla.developers.google.com/> to see your current agreements or to
sign a new one.

### Review Community Guidelines

We adhere to [Google's Open Source Community Guidelines](https://opensource.google/conduct/).
Please familiarize yourself with these guidelines to ensure a positive and
collaborative environment for everyone.

### Acceptance Criteria

We review contributions for third-party tools, plugins, and observability
integrations based on the following criteria:

-   **Completeness and testability**: The integration should be functional and
    testable. Include working code examples that developers can run.
-   **Value for developers**: The tool or integration should provide clear
    value for developers building agents with ADK.
-   **Publishability**: We must be able to publish the documentation in our
    official docs. For example, we cannot accept tools that circumvent technical
    protection measures, violate terms of service, or access services without
    authorization.

### Tips for Success

-   **Test your documentation locally** using `mkdocs serve` before submitting
-   **Include complete, working code examples** that users can copy and run
-   **Keep descriptions concise** but informative
-   **Link to external resources** for detailed platform-specific documentation
-   **Use consistent formatting** with existing documentation pages

## Set Up Your Environment

1.  **Clone the repository:**

    ```shell
    git clone git@github.com:google/adk-docs.git
    cd adk-docs
    ```

2.  **Create and activate a virtual environment:**

    ```shell
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```shell
    pip install -r requirements.txt
    ```

4.  **Run the local development server:**

    ```shell
    mkdocs serve
    ```

    This command starts a local server, typically at `http://127.0.0.1:8000/`.

## Create Your Contribution

| Type | Description |
|------|-------------|
| [Documentation fixes](#documentation-fixes) | Fix typos, broken links, or minor wording improvements |
| [New documentation](#new-documentation) | Add a new guide, tutorial, or reference page |
| [Major changes](#major-changes) | Large-scale reorganization or refactoring |
| [Third-party tools](#third-party-tools) | MCP servers or packages that provide tools for ADK agents |
| [Third-party plugins](#third-party-plugins) | Callback-based extensions for logging, metrics, or policy enforcement |
| [Observability integrations](#observability-integrations) | Monitoring and debugging platforms for ADK agents |

### Documentation Fixes

For typo fixes, broken links, or small wording improvements:

1.  Edit the file directly on GitHub or clone the repo locally
2.  Submit a pull request with a clear description of the fix
3.  No issue required for small fixes

### New Documentation

For new guides, tutorials, or reference pages:

1.  **Open an issue first** to discuss the proposed content
2.  Create your Markdown file in the appropriate `docs/` subdirectory
3.  Add navigation entry to `mkdocs.yml` if needed
4.  Test locally with `mkdocs serve`

### Major Changes

For large-scale reorganization or refactoring:

1.  **Open an issue first** to discuss the scope and approach
2.  Wait for maintainer feedback before starting work
3.  Consider breaking large changes into smaller, reviewable PRs

### Third-Party Tools

Third-party tools include MCP servers or packages that provide tools for ADK
agents. Examples include [Atlassian](docs/tools/third-party/atlassian.md),
[GitHub](docs/tools/third-party/github.md), and
[Hugging Face](docs/tools/third-party/hugging-face.md).

**To contribute a third-party tool:**

1.  **Create the documentation file:**
    Create a new Markdown file at `docs/tools/third-party/<tool-name>.md`.

2.  **Follow the standard structure:**
    Your documentation should include these sections:

    ````markdown
    # Tool Name

    Brief description of the tool and what it connects to. Explain what capabilities it gives ADK agents.

    ## Use cases

    - **Use Case 1**: Description of what users can accomplish
    - **Use Case 2**: Another common use case
    - **Use Case 3**: Additional use case

    ## Prerequisites

    - Required accounts or API keys
    - Any setup steps needed before using the tool

    ## Installation (if applicable)

    ```bash
    pip install your-package-name
    ```

    ## Use with agent

    ```python
    from google.adk.agents import Agent
    # Show a complete, working example
    ```

    ## Available tools

    Tool | Description
    ---- | -----------
    `tool_name_1` | What this tool does
    `tool_name_2` | What this tool does

    ## Additional resources

    - [Link to official documentation](https://example.com)
    - [Link to GitHub repository](https://github.com/example/repo)
    ````

3.  **Add an image asset:**
    Add a logo image to `docs/assets/` named `tools-<tool-name>.png`.
    Images should be square and appropriately sized for display as a card.

4.  **Update the index pages:**
    Add a card entry to **both** of the following files in alphabetical order
    within the "Third-party tools" section. Copy an existing card and modify it:

    - `docs/tools/index.md` (main tools overview page)
    - `docs/tools/third-party/index.md` (dedicated third-party tools page)

5.  **Update the navigation:**
    Add an entry to `mkdocs.yml` under the `Third-party tools` section in
    alphabetical order:

    ```yaml
    - Tool Name: tools/third-party/<tool-name>.md
    ```

### Third-Party Plugins

Plugins are packages that extend ADK using callback hooks for functionality
that applies across your entire agent workflow, such as logging, metrics, or
policy enforcement.

**To contribute a third-party plugin:**

Follow the same process as [third-party tools](#third-party-tools), but:

-   Create the file at `docs/tools/third-party/<plugin-name>.md`
-   Use `plugins-<plugin-name>.png` for the asset image
-   Explain in the documentation that your contribution is a plugin (uses
    `BasePlugin` and callback hooks) rather than a tool

Refer to the [Plugins documentation](https://google.github.io/adk-docs/plugins/) for details on how
plugins work in ADK.

### Observability Integrations

Observability integrations help developers monitor, debug, and analyze their ADK
agents. Examples include [AgentOps](docs/observability/agentops.md),
[Phoenix](docs/observability/phoenix.md), and
[Weave](docs/observability/weave.md).

Most integrations use one of two approaches:

-   **OpenTelemetry/OTLP exporters**: Configure an OTLP span exporter to send
    ADK's built-in traces to your platform
-   **Dedicated instrumentation packages**: Install a package that
    auto-instruments ADK

**To contribute an observability integration:**

1.  **Create the documentation file:**
    Create a new Markdown file at `docs/observability/<platform-name>.md`.

2.  **Follow the standard structure:**
    Your documentation should include these sections:

    ````markdown
    # Agent Observability with Platform Name

    Brief description of the platform and what it provides for ADK observability.
    Link to the platform's website and sign-up page.

    ## Overview (or "Why Platform Name for ADK?")

    Explain the key benefits:
    - **Feature 1**: What it provides
    - **Feature 2**: What it provides
    - **Feature 3**: What it provides

    ## Prerequisites (if applicable)

    - Required software versions
    - Account requirements
    - API keys needed

    ## Installation

    ```bash
    pip install required-packages
    ```

    ## Setup

    ### 1. Create an Account / Get API Key

    Instructions for getting started with the platform.

    ### 2. Configure Your Environment

    ```python
    import os
    os.environ["API_KEY"] = "your-api-key"
    ```

    ### 3. Initialize the Integration

    ```python
    # Show how to set up tracing/instrumentation
    ```

    ## Observe (or "View Traces")

    Show a complete working example with an ADK agent.
    Include screenshots of your platform's dashboard showing ADK traces.

    ## Resources

    - [Platform Documentation](https://example.com/docs)
    - [GitHub Repository](https://github.com/example/repo)
    - [Community/Support Links](https://example.com/community)
    ````

3.  **Include screenshots:**
    Screenshots of your platform's dashboard showing ADK traces are strongly
    encouraged. Host images externally or add them to `docs/assets/`.

4.  **Update the navigation:**
    Add an entry to `mkdocs.yml` under the `Observability` section:

    ```yaml
    - Platform Name: observability/<platform-name>.md
    ```

## Submit Your Contribution

All contributions, including those from project members, undergo a review
process.

1.  **Create a Pull Request:** We use GitHub Pull Requests (PRs) for code
    review. Please refer to
    [GitHub Help](https://help.github.com/articles/about-pull-requests/) if
    you're unfamiliar with PRs.
2.  **Review Process:** Project maintainers will review your PR, providing
    feedback or requesting changes if necessary.
3.  **Merging:** Once the PR is approved and passes any required checks, it will
    be merged into the main branch.

We look forward to your contributions!
