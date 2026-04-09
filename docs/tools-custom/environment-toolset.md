# Environment Toolset

The Environment Toolset provides a structured way for agents to run shell commands and interact with a file system. It's a powerful feature that allows agents to perform a wide range of tasks, from simple file manipulations to complex software builds.

## Key Components

The Environment Toolset is built around two key components: the `Environment` and the `Toolset`.

### Environment

The `Environment` is an abstraction that defines a consistent interface for interacting with a file system and executing commands. The ADK provides a base class, `BaseEnvironment`, that you can extend to create your own custom environments. The ADK also provides a concrete implementation, `LocalEnvironment`, that interacts with the local file system.

#### BaseEnvironment

`BaseEnvironment` is an abstract base class that defines the following methods:

*   `execute(command, timeout)`: Executes a shell command.
*   `read_file(path)`: Reads the content of a file.
*   `write_file(path, content)`: Writes content to a file.

#### LocalEnvironment

`LocalEnvironment` is a concrete implementation of `BaseEnvironment` that uses local subprocesses to execute commands and interacts with the local filesystem. You can specify a working directory for the `LocalEnvironment`, or it will create a temporary one for you.

### Toolset

The `EnvironmentToolset` is a pre-built toolset that includes four tools for interacting with an environment:

*   `ExecuteTool`: Executes a shell command in the environment.
*   `ReadFileTool`: Reads a file from the environment's file system.
*   `WriteFileTool`: Writes content to a file in the environment's file system.
*   `EditFileTool`: Performs a surgical text replacement on a file in the environment's file system.

## How to use the Environment Toolset

To use the Environment Toolset, you need to:

1.  Instantiate an environment, such as `LocalEnvironment`.
2.  Instantiate an `EnvironmentToolset`, passing the environment to it.
3.  Assign the toolset to your agent.

Here's an example of how to do this:

```python
from google.adk.agents import Agent
from google.adk.tools.environment import EnvironmentToolset, LocalEnvironment

# 1. Instantiate a LocalEnvironment
# This will create a temporary working directory.
env = LocalEnvironment()

# 2. Instantiate an EnvironmentToolset
env_toolset = EnvironmentToolset(environment=env)

# 3. Assign the toolset to your agent
my_agent = Agent(
    toolsets=[env_toolset]
)
```

## System Instruction

The `EnvironmentToolset` also injects a specific system instruction (`ENVIRONMENT_INSTRUCTION`) into the LLM's prompt. This instruction guides the LLM on how to use the tools provided by the toolset properly. It provides information about the current working directory and other important details about the environment.
