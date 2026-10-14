---
catalog_title: Quilzo
catalog_description: Govern the MCP tools agents call, with approvals and an audit log
catalog_icon: /integrations/assets/quilzo.svg
catalog_tags: ["mcp", "connectors"]
---

# Quilzo MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Quilzo](https://github.com/quilzo/quilzo) is a self-hosted, open-source
(Apache-2.0) control plane for AI agents. Its governed MCP gateway sits between
your ADK agent and your organization's own MCP servers: the agent sees only the
tools a person pinned, each caller has a role and a daily limit, the server's
credential is injected so the agent never holds it, chosen tools wait for a
person to approve each call, and every call is recorded in a signed audit log.

## Use cases

- **Reach internal tools without handing over their credentials**: The agent
  authenticates to Quilzo; Quilzo calls the tool server with its own credential.
- **Ask a person before tools that change things**: Calls to the tools you
  choose wait until somebody other than the caller approves them.
- **Refuse redefined tools**: A tool is callable only while its definition
  (name, description and input schema) is the one a person pinned.
- **Prove what the agent did**: Each call is recorded with a digest of its
  arguments in a hash-chained, signed audit log.

## Prerequisites

- A running [Quilzo](https://quilzo.github.io/install/) installation, with an
  MCP server declared, its tools pinned, and offered through the gateway. See
  [Tools and the MCP gateway](https://quilzo.github.io/integrations/):

    ```bash
    quilzo integrations tools tracker
    quilzo integrations pin tracker list_issues create_issue
    quilzo integrations gateway tracker --role author --daily 200 --ask create_issue
    ```

- A Quilzo token for the person the agent acts for, such as
  `quilzo token issue support-agent --principal dana --role author`.
- The MCP extra for ADK: `pip install "google-adk[mcp]"`.

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        import os

        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="support_agent",
            instruction="Help the support team find and file issues in the tracker.",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://quilzo.example.com/mcp/gateway/tracker",
                        headers={"Authorization": "Bearer " + os.environ["QUILZO_TOKEN"]},
                    ),
                )
            ],
        )
        ```

## Available tools

The gateway offers the tools of the MCP server you put behind it, as you
pinned them. Quilzo's own operations, such as reading and drafting pages, are
offered at `/mcp`:

Tool | Description
---- | -----------
`quilzo_find` | Finds the operation for a task and returns its exact arguments
`quilzo_read` | Runs a read operation, such as reading or searching pages
`quilzo_write` | Changes a draft; never publishes
`quilzo_check` | Runs the checks that gate publishing

## Configuration

A call to a tool offered with `--ask` does not run. The agent receives an MCP
error naming the held call, which the model reads as any other tool error:

```text
a person approves each call of create_issue on tracker. This one is held as gq_a807fa3c488d: call again with the same arguments once they have decided
```

Approved, the same call with the same arguments goes through once, within the
hour.

## Additional resources

- [Quilzo repository](https://github.com/quilzo/quilzo)
- [Using Quilzo with ADK and other agent frameworks](https://quilzo.github.io/frameworks/#adk)
- [Tools and the MCP gateway](https://quilzo.github.io/integrations/)
