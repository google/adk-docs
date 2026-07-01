---
catalog_title: Cloud Run Sandbox Code Executor
catalog_description: Run AI-generated code inside secure Cloud Run sandboxes
catalog_icon: /integrations/assets/cloud-run.png
catalog_tags: ["code","google"]
---

# Google Cloud Run Sandbox Code Executor tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.23.0</span>
</div>

The Cloud Run Sandbox Code Executor (`CloudRunSandboxCodeExecutor`) provides a secure method for executing LLM-generated code by leveraging Google Cloud Run's sandboxing capabilities. 

This executor is designed to run from **within** a Cloud Run container (such as a Cloud Run Service) where the sandbox launcher is enabled. It executes untrusted code locally inside an isolated guest sandbox using the container's own Python interpreter, preventing the code from accessing the parent container's environment or credentials.

## How it works

When a request to execute code is made, the `CloudRunSandboxCodeExecutor` performs the following steps:

1. Writes the code to the standard input (`stdin`) of the guest sandbox execution command.
2. Spawns the guest sandbox binary using `sandbox do <python_path>`.
3. The guest sandbox executes the code using the parent container's Python interpreter (resolved via `sys.executable`) mounted inside a read-only root filesystem.
4. Captures the standard output and standard error from the execution.
5. Suppresses harmless network namespace cleanup warnings from `stderr` to ensure only actual runtime errors are returned.

## System requirements

To successfully use the Cloud Run Sandbox Code Executor:

- Your ADK project must be deployed to a **Google Cloud Run Service**.
- The Cloud Run resource must be created with the **Sandbox Launcher** enabled. You can do this by deploying with the `--sandbox-launcher` flag:
  ```bash
  gcloud beta run deploy my-agent-service \
      --image=gcr.io/my-project/my-agent-image \
      --sandbox-launcher
  ```
- The container image must include a Python 3 installation (e.g. `python:3.11-slim`), which will be used to run the guest code.
- No special Python extra packages are required (it uses standard library subprocess execution).

## Configuration parameters

The `CloudRunSandboxCodeExecutor` can be configured with the following parameters:

| Parameter           | Type          | Description                                                                                                                                           |
| ------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sandbox_bin`       | `str`         | Path to the local guest sandbox binary in the container. Defaults to `"/usr/local/gcp/bin/sandbox"`.                                                 |
| `allow_egress`      | `bool`        | Whether to allow outbound network connections (egress) from the sandbox. Defaults to `False`.                                                         |
| `timeout_seconds`   | `int \| None` | Timeout in seconds for the code execution. Defaults to `None` (no timeout).                                                                           |

> [!NOTE]
> Unlike other executors, `CloudRunSandboxCodeExecutor` does not support `stateful=True` or `optimize_data_file=True`. Every code block runs in a fresh ephemeral sandbox instance within the container.

## Usage Example

```python
from google.adk.agents import LlmAgent
from google.adk.code_executors import CloudRunSandboxCodeExecutor
from google.adk.code_executors import CodeExecutionInput
from google.adk.agents.invocation_context import InvocationContext

# Initialize the executor with egress allowed and a 60-second timeout
cloud_run_executor = CloudRunSandboxCodeExecutor(
    allow_egress=True,
    timeout_seconds=60,
)

# Example direct execution:
ctx = InvocationContext()
result = cloud_run_executor.execute_code(
    ctx, 
    CodeExecutionInput(code="import urllib.request; print(urllib.request.urlopen('https://example.com').read()[:100])")
)
print(result.stdout)

# Example registering with an Agent:
agent = LlmAgent(
    name="sandbox_coding_agent",
    model="gemini-flash-latest",
    instruction="You are a helpful AI assistant that solves math problems by writing and executing Python code.",
    code_executor=cloud_run_executor,
)
```
