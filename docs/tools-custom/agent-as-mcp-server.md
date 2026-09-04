# Agent-Exposed MCP Server (`to_mcp_server`)

You can make your ADK capabilities accessible to external MCP clients (such as 
Claude Desktop, IDEs, or custom hosts) by building an MCP server that exposes 
ADK constructs. There are two primary ways to achieve this:

* **Expose an entire Agent:** Wraps the full multi-turn agent reasoning and 
  internal tool execution into a server using a simple one-line conversion.

* **Expose individual Tools:** Involves manually building a lightweight MCP 
  server to wrap specific, standalone ADK tools (like a `FunctionTool`) without 
  the agent's reasoning loop.

## Expose an Entire ADK Agent
The most powerful approach is to expose an entire `LlmAgent`. By using the 
`to_mcp_server()` utility, you can convert your agent into a standard FastMCP 
server. This allows external clients to interact with the agent's full cognitive 
capabilities and its internal toolkit.

```python
from google.adk.agents import LlmAgent
from google.adk.tools.load_web_page import load_web_page
from google.adk.tools.mcp_tool import to_mcp_server

# 1. Define your ADK agent
agent = LlmAgent(
    model="gemini-flash-latest", 
    name="web_reader_agent", 
    instruction="Fetch and summarize web content for the user.", 
    tools=[load_web_page], 
)

# 2. Convert the agent into an MCP server
app = to_mcp_server(agent)

if __name__ == "__main__":
    # Runs the agent as a standard stdio MCP server
    app.run()
```

## Expose individual ADK Tools
If you only want to expose individual capabilities (like a specific `FunctionTool`) 
without the full agent reasoning loop, you must manually build an MCP server.

**Prerequisites:**
You must install the MCP Server library in your ADK environment:
```bash
pip install mcp
```

**Implementation Steps:**

1. **Initialize the Tool:** Instantiate the ADK tool you want to expose, such as:
   `FunctionTool(load_web_page)`.
2. **List Tools Handler:** Implement the MCP server's `@app.list_tools()` 
   handler to advertise the tool. You use the `adk_to_mcp_tool_type` utility 
   from `google.adk.tools.mcp_tool.conversion_utils` to convert the ADK tool 
   definition into the MCP schema format.
3. **Call Tool Handler:** Implement the `@app.call_tool()` handler to receive 
   client requests. This handler must identify if the request matches your 
   wrapped tool, execute the ADK tool's `.run_async()` method (passing 
   `tool_context=None`), and format the response into an MCP-compliant 
   structure, for example `mcp.types.TextContent`.

## Build the MCP server with ADK tools

1. Create a new Python file for your MCP server, for example: `my_adk_mcp_server.py`.
2. Implement server logic with the following code to your new file. This following script sets up an MCP server that exposes the ADK `load_web_page` tool.

```python
import asyncio
import json
import os
from dotenv import load_dotenv

# MCP Server Imports
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio 

# ADK Tool Imports
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.load_web_page import load_web_page 
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

load_dotenv()

# 1. Prepare the ADK Tool
adk_tool_to_expose = FunctionTool(load_web_page)

# 2. Create the MCP Server instance
app = Server("adk-tool-exposing-mcp-server")

# 3. Implement the list_tools handler
@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_to_expose)
    return [mcp_tool_schema]

# 4. Implement the call_tool handler
@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    if name == adk_tool_to_expose.name:
        try:
            # Execute the ADK tool
            adk_tool_response = await adk_tool_to_expose.run_async(
                args=arguments, 
                tool_context=None,
            )
            # Format into MCP TextContent
            response_text = json.dumps(adk_tool_response, indent=2)
            return [mcp_types.TextContent(type="text", text=response_text)]
        except Exception as e:
            error_text = json.dumps({"error": str(e)})
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        error_text = json.dumps({"error": f"Tool '{name}' not found."})
        return [mcp_types.TextContent(type="text", text=error_text)]

# 5. MCP Server Runner (Stdio)
async def run_mcp_stdio_server():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(run_mcp_stdio_server())
```

## Connection and transport modes
When exposing your ADK capabilities via these MCP servers, you typically run 
them using a standard input/output connection (`mcp.server.stdio`). This connection allows 
the external client application, running as a parent process, to spawn your 
script and communicate with it directly over the stdio streams, keeping 
the connection self-contained and isolated.

## Test your custom MCP server with an ADK Agent

To test your custom server, you need to build an ADK agent that acts as a client. This agent uses the `McpToolset` to establish a connection to the server script you just created.

1. Set up your agent in a new directory such as `./adk_agent_samples/mcp_client_agent/`. Create an `agent.py` file and include an `__init__.py` alongside it to make it discoverable.

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# IMPORTANT: Provide the absolute path to the server script you built previously
MCP_SERVER_SCRIPT = "/path/to/your/my_adk_mcp_server.py"

root_agent = LlmAgent(
    model='gemini-flash-latest',
    name='web_reader_mcp_client_agent',
    instruction="Use the 'load_web_page' tool to fetch content from a URL provided by the user.",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='python3', 
                    args=[MCP_SERVER_SCRIPT], 
                )
            )
        )
    ],
)
```

2. Navigate to your agent's parent directory in the terminal:

```bash
cd ./adk_agent_samples
adk web
```

3. Open the ADK Web UI and select the web_reader_mcp_client_agent.
4. Test the connection with a prompt such as: *Load the content from "https://example.com"*.
