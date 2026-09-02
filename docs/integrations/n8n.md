---
catalog_title: n8n
catalog_description: Trigger automated workflows, connect apps, and process data
catalog_icon: /integrations/assets/n8n.png
catalog_tags: ["mcp", "connectors"]
---

# n8n MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [n8n MCP
Server](https://docs.n8n.io/advanced-ai/mcp/accessing-n8n-mcp-server/) connects
your ADK agent to [n8n](https://n8n.io/), an extendable workflow automation
tool. This integration allows your agent to securely connect to an n8n instance
to search, inspect, and trigger workflows directly from a natural language
interface.

!!! note "Alternative: Workflow-level MCP Server"

    The configuration guide on this page covers **Instance-level MCP access**,
    which connects your agent to a central hub of enabled workflows.
    Alternatively, you can use the
    [MCP Server Trigger node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/)
    to make a **single workflow** act as its own standalone MCP server. This
    method is useful if you want to craft specific server behaviors or expose
    tools isolated to one workflow.

## Use cases

- **Execute Complex Workflows**: Trigger multi-step business processes defined
  in n8n directly from your agent, leveraging reliable branching logic, loops,
  and error handling to ensure consistency.

- **Connect to External Apps**: Access pre-built integrations through n8n
  without writing custom tools for each service, eliminating the need to manage
  API authentication, headers, or boilerplate code.

- **Data Processing**: Offload complex data transformation tasks to n8n
  workflows, such as converting natural language into API calls or scraping and
  summarizing webpages, utilizing custom Python or JavaScript nodes for precise
  data shaping.

## Prerequisites

- An active n8n instance
- MCP access enabled in settings
- A valid MCP access token

Refer to the [n8n MCP
documentation](https://docs.n8n.io/advanced-ai/mcp/accessing-n8n-mcp-server/)
for detailed setup instructions.

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        --8<-- "examples/inline/python/integrations/n8n/001-use-with-agent.py"
        ```

    === "Remote MCP Server"

        ```python
        --8<-- "examples/inline/python/integrations/n8n/002-use-with-agent.py"
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        --8<-- "examples/inline/typescript/integrations/n8n/003-use-with-agent.ts"
        ```

    === "Remote MCP Server"

        ```typescript
        --8<-- "examples/inline/typescript/integrations/n8n/004-use-with-agent.ts"
        ```

## Available tools

Tool | Description
---- | -----------
`search_workflows` | Search for available workflows
`execute_workflow` | Execute a specific workflow
`get_workflow_details` | Retrieve metadata and schema information for a workflow

## Configuration

To make workflows accessible to your agent, they must meet the following
criteria:

- **Be Active**: The workflow must be activated in n8n.

- **Supported Trigger**: Contain a Webhook, Schedule, Chat, or Form trigger
  node.

- **Enabled for MCP**: You must toggle "Available in MCP" in the workflow
  settings or select "Enable MCP access" from the workflow card menu.

## Additional resources

- [n8n MCP Server Documentation](https://docs.n8n.io/advanced-ai/mcp/accessing-n8n-mcp-server/)
