---
catalog_title: OnlineCompiler.io
catalog_description: Run code in 46 languages and check it against test cases
catalog_icon: /integrations/assets/onlinecompiler.png
catalog_tags: ["code", "mcp"]
---

# OnlineCompiler.io MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [OnlineCompiler.io MCP server](https://github.com/onlinecompiler-io/onlinecompiler-mcp)
gives your ADK agent tools to run programs in 46 languages and to check them
against test cases. Each program runs on OnlineCompiler.io in a new gVisor
sandbox with no network access, so code that the agent writes does not run on
the machine where the agent runs. You can connect to the hosted server over
Streamable HTTP, or start the same server locally over stdio from PyPI.

## Use cases

- **Check generated code**: Let the agent run the code it writes and read the
  output, errors, exit code, time and memory before it answers.
- **Grade solutions**: Run a program against test cases (an input and the
  expected output for each) and get a verdict for every test and a score, for
  tutoring and assessment agents.
- **Work across languages**: Run Python, Java, C++, Go, Rust, SQL and other
  languages without installing compilers where the agent runs.

## Prerequisites

- An OnlineCompiler.io API key. Create one on the
  [API keys page](https://api.onlinecompiler.io/compilers/api-keys/) after
  signing in; the free plan needs no card.
- ADK with MCP support: `pip install "google-adk[mcp]"` for Python, or
  `npm install @google/adk @modelcontextprotocol/sdk` for TypeScript.
- For the local server only: [uv](https://docs.astral.sh/uv/), which provides
  the `uvx` command.

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        ONLINECOMPILER_API_KEY = "YOUR_ONLINECOMPILER_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="onlinecompiler_agent",
            instruction="Run code with OnlineCompiler.io to check your answers",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.onlinecompiler.io/mcp",
                        headers={
                            "Authorization": f"Bearer {ONLINECOMPILER_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        ONLINECOMPILER_API_KEY = "YOUR_ONLINECOMPILER_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="onlinecompiler_agent",
            instruction="Run code with OnlineCompiler.io to check your answers",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["onlinecompiler-mcp", "--transport", "stdio"],
                            env={
                                "ONLINECOMPILER_API_KEY": ONLINECOMPILER_API_KEY,
                            },
                        ),
                        timeout=60,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const ONLINECOMPILER_API_KEY = "YOUR_ONLINECOMPILER_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "onlinecompiler_agent",
            instruction: "Run code with OnlineCompiler.io to check your answers",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://api.onlinecompiler.io/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${ONLINECOMPILER_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const ONLINECOMPILER_API_KEY = "YOUR_ONLINECOMPILER_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "onlinecompiler_agent",
            instruction: "Run code with OnlineCompiler.io to check your answers",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["onlinecompiler-mcp", "--transport", "stdio"],
                        env: {
                            ONLINECOMPILER_API_KEY: ONLINECOMPILER_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

Tool | Description
---- | -----------
`list_compilers` | List the compiler ids (languages and versions) that the other tools accept
`run_code` | Run one program with optional standard input and return its output, errors, exit code, time and memory
`run_tests` | Run one program against up to 10 test cases and return a verdict for each test, an overall verdict and a score
`judge_problem` | Judge a program against a problem stored in your OnlineCompiler.io account and return a verdict, a score and a signed receipt

## Additional resources

- [OnlineCompiler.io MCP server documentation](https://onlinecompiler.io/mcp-code-execution)
- [OnlineCompiler.io MCP server repository](https://github.com/onlinecompiler-io/onlinecompiler-mcp)
- [onlinecompiler-mcp on PyPI](https://pypi.org/project/onlinecompiler-mcp/)
- [OnlineCompiler.io API documentation](https://onlinecompiler.io/docs)
