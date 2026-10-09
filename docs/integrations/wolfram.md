---
catalog_title: Wolfram
catalog_description: Inject precise, real-time computation and knowledge
catalog_icon: /integrations/assets/wolfram.svg
catalog_tags: ["data", "mcp"]
---

# Wolfram MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Wolfram MCP Server](https://www.wolfram.com/artificial-intelligence/mcp-service/)
transforms your AI environment into a rigorous computational powerhouse. By
integrating [Wolfram Language](https://www.wolfram.com/language/) and
[Wolfram|Alpha](https://www.wolframalpha.com/), this server provides access to
curated data and sophisticated algorithms. When a user submits a query, the LLM
works with Wolfram to convert it into Wolfram Language for precise evaluation,
and these exact results are incorporated into the response provided by the LLM.

Whether you are solving complex differential equations, analyzing chemical
structures or querying real-time socioeconomic data, the MCP Server ensures
your AI has the "computational brain" necessary to deliver verified, high-level
technical results that can be trusted.

## Use cases

- Solving complex differential equations
- Analyzing chemical structures
- Querying real-time socioeconomic data

## Prerequisites

- No special requirements
- No auth needed

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="wolfram_agent",
            instruction="Use Wolfram tools for computation and knowledge queries.",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://agenttools.wolfram.com/mcp",
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "wolfram_agent",
            instruction: "Use Wolfram tools for computation and knowledge queries.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://agenttools.wolfram.com/mcp",
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

Tool | Description
---- | -----------
`WolframContext` | Uses semantic search to retrieve any relevant information from Wolfram
`WolframLanguageEvaluator` | Evaluates Wolfram Language code for the user in a Wolfram Language kernel
`WolframAlpha` | Use natural language queries with Wolfram\|Alpha to get up-to-date computational results about entities in chemistry, physics, geography, history, art, astronomy, and more

These are documented in
[Wolfram/AgentTools/tutorial/DefaultTools](https://reference.wolfram.com/language/Wolfram/AgentTools/tutorial/DefaultTools.html).

## Additional resources

- [Wolfram MCP Service Documentation](https://www.wolfram.com/artificial-intelligence/mcp-service/)
- [Wolfram AgentTools Repository](https://github.com/WolframResearch/AgentTools)
- [Wolfram Support](https://support.wolfram.com/)
