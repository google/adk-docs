# Model Context Protocol Tools

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.7.0</span>
</div>

This guide walks you through two ways of integrating Model Context Protocol (MCP) with ADK.

!!! tip "MCP tools for ADK"
    For a list of pre-built MCP tools for ADK, see [Tools and Integrations](/integrations/?topic=mcp).

## What is Model Context Protocol (MCP)?

The Model Context Protocol (MCP) is an open standard designed to standardize how Large Language Models (LLMs) like Gemini and Claude communicate with external applications, data sources, and tools. Think of it as a universal connection mechanism that simplifies how LLMs obtain context, execute actions, and interact with various systems.

MCP follows a client-server architecture, defining how **data** (resources), **interactive templates** (prompts), and **actionable functions** (tools) are exposed by an **MCP server** and consumed by an **MCP client** (which could be an LLM host application or an AI agent).

This guide covers two primary integration patterns:

1. **Using Existing MCP Servers within ADK:** An ADK agent acts as an MCP client, leveraging tools provided by external MCP servers.
2. **Exposing ADK Tools via an MCP Server:** Building an MCP server that wraps ADK tools, making them accessible to any MCP client.

## Key considerations

When you start building with the Model Context Protocol (MCP) and ADK, these key architectural differences will help you design more stable and efficient agents:

* **Protocol vs. Library:** MCP is a protocol specification, defining communication rules. ADK is a Python library/framework for building agents. McpToolset bridges these by implementing the client side of the MCP protocol within the ADK framework. Conversely, building an MCP server in Python requires using the model-context-protocol library.

* **ADK Tools vs. MCP Tools:**

    * ADK Tools (BaseTool, FunctionTool, AgentTool, etc.) are Python objects designed for direct use within the ADK's LlmAgent and Runner.
    * MCP Tools are capabilities exposed by an MCP Server according to the protocol's schema. McpToolset makes these look like ADK tools to an LlmAgent.

* **Asynchronous nature:** Both ADK and the MCP Python library are heavily based on the asyncio Python library. Tool implementations and server handlers should generally be async functions.

* **Stateful sessions (MCP):** MCP establishes stateful, persistent connections between a client and server instance. This differs from typical stateless REST APIs.

    * **Deployment:** This statefulness can pose challenges for scaling and deployment, especially for remote servers handling many users. The original MCP design often assumed client and server were co-located. Managing these persistent connections requires careful infrastructure considerations (e.g., load balancing, session affinity).
    * **ADK McpToolset:** Manages this connection lifecycle. The exit\_stack pattern shown in the examples is crucial for ensuring the connection (and potentially the server process) is properly terminated when the ADK agent finishes.
 
* **Session persistence**: The `MCPToolset` supports object serialization via `getstate` and `setstate` methods. This feature helps your agent maintain its context when deployed to managed environments like Cloud Run or Google Kubernetes Engine (GKE).

!!! Note: While the agent preserves its session state during lifecycle events, active MCP connections are not automatically re-established upon restoration. The agent will re-initialize its connection to the MCP server as needed after the process is restored to ensure a reliable and up-to-date link.

## Prerequisites

Before you begin, ensure you have the following set up:

* **Set up ADK:** Follow the standard ADK [setup instructions](../get-started/index.md) in the quickstart.
* **Install/update Python/Java:** MCP requires Python version of 3.9 or higher for Python or Java 17 or higher.
* **Setup Node.js and npx:** **(Python only)** Many community MCP servers are distributed as Node.js packages and run using `npx`. Install Node.js (which includes npx) if you haven't already. For details, see [https://nodejs.org/en](https://nodejs.org/en).
* **Verify Installations:** **(Python only)** Confirm `adk` and `npx` are in your PATH within the activated virtual environment:

=== "MacOS / Linux"

  ```shell
  # Both commands should print the path to the executables.
  which adk
  which npx
  ```

=== "Windows"

  ```shell
  # Both commands should print the path to the executables.
  Get-Command adk
  Get-Command npx
  ```

## 1. Using MCP servers with ADK agents (ADK as an MCP client) in `adk web`

This section demonstrates how to integrate tools from external MCP (Model Context Protocol) servers into your ADK agents. This is the **most common** integration pattern when your ADK agent needs to use capabilities provided by an existing service that exposes an MCP interface. You will see how the `McpToolset` class can be directly added to your agent's `tools` list, enabling seamless connection to an MCP server, discovery of its tools, and making them available for your agent to use. These examples primarily focus on interactions within the `adk web` development environment.

### `McpToolset` class

The `McpToolset` class is ADK's primary mechanism for integrating tools from an MCP server. When you include an `McpToolset` instance in your agent's `tools` list, it automatically handles the interaction with the specified MCP server. Here's how it works:

1.  **Connection Management:** On initialization, `McpToolset` establishes and manages the connection to the MCP server. This can be a local server process (using `StdioConnectionParams` for communication over standard input/output) or a remote server (using `SseConnectionParams` for Server-Sent Events). The toolset also handles the graceful shutdown of this connection when the agent or application terminates.
2.  **Tool Discovery & Adaptation:** Once connected, `McpToolset` queries the MCP server for its available tools (via the `list_tools` MCP method). It then converts the schemas of these discovered MCP tools into ADK-compatible `BaseTool` instances.
3.  **Exposure to Agent:** These adapted tools are then made available to your `LlmAgent` as if they were native ADK tools.
4.  **Proxying Tool Calls:** When your `LlmAgent` decides to use one of these tools, `McpToolset` transparently proxies the call (using the `call_tool` MCP method) to the MCP server, sends the necessary arguments, and returns the server's response back to the agent.
5.  **Filtering (Optional):** You can use the `tool_filter` parameter when creating an `McpToolset` to select a specific subset of tools from the MCP server, rather than exposing all of them to your agent.

The following examples demonstrate how to use `McpToolset` within the `adk web` development environment. For scenarios where you need more fine-grained control over the MCP connection lifecycle or are not using `adk web`, refer to the "Using MCP Tools in your own Agent out of `adk web`" section later in this page.

### Example 1: File System MCP Server

This Python example demonstrates connecting to a local MCP server that provides file system operations.

#### Step 1: Define your Agent with `McpToolset`

Create an `agent.py` file (e.g., in `./adk_agent_samples/mcp_agent/agent.py`). The `McpToolset` is instantiated directly within the `tools` list of your `LlmAgent`.

*   **Important:** Replace `"/path/to/your/folder"` in the `args` list with the **absolute path** to an actual folder on your local system that the MCP server can access.
*   **Important:** Place the `.env` file in the parent directory of the `./adk_agent_samples` directory.

```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/001-step-1-define-your-agent-with-mcptoolset.py"
```


#### Step 2: Create an `__init__.py` file

Ensure you have an `__init__.py` in the same directory as `agent.py` to make it a discoverable Python package for ADK.

```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/002-step-2-create-an-init-py-file.py"
```

#### Step 3: Run `adk web` and Interact

Navigate to the parent directory of `mcp_agent` (e.g., `adk_agent_samples`) in your terminal and run:

```shell
cd ./adk_agent_samples # Or your equivalent parent directory
adk web
```

!!!info "Note for Windows users"

    When hitting the `_make_subprocess_transport NotImplementedError`, consider using `adk web --no-reload` instead.


Once the ADK Web UI loads in your browser:

1.  Select the `filesystem_assistant_agent` from the agent dropdown.
2.  Try prompts like:
    *   "List files in the current directory."
    *   "Can you read the file named sample.txt?" (assuming you created it in `TARGET_FOLDER_PATH`).
    *   "What is the content of `another_file.md`?"

You should see the agent interacting with the MCP file system server, and the server's responses (file listings, file content) relayed through the agent. The `adk web` console (terminal where you ran the command) might also show logs from the `npx` process if it outputs to stderr.

![MCP with ADK Web - FileSystem Example](../assets/adk-tool-mcp-filesystem-adk-web-demo.png)

For Java, refer to the following sample to define an agent that initializes the `McpToolset`:

```java
--8<-- "examples/inline/java/tools-custom/mcp-tools/003-step-3-run-adk-web-and-interact.java"
```

Assuming a folder containing three files named `first`, `second` and `third`, successful response will look like this:

```shell
Event received: {"id":"163a449e-691a-48a2-9e38-8cadb6d1f136","invocationId":"e-c2458c56-e57a-45b2-97de-ae7292e505ef","author":"enterprise_assistant","content":{"parts":[{"functionCall":{"id":"adk-388b4ac2-d40e-4f6a-bda6-f051110c6498","args":{"path":"~/home-test"},"name":"list_directory"}}],"role":"model"},"actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"timestamp":1747377543788}

Event received: {"id":"8728380b-bfad-4d14-8421-fa98d09364f1","invocationId":"e-c2458c56-e57a-45b2-97de-ae7292e505ef","author":"enterprise_assistant","content":{"parts":[{"functionResponse":{"id":"adk-388b4ac2-d40e-4f6a-bda6-f051110c6498","name":"list_directory","response":{"text_output":[{"text":"[FILE] first\n[FILE] second\n[FILE] third"}]}}}],"role":"user"},"actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"timestamp":1747377544679}

Event received: {"id":"8fe7e594-3e47-4254-8b57-9106ad8463cb","invocationId":"e-c2458c56-e57a-45b2-97de-ae7292e505ef","author":"enterprise_assistant","content":{"parts":[{"text":"There are three files in the directory: first, second, and third."}],"role":"model"},"actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"timestamp":1747377544689}
```

For TypeScript, you can define an agent that initializes the `MCPToolset` as follows:

```typescript
--8<-- "examples/inline/typescript/tools-custom/mcp-tools/004-step-3-run-adk-web-and-interact.ts"
```



### Example 2: Google Maps Grounding Lite MCP Server

[Google Maps Platform Grounding Lite](https://developers.google.com/maps/ai/grounding-lite) is a service with Model Context Protocol (MCP) support that makes it easy to ground your AI applications with trusted geospatial data from Google Maps. The MCP server provides tools that allow LLMs to access capabilities for places, weather, and routes. You can try out Grounding Lite by enabling it in any tool that supports MCP servers.

Grounding Lite provides tools that allow LLMs to access the following Google Maps capabilities:

* **Search places:** Request information about places and get AI-generated place data summaries, as well as Place IDs, latitude and longitude coordinates, and Google Maps links for each of the places included in the summary. You can use the returned Place IDs and latitude and longitude coordinates with other Google Maps Platform APIs to show places on a map.
* **Lookup weather:** Request information about weather and return current conditions, hourly forecasts, and daily forecasts.
* **Compute routes:** Request information about driving or walking routes between two locations and return route distance and duration information.

#### Step 1: Enable the Maps Grounding Lite service on your Google Cloud project

1. [Set up your Google Cloud project](https://developers.google.com/maps/get-started#create-project) if you haven’t got one.
2. In the [Google Cloud Console](https://console.developers.google.com), choose the project you want to use for Grounding Lite.
3. Enable Grounding Lite in the [Google Cloud Console API Library](https://console.developers.google.com/apis/library/mapstools.googleapis.com).
4. [Get a Google Maps Platform API Key](https://developers.google.com/maps/get-started#api-key)

#### Step 2: Define your Agent with `McpToolset` for Google Maps Grounding Lite

Modify your `agent.py` file (e.g., in `./adk_agent_samples/mcp_agent/agent.py`). Replace `YOUR_GOOGLE_MAPS_API_KEY` with the actual API key you obtained.

```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/005-step-2-define-your-agent-with-mcptoolset.py"
```

#### Step 3: Ensure `__init__.py` Exists

If you created this in Example 1, you can skip this. Otherwise, ensure you have an `__init__.py` in the `./adk_agent_samples/mcp_agent/` directory:

```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/002-step-2-create-an-init-py-file.py"
```

#### Step 4: Run `adk web` and Interact

1.  **Set Environment Variable (Recommended):**
    Before running `adk web`, it's best to set your Google Maps API key as an environment variable in your terminal:
    ```shell
    export GOOGLE_MAPS_API_KEY="YOUR_ACTUAL_GOOGLE_MAPS_API_KEY"
    ```
    Replace `YOUR_ACTUAL_GOOGLE_MAPS_API_KEY` with your key.

2.  **Run `adk web`**:
    Navigate to the parent directory of `mcp_agent` (e.g., `adk_agent_samples`) and run:
    ```shell
    cd ./adk_agent_samples # Or your equivalent parent directory
    adk web
    ```

3.  **Interact in the UI**:
    *   Select the `travel_planner_agent`.
    *   Try prompts like:
        *   "I will be in San Francisco tomorrow. What’s the weather like?"
        *   "Find coffee shops near Golden Gate Park."
        *   "Get directions from GooglePlex to SFO."

You should see the agent use the Google Maps Grounding Lite MCP tools to provide directions or location-based information.

![Google Maps Grounding Lite MCP with ADK Web Example](../assets/adk-tool-maps-lite-mcp-adk-web-demo.png)

For Java, refer to the following sample to define an agent that initializes the `McpToolset`:

```java
--8<-- "examples/inline/java/tools-custom/mcp-tools/007-step-4-run-adk-web-and-interact.java"
```

For TypeScript, refer to the following sample to define an agent that initializes the `MCPToolset`:

```typescript
--8<-- "examples/inline/typescript/tools-custom/mcp-tools/008-step-4-run-adk-web-and-interact.ts"
```

## 2. Build an MCP server with ADK tools (MCP server exposing ADK)

This pattern allows you to wrap existing ADK tools and make them available to any standard MCP client application. The example in this section exposes the ADK `load_web_page` tool through a custom-built MCP server.

### Summary of steps

You will create a standard Python MCP server application using the `mcp` library. Within this server, you will:

1.  Instantiate the ADK tool(s) you want to expose (e.g., `FunctionTool(load_web_page)`).
2.  Implement the MCP server's `@app.list_tools()` handler to advertise the ADK tool(s). This involves converting the ADK tool definition to the MCP schema using the `adk_to_mcp_tool_type` utility from `google.adk.tools.mcp_tool.conversion_utils`.
3.  Implement the MCP server's `@app.call_tool()` handler. This handler will:
    *   Receive tool call requests from MCP clients.
    *   Identify if the request targets one of your wrapped ADK tools.
    *   Execute the ADK tool's `.run_async()` method.
    *   Format the ADK tool's result into an MCP-compliant response (e.g., `mcp.types.TextContent`).

### Prerequisites

Install the MCP server library in the same Python environment as your ADK installation:

```shell
pip install mcp
```

### Step 1: Create the MCP Server Script

Create a new Python file for your MCP server, for example, `my_adk_mcp_server.py`.

### Step 2: Implement the Server Logic

Add the following code to `my_adk_mcp_server.py`. This script sets up an MCP server that exposes the ADK `load_web_page` tool.

```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/009-step-2-implement-the-server-logic.py"
```

### Step 3: Test your Custom MCP Server with an ADK Agent

Now, create an ADK agent that will act as a client to the MCP server you just built. This ADK agent will use `McpToolset` to connect to your `my_adk_mcp_server.py` script.

Create an `agent.py` (e.g., in `./adk_agent_samples/mcp_client_agent/agent.py`):

```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/010-step-3-test-your-custom-mcp-server-with.py"
```

And an `__init__.py` in the same directory:
```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/011-important-replace-this-with-the-absolute.py"
```

**To run the test:**

1.  **Start your custom MCP server (optional, for separate observation):**
    You can run your `my_adk_mcp_server.py` directly in one terminal to see its logs:
    ```shell
    python3 /path/to/your/my_adk_mcp_server.py
    ```
    It will print "Launching MCP Server..." and wait. The ADK agent (run via `adk web`) will then connect to this process if the `command` in `StdioConnectionParams` is set up to execute it.
    *(Alternatively, `McpToolset` will start this server script as a subprocess automatically when the agent initializes).*

2.  **Run `adk web` for the client agent:**
    Navigate to the parent directory of `mcp_client_agent` (e.g., `adk_agent_samples`) and run:
    ```shell
    cd ./adk_agent_samples # Or your equivalent parent directory
    adk web
    ```

3.  **Interact in the ADK Web UI:**
    *   Select the `web_reader_mcp_client_agent`.
    *   Try a prompt like: "Load the content from https://example.com"

The ADK agent (`web_reader_mcp_client_agent`) will use `McpToolset` to start and connect to your `my_adk_mcp_server.py`. Your MCP server will receive the `call_tool` request, execute the ADK `load_web_page` tool, and return the result. The ADK agent will then relay this information. You should see logs from both the ADK Web UI (and its terminal) and potentially from your `my_adk_mcp_server.py` terminal if you ran it separately.

This example demonstrates how ADK tools can be encapsulated within an MCP server, making them accessible to a broader range of MCP-compliant clients, not just ADK agents.

Refer to the [documentation](https://modelcontextprotocol.io/quickstart/server#core-mcp-concepts), to try it out with Claude Desktop.

## Advanced use cases

The following sections describe how to handle more advanced use cases with MCP Tools in agents.

### Use MCP Tools without `adk web`

This section is relevant to you if:

* You are developing your own Agent using ADK
* And, you are **NOT** using `adk web`,
* And, you are exposing the agent via your own UI


Using MCP Tools requires a different setup than using regular tools, due to the fact that specs for MCP Tools are fetched asynchronously
from the MCP Server running remotely, or in another process.

The following example is modified from the "Example 1: File System MCP Server" example above. The main differences are:

1. Your tool and agent are created asynchronously
2. You need to properly manage the exit stack, so that your agents and tools are destructed properly when the connection to MCP Server is closed.

```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/012-use-mcp-tools-without-adk-web.py"
```

### Handling progress updates

For long-running tools, `McpToolset` supports a `progress_callback`. This approach allows you to receive real-time updates from the MCP server. You can provide a simple callback function or a factory that creates callbacks with access to the runtime context, such as updating session state.

```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/013-handling-progress-updates.py"
```

## Deploy Agents with MCP Tools

When deploying ADK agents that use MCP tools to production environments like Cloud Run, GKE, or Agent Runtime, you need to consider how MCP connections will work in containerized and distributed environments.

### Critical Deployment Requirement: Synchronous Agent Definition

**⚠️ Important:** When deploying agents with MCP tools, the agent and its McpToolset must be defined **synchronously** in your `agent.py` file. While `adk web` allows for asynchronous agent creation, deployment environments require synchronous instantiation.

```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/014-critical-deployment-requirement-synchron.py"
```

```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/015-correct-synchronous-agent-definition-for.py"
```

### Quick Deployment Commands

#### Agent Runtime
```bash
uv run adk deploy agent_engine \
  --project=<your-gcp-project-id> \
  --region=<your-gcp-region> \
  --staging_bucket="gs://<your-gcs-bucket>" \
  --display_name="My MCP Agent" \
  ./path/to/your/agent_directory
```

#### Cloud Run
```bash
uv run adk deploy cloud_run \
  --project=<your-gcp-project-id> \
  --region=<your-gcp-region> \
  --service_name=<your-service-name> \
  ./path/to/your/agent_directory
```

### Deployment Patterns

#### Pattern 1: Self-Contained Stdio MCP Servers

For MCP servers that can be packaged as npm packages or Python modules (like `@modelcontextprotocol/server-filesystem`), you can include them directly in your agent container:

**Container Requirements:**
```dockerfile
# Example for npm-based MCP servers
FROM python:3.13-slim

# Install Node.js and npm for MCP servers
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Install your Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your agent code
COPY . .

# Your agent can now use StdioConnectionParams with 'npx' commands
CMD ["python", "main.py"]
```

**Agent Configuration:**
```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/016-your-agent-can-now-use-stdioconnectionpa.py"
```

#### Pattern 2: Remote MCP Servers (Streamable HTTP)

For production deployments requiring scalability, deploy MCP servers as separate services and connect via Streamable HTTP:

**MCP Server Deployment (Cloud Run):**
```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/017-pattern-2-remote-mcp-servers-streamable.py"
```

**Agent Configuration for Remote MCP:**

=== "Python"

    ```python
    --8<-- "examples/inline/python/tools-custom/mcp-tools/018-deploymcpserver-py-separate-cloud-run-se.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/tools-custom/mcp-tools/019-deploymcpserver-py-separate-cloud-run-se.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/inline/kotlin/tools-custom/mcp-tools/020-deploymcpserver-py-separate-cloud-run-se.kt"
    ```

#### Pattern 3: Sidecar MCP Servers (GKE)

In Kubernetes environments, you can deploy MCP servers as sidecar containers:

```yaml
# deployment.yaml - GKE with MCP sidecar
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent-with-mcp
spec:
  template:
    spec:
      containers:
      # Main ADK agent container
      - name: adk-agent
        image: your-adk-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: MCP_SERVER_URL
          value: "http://localhost:8081"

      # MCP server sidecar
      - name: mcp-server
        image: your-mcp-server:latest
        ports:
        - containerPort: 8081
```

### Connection Management Considerations

#### Stdio Connections
- **Pros:** Simple setup, process isolation, works well in containers
- **Cons:** Process overhead, not suitable for high-scale deployments
- **Best for:** Development, single-tenant deployments, simple MCP servers

#### SSE/HTTP Connections
- **Pros:** Network-based, scalable, can handle multiple clients
- **Cons:** Requires network infrastructure, authentication complexity
- **Best for:** Production deployments, multi-tenant systems, external MCP services

### Production Deployment Checklist

When deploying agents with MCP tools to production:

**✅ Connection Lifecycle**
- Ensure proper cleanup of MCP connections using exit_stack patterns
- Configure appropriate timeouts for connection establishment and requests
- Implement retry logic for transient connection failures

**✅ Resource Management**
- Monitor memory usage for stdio MCP servers (each spawns a process)
- Configure appropriate CPU/memory limits for MCP server processes
- Consider connection pooling for remote MCP servers

**✅ Security**
- Use authentication headers for remote MCP connections
- Restrict network access between ADK agents and MCP servers
- **Filter MCP tools using `tool_filter` to limit exposed functionality**
- Validate MCP tool inputs to prevent injection attacks
- Use restrictive file paths for filesystem MCP servers (e.g., `os.path.dirname(os.path.abspath(__file__))`)
- Consider read-only tool filters for production environments

**✅ Monitoring & Observability**
- Log MCP connection establishment and teardown events
- Monitor MCP tool execution times and success rates
- Set up alerts for MCP connection failures

**✅ Scalability**
- For high-volume deployments, prefer remote MCP servers over stdio
- Configure session affinity if using stateful MCP servers
- Consider MCP server connection limits and implement circuit breakers

### Environment-Specific Configurations

#### Cloud Run
```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/021-cloud-run.py"
```

#### GKE
```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/022-gke.py"
```

#### Agent Runtime
```python
--8<-- "examples/inline/python/tools-custom/mcp-tools/023-agent-runtime.py"
```

### Troubleshooting Deployment Issues

**Common MCP Deployment Problems:**

1. **Stdio Process Startup Failures**
   ```python
   --8<-- "examples/inline/python/tools-custom/mcp-tools/024-troubleshooting-deployment-issues.py"
   ```

2. **Network Connectivity Issues**
   ```python
   --8<-- "examples/inline/python/tools-custom/mcp-tools/025-debug-stdio-connection-issues.py"
   ```

3. **Resource Exhaustion**
   - Monitor container memory usage when using stdio MCP servers
   - Set appropriate limits in Kubernetes deployments
   - Use remote MCP servers for resource-intensive operations

## Further Resources

* [Model Context Protocol Documentation](https://modelcontextprotocol.io/ )
* [MCP Specification](https://modelcontextprotocol.io/specification/)
* [MCP Python SDK & Examples](https://github.com/modelcontextprotocol/)
