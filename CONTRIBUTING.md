# How to contribute

Thank you for your interest in contributing! We appreciate your willingness to
share your patches and improvements with the project.

## Before You Start

We're excited to have you contribute! To help your contribution go smoothly,
please review the following sections before you begin.

### Find Something to Work On

Check the [GitHub Issues](https://github.com/google/adk-docs/issues) for bug
reports or feature requests. Feel free to pick up an existing issue or open a
new one if you have an idea or find a bug.

### Sign the Contributor License Agreement

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

We review contributions for integrations based on the following criteria:

- **Completeness and testability**: The integration should be functional and
  testable. Include working code examples that developers can run.
- **Value for developers**: The integration should provide clear value for
  developers building agents with ADK.
- **Publishability**: We must be able to publish the documentation in our
  official docs. For example, we cannot accept integrations that circumvent
  technical protection measures, violate terms of service, or access services
  without authorization.

### Tips for Success

- **Test your documentation locally** using `mkdocs serve` before submitting
- **Include complete, working code examples** that users can copy and run
- **Keep descriptions concise** but informative
- **Link to external resources** for detailed platform-specific documentation
- **Use consistent formatting** with existing documentation pages

## Set Up Your Environment

1. **Clone the repository:**

    ```shell
    git clone git@github.com:google/adk-docs.git
    cd adk-docs
    ```

2. **Create and activate a virtual environment:**

    ```shell
    python -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies:**

    ```shell
    pip install -r requirements.txt
    ```

4. **Run the local development server:**

    ```shell
    mkdocs serve
    ```

    This command starts a local docs server, typically at
    `http://127.0.0.1:8000/`.

## Create Your Contribution

| Type | Description |
|------|-------------|
| [Documentation fixes](#documentation-fixes) | Fix typos, broken links, or minor wording improvements |
| [New documentation](#new-documentation) | Add a new guide, tutorial, or reference page |
| [Major changes](#major-changes) | Large-scale reorganization or refactoring |
| [Integrations](#integrations) | Tools, plugins, observability libraries, user interfaces, or any extensions to ADK agents or agent development |

### Documentation Fixes

For typo fixes, broken links, or small wording improvements:

1. Edit the file directly on GitHub or clone the repo locally
2. Submit a pull request with a clear description of the fix
3. No issue required for small fixes

### New Documentation

For new guides, tutorials, or reference pages:

1. **Open an issue first** to discuss the proposed content
2. Create your Markdown file in the appropriate `docs/` subdirectory
3. Add navigation entry to `mkdocs.yml` if needed
4. Test locally with `mkdocs serve`

### Major Changes

For large-scale reorganization or refactoring:

1. **Open an issue first** to discuss the scope and approach
2. Wait for maintainer feedback before starting work
3. Consider breaking large changes into smaller, reviewable PRs

### Integrations

Integrations include third-party tools, plugins, and observability platforms for
ADK agents. All integrations live under `docs/integrations/`. Examples include
[GitHub](https://google.github.io/adk-docs/integrations/github/),
[Daytona](https://google.github.io/adk-docs/integrations/daytona/), and
[AgentOps](https://google.github.io/adk-docs/integrations/agentops/).

**To contribute an integration:**

1. **Create the documentation file:**

    Create a new Markdown file at `docs/integrations/<name>.md`.

2. **Follow the standard structure:**

    Your documentation should include frontmatter and the sections below that
    are relevant to your integration.

    See [existing integration
    pages](https://github.com/google/adk-docs/tree/main/docs/integrations) for
    reference.

    ````markdown
    ---
    catalog_title: Integration Name
    catalog_description: A short description of what your integration does
    catalog_icon: /adk-docs/integrations/assets/<name>.png
    ---

    # Integration Name

    Brief description of the integration and what it provides for ADK agents.

    ## Use cases

    - **Use Case 1**: Description of what users can accomplish
    - **Use Case 2**: Another common use case
    - **Use Case 3**: Additional use case

    ## Prerequisites

    - Required software versions
    - Required accounts or API keys
    - Any setup steps needed

    ## Installation

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

    ## Resources

    - [Platform Documentation](https://example.com/docs)
    - [GitHub Repository](https://github.com/example/repo)
    - [Community/Support Links](https://example.com/community)
    ````

3. **Add an image asset:**

    Add a logo image to `docs/integrations/assets/` named `<name>.png`.
    Images should be square and appropriately sized for display as a card.

4. **Include screenshots:**

    Screenshots or visuals that illustrate your integration in action are
    strongly encouraged. Add them to `docs/integrations/assets/`.

## Submit Your Contribution

All contributions, including those from project members, undergo a review
process.

1. **Create a Pull Request:** We use GitHub Pull Requests (PRs) for code review.
   Please refer to [GitHub
   Help](https://help.github.com/articles/about-pull-requests/) if you're
   unfamiliar with PRs.

2. **Review Process:** Project maintainers will review your PR, providing
   feedback or requesting changes if necessary.

3. **Merging:** Once the PR is approved and passes any required checks, it will
   be merged into the main branch.

We look forward to your contributions!
