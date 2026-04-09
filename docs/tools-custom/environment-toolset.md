---
title: Environment Toolset
---

The `EnvironmentToolset` provides your agent with a toolkit for interacting with an execution environment. This allows your agent to perform actions like running shell commands, reading files, and writing to files.

## Core Concepts

### BaseEnvironment

The `BaseEnvironment` is an abstract class that defines the interface for an execution environment. It outlines the methods necessary for the `EnvironmentToolset` to operate, such as `execute`, `read_file`, and `write_file`. You can create custom environments by subclassing `BaseEnvironment` and implementing its methods.

### LocalEnvironment

The ADK includes a concrete implementation of the `BaseEnvironment` called `LocalEnvironment`. This class provides a sandboxed environment on your local machine, allowing your agent to safely execute commands and interact with the local filesystem within a specified working directory.

## Tools Included

The `EnvironmentToolset` comes with the following four tools:

*   **`ExecuteTool`**: Executes a shell command in the environment's working directory.
*   **`ReadFileTool`**: Reads the entire content of a file.
*   **`WriteFileTool`**: Writes content to a file, creating the file if it doesn't exist or overwriting it if it does.
*   **`EditFileTool`**: Performs a sed-like replacement on a file.

## Usage

To use the `EnvironmentToolset`, you need to instantiate an environment, such as the `LocalEnvironment`, and pass it to the toolset. Then, assign the toolset to your agent.

```python
from google.adk.agents import Agent
from google.adk.tools.environment import EnvironmentToolset
from google.adk.tools.environment import LocalEnvironment

# 1. Instantiate a LocalEnvironment
# This creates a sandboxed environment in the specified working directory.
local_env = LocalEnvironment(working_dir='/path/to/your/sandbox')

# 2. Create an EnvironmentToolset with the environment
environment_toolset = EnvironmentToolset(environment=local_env)

# 3. Assign the toolset to your agent
my_agent = Agent(
    tools=[environment_toolset],
    # ... other agent configuration
)
```

### System Instruction

The `EnvironmentToolset` automatically injects a system instruction, `ENVIRONMENT_INSTRUCTION`, into the LLM request. This instruction informs the model about the current working directory and provides guidelines on how to use the environment tools effectively and responsibly. This helps the LLM to better understand its capabilities and limitations within the provided environment.
