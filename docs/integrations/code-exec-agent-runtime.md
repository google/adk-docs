---
catalog_title: Code Execution Tool with Agent Runtime
catalog_description: Run AI-generated code in a secure and scalable environment
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["code", "google"]
---

# Agent Runtime Code Execution tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.17.0</span>
</div>

The Agent Runtime Code Execution ADK Tool provides a low-latency, highly
efficient method for running AI-generated code using the
[Google Cloud Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
service. This tool is designed for fast execution, tailored for agentic workflows,
and uses sandboxed environments for improved security. The Code Execution tool
allows code and data to persist over multiple requests, enabling complex,
multi-step coding tasks, including:

-   **Code development and debugging:** Create agent tasks that test and
    iterate on versions of code over multiple requests.
-   **Code with data analysis:** Upload data files up to 100MB, and run
    multiple code-based analyses without the need to reload data for each code run.

This code execution tool is part of the Agent Runtime suite, however you do not
have to deploy your agent to Agent Runtime to use it. You can run your agent
locally or with other services and use this tool. For more information about the
Code Execution feature in Agent Runtime, see the
[Agent Runtime Code Execution](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/overview)
documentation.


## Use the Tool

Using the Agent Runtime Code Execution tool requires that you create a sandbox
environment with Google Cloud Agent Runtime before using the tool with an ADK
agent.

To use the Code Execution tool with your ADK agent:

1.  Follow the instructions in the Agent Runtime
    [Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart)
    to create a code execution sandbox environment.
1.  Create an ADK agent with settings to access the Google Cloud project
    where you created the sandbox environment.
1.  The following code example shows an agent configured to use the Code
    Executor tool. Replace `SANDBOX_RESOURCE_NAME` with the sandbox environment
    resource name you created.

```python
--8<-- "examples/inline/python/integrations/code-exec-agent-runtime/001-use-the-tool.py"
```

For details on the expected format of the `sandbox_resource_name` value, and the
alternative `agent_engine_resource_name` parameter, see [Configuration
parameters](#config-parameters). For a more advanced example, including
recommended system instructions for the tool, see the [Advanced
example](#advanced-example) or the full
[agent code example](https://github.com/google/adk-python/tree/main/contributing/samples/code_execution/agent_engine_code_execution).

## How it works

The `AgentEngineSandboxCodeExecutor` Tool maintains a single sandbox throughout an
agent's task, meaning the sandbox's state persists across all operations within
an ADK workflow session.

1.  **Sandbox creation:** For multi-step tasks requiring code execution,
    the Agent Runtime creates a sandbox with specified language and machine
    configurations, isolating the code execution environment. If no sandbox is
    pre-created, the code execution tool will automatically create one using
    default settings.
1.  **Code execution with persistence:** AI-generated code for a tool call
    is streamed to the sandbox and then executed within the isolated
    environment. After execution, the sandbox *remains active* for subsequent
    tool calls within the same session, preserving variables, imported modules,
    and file state for the next tool call from the same agent.
1.  **Result retrieval:** The standard output, and any captured error
    streams are collected and passed back to the calling agent.
1.  **Sandbox clean up:** Once the agent task or conversation concludes, the
    agent can explicitly delete the sandbox, or rely on the TTL feature of the
    sandbox specified when creating the sandbox.

## Key benefits

-   **Persistent state:** Solve complex tasks where data manipulation or
    variable context must carry over between multiple tool calls.
-   **Targeted Isolation:** Provides robust process-level isolation,
    ensuring that tool code execution is safe while remaining lightweight.
-   **Agent Runtime integration:** Tightly integrated into the Agent Runtime
    tool-use and orchestration layer.
-   **Low-latency performance:** Designed for speed, allowing agents to
    execute complex tool-use workflows efficiently without significant overhead.
-   **Flexible compute configurations:** Create sandboxes with specific
    programming language, processing power, and memory configurations.

## System requirements¶

The following requirements must be met to successfully use the Agent Runtime
Code Execution tool with your ADK agents:

-   Google Cloud project with Agent Platform API enabled
-   Agent's service account requires **roles/aiplatform.user** role, which
    allow it to:
    -   Create, get, list and delete code execution sandboxes
    -   Execute code execution sandbox

## Configuration parameters {#config-parameters}

The Agent Runtime Code Execution tool has the following parameters. You must set
one of the following resource parameters:

-   **`sandbox_resource_name`** : A sandbox resource path to an
    existing sandbox environment it uses for each tool call. The expected
string format is as follows:
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}/sandboxEnvironments/{$SANDBOX_ENVIRONMENT_ID}

    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172/sandboxEnvironments/6545148888889161728
    ```
-   **`agent_engine_resource_name`**: Agent Runtime resource name where the tool
creates a sandbox environment. The expected string format is as follows:
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}

    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172
    ```

You can use Google Cloud Agent Runtime's API to configure Agent Runtime sandbox
environments separately using a Google Cloud client connection, including the
following settings:

-   **Programming languages,** including Python and JavaScript
-   **Compute environment**, including CPU and memory sizes

For more information on connecting to Google Cloud Agent Runtime and configuring
sandbox environments, see the Agent Runtime
[Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart#create_a_sandbox).

## Advanced example {#advanced-example}

The following example code shows how to implement use of the Code Executor tool
in an ADK agent. This example includes a `base_system_instruction` clause to set
the operating guidelines for code execution. This instruction clause is
optional, but strongly recommended for getting the best results from this tool.

```python
--8<-- "examples/inline/python/integrations/code-exec-agent-runtime/002-advanced-example-advanced-example.py"
```

For a complete version of an ADK agent using this example code, see the
[agent_engine_code_execution sample](https://github.com/google/adk-python/tree/main/contributing/samples/code_execution/agent_engine_code_execution).
