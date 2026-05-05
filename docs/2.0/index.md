# Welcome to ADK 2.0 Beta

!!! example "Beta Release"

    ADK 2.0 is a Beta release and may cause breaking changes when used with prior
    versions of ADK. Do not use ADK 2.0 if you require backwards compatibility, such
    as in production environments. We encourage you to test this release and we
    welcome your
    [feedback](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)!

ADK 2.0 introduces powerful tools for building sophisticated AI agents, and
helps you structure agents to execute challenging tasks with more control,
predictability, and reliability. ADK 2.0 is available as a Beta release for
Python and includes the following key features:

-   [**Graph-based workflows**](/workflows/): Build deterministic agent
    workflows with more control over how tasks are routed and executed.

-   [**Collaborative agents**](/workflows/collaboration/):
    Build complex agent architectures with coordinator agents and multiple
    subagents working together.

-   [**Dynamic workflows**](/workflows/dynamic/):
    Use code-based logic for building more complex workflows including
    iterative loops and complex decision-based branching.

Check out the linked topics above for more information, and try out the new way
to build agents with ADK 2.0!

## ADK 1.0 compatibility

ADK 2.0 is designed to be compatible with agents developed with ADK 1.x
releases. However, given the number and diversity of agents built with ADK 1.x,
we expect that some agent implementations, particularly advanced and
feature-rich agents, will uncover incompatibilities in ADK 2.0. During the
current pre-GA release period, we ask your assistance helping us identify these
issues so we have a chance to address them. Report any ADK 1.0 to ADK 2.0
incompatibilities you encounter through our
[issue tracker](https://github.com/google/adk-python/issues/new?template=bug_report.md&labels=v2).


## Install ADK 2.0 {#install}

While ADK 2.0 is available as a pre-GA release, it is not installed automatically.
You must select it as an installation option. This version has the following
system requirements:

*   **Python 3.10** or later
*   `pip` for installing packages

To install ADK 2.0, follow these steps:

1.  Enable a Python virtual environment. See below for instructions.

1.  Install the package using pip using `--pre` to select the current,
    pre-GA version of ADK 2.0:

    ```bash
    pip install google-adk --pre
    ```

??? tip "Recommended: Create and activate a Python virtual environment"

    Create a Python virtual environment:

    ```shell
    python3 -m venv .venv
    ```

    Activate the Python virtual environment:

    === "Windows CMD"

        ```console
        .venv\Scripts\activate.bat
        ```

    === "Windows Powershell"

        ```console
        .venv\Scripts\Activate.ps1
        ```

    === "MacOS / Linux"

        ```bash
        source .venv/bin/activate
        ```

!!! note "Note: Updating existing ADK 1.0 projects"

    The `--pre` option does not install the ADK 2.0 libraries if you already have
    ADK 1.0 libraries installed in a Python environment. You can force installation
    of the ADK 2.0 library by adding the `--force` option to the install command
    shown above. Remember to use Python virtual environments for ADK 2.0, and
    **ensure you have backups of ADK 1.0 projects *before* updating them to
    use ADK 2.0 libraries.**

## Next steps

Read the developer guides for building agents with ADK 2.0 features:

-   [**Graph-based workflows**](/workflows/)
-   [**Collaborative agents**](/workflows/collaboration/)
-   [**Dynamic workflows**](/workflows/dynamic/)

Check out these ADK 2.0 code samples for testing and inspiration:

-   [**Workflow samples**](https://github.com/google/adk-python/tree/v2/contributing/workflow_samples)
-   [**Collaborative task samples**](https://github.com/google/adk-python/tree/v2/contributing/task_samples)

Thanks for checking out ADK 2.0! We look forward to your
[feedback](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)!
