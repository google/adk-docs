---
catalog_title: GKE Code Executor
catalog_description: Run AI-generated code in a secure and scalable GKE environment
catalog_icon: /adk-docs/integrations/assets/gke.png
catalog_tags: ["code","google"]
---

# Google Cloud GKE Code Executor tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.14.0</span>
</div>

The GKE Code Executor (`GkeCodeExecutor`) provides a secure and scalable method
for running LLM-generated code by leveraging the GKE (Google Kubernetes Engine)
Sandbox environment, which uses gVisor for workload isolation. For each code
execution request, it dynamically creates an ephemeral, sandboxed Kubernetes Job
with a hardened Pod configuration. You should use this executor for production
environments on GKE where security and isolation are critical.

## How it Works

When a request to execute code is made, the `GkeCodeExecutor` performs the following steps:

1.  **Creates a ConfigMap:** A Kubernetes ConfigMap is created to store the Python code that needs to be executed.
2.  **Creates a Sandboxed Pod:** A new Kubernetes Job is created, which in turn creates a Pod with a hardened security context and the gVisor runtime enabled. The code from the ConfigMap is mounted into this Pod.
3.  **Executes the Code:** The code is executed within the sandboxed Pod, isolated from the underlying node and other workloads.
4.  **Retrieves the Result:** The standard output and error streams from the execution are captured from the Pod's logs.
5.  **Cleans Up Resources:** Once the execution is complete, the Job and the associated ConfigMap are automatically deleted, ensuring that no artifacts are left behind.

## Key Benefits

*   **Enhanced Security:** Code is executed in a gVisor-sandboxed environment with kernel-level isolation.
*   **Ephemeral Environments:** Each code execution runs in its own ephemeral Pod, to prevent state transfer between executions.
*   **Resource Control:** You can configure CPU and memory limits for the execution Pods to prevent resource abuse.
*   **Scalability:** Allows you to run a large number of code executions in parallel, with GKE handling the scheduling and scaling of the underlying nodes.

## System requirements

The following requirements must be met to successfully deploy your ADK project
with the GKE Code Executor tool:

- GKE cluster with a **gVisor-enabled node pool**.
- Agent's service account requires specific **RBAC permissions**, which allow it to:
    - Create, watch, and delete **Jobs** for each execution request.
    - Manage **ConfigMaps** to inject code into the Job's pod.
    - List **Pods** and read their **logs** to retrieve the execution result
- Install the client library with GKE extras: `pip install google-adk[gke]`

For a complete, ready-to-use configuration, see the
[deployment_rbac.yaml](https://github.com/google/adk-python/blob/main/contributing/samples/gke_agent_sandbox/deployment_rbac.yaml)
sample. For more information on deploying ADK workflows to GKE, see
[Deploy to Google Kubernetes Engine (GKE)](/adk-docs/deploy/gke/).

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.code_executors import GkeCodeExecutor

    # Initialize the executor, targeting the namespace where its ServiceAccount
    # has the required RBAC permissions.
    # This example also sets a custom timeout and resource limits.
    gke_executor = GkeCodeExecutor(
        namespace="agent-sandbox",
        timeout_seconds=600,
        cpu_limit="1000m",  # 1 CPU core
        mem_limit="1Gi",
    )

    # The agent now uses this executor for any code it generates.
    gke_agent = LlmAgent(
        name="gke_coding_agent",
        model="gemini-2.0-flash",
        instruction="You are a helpful AI agent that writes and executes Python code.",
        code_executor=gke_executor,
    )
    ```

## Configuration parameters

The `GkeCodeExecutor` can be configured with the following parameters:

| Parameter            | Type   | Description                                                                             |
| -------------------- | ------ | --------------------------------------------------------------------------------------- |
| `namespace`          | `str`  | Kubernetes namespace where the execution Jobs will be created. Defaults to `"default"`. |
| `image`              | `str`  | Container image to use for the execution Pod. Defaults to `"python:3.11-slim"`.         |
| `timeout_seconds`    | `int`  | Timeout in seconds for the code execution. Defaults to `300`.                           |
| `cpu_requested`      | `str`  | Amount of CPU to request for the execution Pod. Defaults to `"200m"`.                   |
| `mem_requested`      | `str`  | Amount of memory to request for the execution Pod. Defaults to `"256Mi"`.               |
| `cpu_limit`          | `str`  | Maximum amount of CPU the execution Pod can use. Defaults to `"500m"`.                  |
| `mem_limit`          | `str`  | Maximum amount of memory the execution Pod can use. Defaults to `"512Mi"`.              |
| `kubeconfig_path`    | `str`  | Path to a kubeconfig file to use for authentication. Falls back to in-cluster config or the default local kubeconfig. |
| `kubeconfig_context` | `str`  | The `kubeconfig` context to use.  |
