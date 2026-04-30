# Google Cloud GKE Code Executor tool for ADK

Supported in ADKPython v1.14.0

The GKE Code Executor (`GkeCodeExecutor`) provides a secure and scalable method for running LLM-generated code by leveraging Google Kubernetes Engine (GKE). You should use this executor for production environments on GKE where security and isolation are critical. It supports two execution modes:

1. **Sandbox Mode (Recommended):** Utilizes the [Agent Sandbox](https://github.com/kubernetes-sigs/agent-sandbox) client to execute code within sandbox instances created on-demand from a template. This mode offers lower latency by using [pre-warmed sandboxes](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox#create_a_sandboxtemplate_and_sandboxwarmpool) and supports more direct interaction with the sandbox environment.
1. **Job Mode:** Uses the GKE Sandbox environment with gVisor for workload isolation. For each code execution request, it dynamically creates an ephemeral, sandboxed Kubernetes Job with a hardened Pod configuration. This mode is provided for backward compatibility.

## Execution Modes

### Sandbox Mode (`executor_type="sandbox"`)

This is the recommended mode. It uses the `k8s-agent-sandbox` client library to create and communicate with the Agent Sandbox in the GKE Cluster. When a request to execute code is made, it performs the following steps:

1. Creates a `SandboxClaim` using the specified template.
1. Waits for the sandbox instance to become ready.
1. Executes the code in the claimed sandbox.
1. Retrieves the standard output and error.
1. Deletes the `SandboxClaim`, which in turn cleans up the sandbox instance.

This approach is faster than the Job mode as it leverages pre-warmed sandboxes and optimizes startup time provided by the Agent Sandbox controller.

**Key Benefits:**

In addition to all the benefits of the Job mode, Sandbox mode also offers the following features:

- **Lower Latency:** Aims to reduce startup time compared to creating full Kubernetes Jobs.
- **Managed Environment:** Leverages the Agent Sandbox framework for sandbox lifecycle management.

**Prerequisites:**

- An existing Agent Sandbox deployment in your GKE cluster, including the sandbox controller and it's extensions (e.g., sandbox claim controller & sandbox warmpool controller), router, gateway and relevant `SandboxTemplate` resources (e.g., `python-sandbox-template`).
- The necessary RBAC permissions for the ADK agent to create and delete `SandboxClaim` resources.

### Job Mode (`executor_type="job"`)

This mode is provided for backward compatibility. When a request to execute code is made, the `GkeCodeExecutor` performs the following steps:

1. **Creates a ConfigMap:** A Kubernetes ConfigMap is created to store the Python code that needs to be executed.
1. **Creates a Sandboxed Pod:** A new Kubernetes Job is created, which in turn creates a Pod with a hardened security context and the gVisor runtime enabled. The code from the ConfigMap is mounted into this Pod.
1. **Executes the Code:** The code is executed within the sandboxed Pod, isolated from the underlying node and other workloads.
1. **Retrieves the Result:** The standard output and error streams from the execution are captured from the Pod's logs.
1. **Cleans Up Resources:** Once the execution is complete, the Job and the associated ConfigMap are automatically deleted, ensuring that no artifacts are left behind.

**Key Benefits:**

- **Enhanced Security:** Code is executed in a gVisor-sandboxed environment with kernel-level isolation.
- **Ephemeral Environments:** Each code execution runs in its own ephemeral Pod, to prevent state transfer between executions.
- **Resource Control:** You can configure CPU and memory limits for the execution Pods to prevent resource abuse.
- **Scalability:** Allows you to run a large number of code executions in parallel, with GKE handling the scheduling and scaling of the underlying nodes.
- **Minimal Setup:** Relies on standard GKE features and gVisor.

## System requirements

The following requirements must be met to successfully deploy your ADK project with the GKE Code Executor tool:

- GKE cluster with a **gVisor-enabled node pool** (required for both Job Mode's default image and typical Agent Sandbox templates).
- Agent's service account requires specific **RBAC permissions**:
  - **Job Mode:** Create, watch, and delete **Jobs**; Manage **ConfigMaps**; List **Pods** and read their **logs**. For a complete, ready-to-use configuration for Job Mode, see the [deployment_rbac.yaml](https://github.com/google/adk-python/blob/main/contributing/samples/gke_agent_sandbox/deployment_rbac.yaml) sample.
  - **Sandbox Mode:** Permissions to create, get, watch, and delete **SandboxClaim** and **Sandbox** resources within the namespace where the Agent Sandbox is deployed.
- Install the client library with the appropriate extras: `pip install google-adk[gke]`

## Configuration parameters

The `GkeCodeExecutor` can be configured with the following parameters:

| Parameter              | Type                        | Description                                                                                                           |
| ---------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `namespace`            | `str`                       | Kubernetes namespace where the execution resources (Jobs or SandboxClaims) will be created. Defaults to `"default"`.  |
| `executor_type`        | `Literal["job", "sandbox"]` | Specifies the execution mode. Defaults to `"job"`.                                                                    |
| `image`                | `str`                       | (Job Mode) Container image to use for the execution Pod. Defaults to `"python:3.11-slim"`.                            |
| `timeout_seconds`      | `int`                       | (Job Mode) Timeout in seconds for the code execution. Defaults to `300`.                                              |
| `cpu_requested`        | `str`                       | (Job Mode) Amount of CPU to request for the execution Pod. Defaults to `"200m"`.                                      |
| `mem_requested`        | `str`                       | (Job Mode) Amount of memory to request for the execution Pod. Defaults to `"256Mi"`.                                  |
| `cpu_limit`            | `str`                       | (Job Mode) Maximum amount of CPU the execution Pod can use. Defaults to `"500m"`.                                     |
| `mem_limit`            | `str`                       | (Job Mode) Maximum amount of memory the execution Pod can use. Defaults to `"512Mi"`.                                 |
| `kubeconfig_path`      | `str`                       | Path to a kubeconfig file to use for authentication. Falls back to in-cluster config or the default local kubeconfig. |
| `kubeconfig_context`   | `str`                       | The `kubeconfig` context to use.                                                                                      |
| `sandbox_gateway_name` | `str \| None`               | (Sandbox Mode) The name of the sandbox gateway to use. Optional.                                                      |
| `sandbox_template`     | `str \| None`               | (Sandbox Mode) The name of the `SandboxTemplate` to use. Defaults to `"python-sandbox-template"`.                     |

## Usage Examples

```python
from google.adk.agents import LlmAgent
from google.adk.code_executors import GkeCodeExecutor
from google.adk.code_executors import CodeExecutionInput
from google.adk.agents.invocation_context import InvocationContext

# Initialize the executor for Sandbox Mode
# Namespace should have RBAC for SandboxClaims and Sandbox
gke_sandbox_executor = GkeCodeExecutor(
    namespace="agent-sandbox-system",  # Typically where agent-sandbox is installed
    executor_type="sandbox",
    sandbox_template="python-sandbox-template",
    sandbox_gateway_name="your-gateway-name", # Optional
)

# Example direct execution:
ctx = InvocationContext()
result = gke_sandbox_executor.execute_code(ctx, CodeExecutionInput(code="print('Hello from Sandbox Mode')"))
print(result.stdout)

# Example with an Agent:
gke_sandbox_agent = LlmAgent(
    name="gke_sandbox_coding_agent",
    model="gemini-flash-latest",
    instruction="You are a helpful AI agent that writes and executes Python code using sandboxes.",
    code_executor=gke_sandbox_executor,
)
```

```python
from google.adk.agents import LlmAgent
from google.adk.code_executors import GkeCodeExecutor
from google.adk.code_executors import CodeExecutionInput
from google.adk.agents.invocation_context import InvocationContext

# Initialize the executor for Job Mode
# Namespace should have RBAC for Jobs, ConfigMaps, Pods, Logs
gke_executor = GkeCodeExecutor(
    namespace="agent-ns",
    executor_type="job",
    timeout_seconds=600,
    cpu_limit="1000m",  # 1 CPU core
    mem_limit="1Gi",
)

# Example direct execution:
ctx = InvocationContext()
result = gke_executor.execute_code(ctx, CodeExecutionInput(code="print('Hello from Job Mode')"))
print(result.stdout)

# Example with an Agent:
gke_agent = LlmAgent(
    name="gke_coding_agent",
    model="gemini-flash-latest",
    instruction="You are a helpful AI agent that writes and executes Python code.",
    code_executor=gke_executor,
)
```
