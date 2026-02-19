# Model Context Protocol (MCP)

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

The
[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is
an open standard designed to standardize how Large Language Models (LLMs) like
Gemini and Claude communicate with external applications, data sources, and
tools. Think of it as a universal connection mechanism that simplifies how LLMs
obtain context, execute actions, and interact with various systems.

!!! tip "MCP tools for ADK"
    For a list of pre-built MCP tools for ADK, see
    [Tools and Integrations](/adk-docs/integrations/?topic=mcp).

## How does MCP work?

MCP follows a client-server architecture, defining how data (resources),
interactive templates (prompts), and actionable functions (tools) are
exposed by an MCP server and consumed by an MCP client (which could be
an LLM host application or an AI agent).

## MCP Tools in ADK

ADK helps you both use and consume MCP tools in your agents, whether you're
trying to build a tool to call an MCP service, or exposing an MCP server for
other developers or agents to interact with your tools.

See [Tools and Integrations](/adk-docs/integrations/) for pre-built
MCP tools you can use in your agents. Refer to the
[MCP Tools documentation](/adk-docs/tools-custom/mcp-tools/) for code samples
and design patterns that help you use ADK together with MCP servers, including:

- **Using Existing MCP Servers within ADK**: An ADK agent can act as an MCP
  client and use tools provided by external MCP servers.
- **Exposing ADK Tools via an MCP Server**: How to build an MCP server that
  wraps ADK tools, making them accessible to any MCP client.

## ADK Agent and FastMCP server
ADK uses [FastMCP](https://github.com/jlowin/fastmcp) to handle all the
complex MCP protocol details and server management, so you can focus on
building great tools. It's designed to be high-level and Pythonic; in most
cases, decorating a function is all you need.

Refer to the [MCP Tools](/adk-docs/tools-custom/mcp-tools/) documentation on
how you can use ADK together with the FastMCP server running on Cloud Run.

## MCP Servers for Google Cloud Genmedia

[MCP Tools for Genmedia Services](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia)
is a set of open-source MCP servers that enable you to integrate Google Cloud
generative media services—such as Imagen, Veo, Chirp 3 HD voices, and Lyria—into
your AI applications.

Agent Development Kit (ADK) and [Genkit](https://genkit.dev/) provide built-in
support for these MCP tools, allowing your AI agents to effectively orchestrate
generative media workflows. For implementation guidance, refer to the [ADK
example
agent](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/adk)
and the
[Genkit example](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/genkit).