# Model Context Protocol Tools

 This guide walks you through two ways of integrating Model Context Protocol (MCP) with ADK.

## What is Model Context Protocol (MCP)?

The Model Context Protocol (MCP) is an open standard designed to standardize how Large Language Models (LLMs) like Gemini and Claude communicate with external applications, data sources, and tools. Think of it as a universal connection mechanism that simplifies how LLMs obtain context, execute actions, and interact with various systems.

MCP follows a client-server architecture, defining how **data** (resources), **interactive templates** (prompts), and **actionable functions** (tools) are exposed by an **MCP server** and consumed by an **MCP client** (which could be an LLM host application or an AI agent).

This guide covers two primary integration patterns:

1. **Using Existing MCP Servers within ADK:** An ADK agent acts as an MCP client, leveraging tools provided by external MCP servers.
2. **Exposing ADK Tools via an MCP Server:** Building an MCP server that wraps ADK tools, making them accessible to any MCP client.

## Prerequisites

Before you begin, ensure you have the following set up:

* **Set up ADK:** Follow the standard ADK [setup instructions](../get-started/quickstart.md/#venv-install) in the quickstart.
* **Install/update Python/Java:** MCP requires Python version of 3.9 or higher for Python or Java 17+.
* **Setup Node.js and npx:** Many community MCP servers are distributed as Node.js packages and run using `npx`. Install Node.js (which includes npx) if you haven't already. For details, see [https://nodejs.org/en](https://nodejs.org/en).
* **Verify Installations:**  Confirm `adk` and `npx` are in your PATH within the activated virtual environment:

```shell
# Both commands should print the path to the executables.
which adk
which npx
```

## 1. Using MCP servers with ADK agents (ADK as an MCP client) in `adk web`

This section demonstrates how to integrate tools from external MCP (Model Context Protocol) servers into your ADK agents. This is the **most common** integration pattern when your ADK agent needs to use capabilities provided by an existing service that exposes an MCP interface. You will see how the `MCPToolset` class can be directly added to your agent's `tools` list, enabling seamless connection to an MCP server, discovery of its tools, and making them available for your agent to use. These examples primarily focus on interactions within the `adk web` development environment.

### `MCPToolset` class

The `MCPToolset` class is ADK's primary mechanism for integrating tools from an MCP server. When you include an `MCPToolset` instance in your agent's `tools` list, it automatically handles the interaction with the specified MCP server. Here's how it works:

1.  **Connection Management:** On initialization, `MCPToolset` establishes and manages the connection to the MCP server. This can be a local server process (using `StdioServerParameters` for communication over standard input/output) or a remote server (using `SseServerParams` for Server-Sent Events). The toolset also handles the graceful shutdown of this connection when the agent or application terminates.
2.  **Tool Discovery & Adaptation:** Once connected, `MCPToolset` queries the MCP server for its available tools (via the `list_tools` MCP method). It then converts the schemas of these discovered MCP tools into ADK-compatible `BaseTool` instances.
3.  **Exposure to Agent:** These adapted tools are then made available to your `LlmAgent` as if they were native ADK tools.
4.  **Proxying Tool Calls:** When your `LlmAgent` decides to use one of these tools, `MCPToolset` transparently proxies the call (using the `call_tool` MCP method) to the MCP server, sends the necessary arguments, and returns the server's response back to the agent.
5.  **Filtering (Optional):** You can use the `tool_filter` parameter when creating an `MCPToolset` to select a specific subset of tools from the MCP server, rather than exposing all of them to your agent.

The following examples demonstrate how to use `MCPToolset` within the `adk web` development environment. For scenarios where you need more fine-grained control over the MCP connection lifecycle or are not using `adk web`, refer to the "Using MCP Tools in your own Agent out of `adk web`" section later in this page.

### Example 1: STDIO MCP Server

This example demonstrates connecting to a local MCP server that provides file system operations.

Create an `McpToolsExample.java` file. The `MCPToolset` is instantiated directly within the `tools` list of your `LlmAgent`.

*   **Important:** Replace `"/path/to/your/folder"` in the `args` list with the **absolute path** to an actual folder on your local system that the MCP server can access.

```java
package com.google.adk.examples;

import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.ToolPredicate;
import com.google.adk.tools.mcp.McpToolset;
import io.modelcontextprotocol.client.transport.ServerParameters;

import java.util.Optional;

public class McpToolsExample {

    /**
     * IMPORTANT: This MUST be an ABSOLUTE path to a folder the
     * npx process can access.
     * Replace with a valid absolute path on your system.
     * For example: "/Users/youruser/accessible_mcp_files"
     * or use a dynamically constructed absolute path:
     */
    private static final String TARGET_FOLDER_PATH = "/path/to/your/folder";

    public static void main(String[] args) {
        ServerParameters serverParameters = ServerParameters.builder("npx")
                .args(
                        "-y", // Argument for npx to auto-confirm install
                        "@modelcontextprotocol/server-filesystem",
                        TARGET_FOLDER_PATH
                )
                .build();
        var tools = new McpToolset(
                serverParameters,
                // Optional: Filter which tools from the MCP server are exposed
                Optional.of((ToolPredicate) (tool, readonlyContext) -> true)
        );
        LlmAgent llmAgent = LlmAgent.builder()
                .name("filesystem_assistant_agent")
                .description("Help the user manage their files. You can list files, read files, etc.")
                .model("gemini-2.5-flash")
                .tools(tools)
                .build();
    }
}

```


### Example 2: SSE MCP Server

This example demonstrates connecting to the SSE MCP server.

Create an `McpToolsExample.java` file. The `MCPToolset` is instantiated directly within the `tools` list of your `LlmAgent`.

```java
package com.google.adk.examples;

import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.ToolPredicate;
import com.google.adk.tools.mcp.McpToolset;
import com.google.adk.tools.mcp.SseServerParameters;

import java.time.Duration;
import java.util.Map;
import java.util.Optional;

public class McpToolsExample {

    public static void main(String[] args) {
        SseServerParameters sseServerParameters = SseServerParameters.builder()
                .url("https://your.sse-mcp.server/sse")
                .headers(Map.of(
                        "Authorization", "Bearer your-mcp-api-key" // Optional: pass headers to you sse server
                ))
                .timeout(Duration.ofSeconds(10L)) // timeout to connect to sse server
                .sseReadTimeout(Duration.ofSeconds(30L)) // timeout to tool call
                .build();
        var tools = new McpToolset(
                sseServerParameters,
                // Optional: Filter which tools from the MCP server are exposed
                Optional.of((ToolPredicate) (tool, readonlyContext) -> true)
        );
        LlmAgent llmAgent = LlmAgent.builder()
                .name("...")
                .description("...")
                .model("gemini-2.5-flash")
                .tools(tools)
                .build();
    }
}

```

## Key considerations

When working with MCP and ADK, keep these points in mind:

* **Protocol vs. Library:** MCP is a protocol specification, defining communication rules. ADK is a Python/Java library/framework for building agents. MCPToolset bridges these by implementing the client side of the MCP protocol within the ADK framework. Conversely, building an MCP server using the model-context-protocol library.
* **ADK Tools vs. MCP Tools:**
    * ADK Tools (BaseTool, FunctionTool, AgentTool, etc.) are Python/Java objects designed for direct use within the ADK's LlmAgent and Runner.
    * MCP Tools are capabilities exposed by an MCP Server according to the protocol's schema. MCPToolset makes these look like ADK tools to an LlmAgent.
    * Langchain/CrewAI Tools are specific implementations within those libraries, often simple functions or classes, lacking the server/protocol structure of MCP. ADK offers wrappers (LangchainTool, CrewaiTool) for some interoperability.

## Further Resources

* [Model Context Protocol Documentation](https://modelcontextprotocol.io/ )
* [MCP Specification](https://modelcontextprotocol.io/specification/)
* [MCP Python SDK & Examples](https://github.com/modelcontextprotocol/)
