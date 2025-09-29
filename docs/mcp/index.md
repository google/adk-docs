# Model Context Protocol (MCP)

## What is Model Context Protocol (MCP)?

The
[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is
an open standard designed to standardize how Large Language Models (LLMs) like
Gemini and Claude communicate with external applications, data sources, and
tools. Think of it as a universal connection mechanism that simplifies how LLMs
obtain context, execute actions, and interact with various systems.

## How does MCP work?

MCP follows a client-server architecture, defining how data (resources),
interactive templates (prompts), and actionable functions (tools) are
exposed by an MCP server and consumed by an MCP client (which could be
an LLM host application or an AI agent).

## MCP Tools in ADK

ADK helps you both use and consume MCP tools in your agents, whether you're
trying to build a tool to call an MCP service, or exposing an MCP server for
other developers or agents to interact with your tools.

Refer to the [MCP Tools documentation](../tools/mcp-tools.md) for code samples
and design patterns that help you use ADK together with MCP servers, including:

- **Using Existing MCP Servers within ADK**: An ADK agent can act as an MCP
  client and use tools provided by external MCP servers.
- **Exposing ADK Tools via an MCP Server**: How to build an MCP server that
  wraps ADK tools, making them accessible to any MCP client.

## MCP Toolbox for Databases

[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) is an
open-source MCP server that securely exposes your backend data sources as a
set of pre-built, production-ready tools for Gen AI agents. It functions as a
universal abstraction layer, allowing your ADK agent to securely query, analyze,
and retrieve information from a wide array of databases with built-in support.

The MCP Toolbox server includes a comprehensive library of connectors, ensuring that
agents can safely interact with your complex data estate.

### Supported Data Sources

MCP Toolbox provides out-of-the-box toolsets for the following databases and data platforms:

#### Google Cloud

* BigQuery (including tools for SQL execution, schema discovery, and AI-powered time series forecasting)
* AlloyDB (PostgreSQL-compatible, with tools for both standard queries and natural language queries)
* Spanner (supporting both GoogleSQL and PostgreSQL dialects)
* Cloud SQL (with dedicated support for Cloud SQL for PostgreSQL, Cloud SQL for MySQL, and Cloud SQL for SQL Server)
* Firestore
* Bigtable
* Dataplex (for data discovery and metadata search)

#### Relational & SQL Databases

* PostgreSQL (generic)
* MySQL (generic)
* Microsoft SQL Server (generic)
* ClickHouse
* TiDB
* OceanBase
* Firebird
* SQLite

#### NoSQL & Key-Value Stores
* MongoDB
* Couchbase
* Redis
* Valkey

#### Graph Databases

* Neo4j (with tools for Cypher queries and schema inspection)
* Dgraph

#### Data Platforms & Federation

* Looker (for running Looks, queries, and building dashboards via the Looker API)
* Trino (for running federated queries across multiple sources)

### Documentation

Refer to the
[MCP Toolbox for Databases](../tools/google-cloud-tools.md#toolbox-tools-for-databases)
documentation on how you can use ADK together with the MCP Toolbox for
Databases. For getting started with the MCP Toolbox for Databases, a blog post [Tutorial : MCP Toolbox for Databases - Exposing Big Query Datasets](https://medium.com/google-cloud/tutorial-mcp-toolbox-for-databases-exposing-big-query-datasets-9321f0064f4e) and Codelab [MCP Toolbox for Databases:Making BigQuery datasets available to MCP clients](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en#0) are also available.

![GenAI Toolbox](../assets/mcp_db_toolbox.png)

## ADK Agent and FastMCP server
[FastMCP](https://github.com/jlowin/fastmcp) handles all the complex MCP protocol details and server management, so you can focus on building great tools. It's designed to be high-level and Pythonic; in most cases, decorating a function is all you need.

Refer to the [MCP Tools documentation](../tools/mcp-tools.md) documentation on
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