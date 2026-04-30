# Environment Toolsets for ADK

Supported in ADKPython v1.29.0Experimental

Some types of tasks, particularly coding and file operations, require an agent to interact with a compute environment that can run code and operate on files that persist across multiple agent requests. The ***EnvironmentToolset*** class for ADK allows agents to interact with an environment to perform file operations and execute shell commands. The Environment Toolset is designed as a general framework for configuring and using local or remote execution environments with ADK agents. ADK provides a [***LocalEnvironment***](#local-environment) implementation for use with the Environment Toolset framework.

Experimental

The Environment Toolset feature is experimental and may be updated. We welcome your [feedback](https://github.com/google/adk-python/issues/new?template=feature_request.md)!

## Get started

Enable local environment interactions by adding the ***EnvironmentToolset*** with a ***LocalEnvironment*** instance to your agent's tools.

```python
from google.adk import Agent
from google.adk.environment import LocalEnvironment
from google.adk.tools.environment import EnvironmentToolset

root_agent = Agent(
    model="gemini-flash-latest",
    name="my_agent",
    instruction="""
    You are a helpful AI assistant that can use the local environment
    to execute commands and file I/O. Follow the rules of the
    environment and the user's instructions.
    """,
    tools=[
        EnvironmentToolset(
            environment=LocalEnvironment(),
        ),
    ],
)
```

For a full implementation example, see the [Local environment sample](https://github.com/google/adk-python/tree/main/contributing/samples/local_environment).

### Try with agent

You can interact with an agent configured with the Environment Toolset by providing prompts that require file operations and command execution. Try the following prompt in an interactive session with an agent:

```text
Write a Python file named hello.py to the working directory
that prints 'Hello from ADK!'. Then read the file to verify
its contents, and finally execute it using a command.
```

Based on these instructions, the agent performs the following operations:

- Write File: The agent writes a `hello.py` file with the content "Hello from ADK!".
- Read File: The agent reads the `hello.py` file and verifies its content.
- Execute: The agent runs the `hello.py` file and returns the output.

## LocalEnvironment

The ***LocalEnvironment*** class is an environment implementation provided by ADK for use with ***Environment Toolset***. This environment provides the following capabilities:

- **Local Execution:** Run shell commands and scripts directly on the local machine using Python asyncio subprocesses.
- **File Operations:** Create, read, and modify files within a specified working directory.
- **Customization:** Configure custom environment variables and working directories for the agent's workspace.
- **Framework Compatibility:** Works with both ADK 1.0 and ADK 2.0 framework versions, including graph-based workflows.

### Configuration options

The ***LocalEnvironment*** class supports the following parameters:

- **working_dir**: (optional) The directory where the agent will perform file operations and execute commands. Setting a working directory means that any generated files are still accessible after the agent runs. For more details, see [File persistence](#file-persistence).
- **env_vars**: (optional) A dictionary of environment variables to be set for the execution context.

The following code sample shows how to set these options for a ***LocalEnvironment*** object:

```python
local_environment=LocalEnvironment(
    working_dir="/tmp/my_agent_workspace",
    env_vars={"PORT": "8080", "LOG_LEVEL": "DEBUG"},
)
```

### File operations

The ***LocalEnvironment*** implementation includes the following tools an agent can run within a local compute environment:

- ***ReadFile***: Read an existing text file based on agent instructions.
- ***EditFile***: Edit an existing text file based on agent instructions.
- ***WriteFile***: Create a new text file based on agent instructions.
- ***Execute***: Execute terminal commands, including running installers, shell scripts, and program code, based on agent instructions.

Danger: Potential data loss, code execution

Executing terminal commands in a local environment can cause loss of data and impact the execution of code and applications in that environment. Exercise caution and consider implementing human permission checks before allowing agents to change files and execute commands.

Commands executed with ***LocalEnvironment*** use `asyncio.create_subprocess_shell`, ensuring that the agent remains responsive during long-running tasks.

### File persistence

Files and file output generated with the ***LocalEnvironment*** are placed in a temporary directory by default. That directory is removed when an agent is shut down, for example, when exiting an ADK Web session. However, if you set a ***working directory*** for the environment, any files written there *are not removed* after the agent shuts down.

**Tip:** If you want more control over how files are persisted between agent sessions, use [***Artifacts***](/artifacts/) and the Artifact Service to upload and download files to the environment.

## Custom environments

The ***EnvironmentToolset*** architecture is designed to be extensible so you can build your own custom environments, including remote environments. We encourage you to build execution environments for use with this feature using the [BaseEnvironment](https://github.com/google/adk-python/blob/main/src/google/adk/environment/_base_environment.py) class. You can review the code for the [LocalEnvironment](https://github.com/google/adk-python/blob/main/src/google/adk/environment/_local_environment.py) implementation to help you get started.
