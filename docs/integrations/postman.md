---
catalog_title: Postman
catalog_description: Manage API collections, workspaces, and generate client code
catalog_icon: /integrations/assets/postman.png
catalog_tags: ["mcp"]
---

# Postman MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Postman MCP Server](https://github.com/postmanlabs/postman-mcp-server)
connects your ADK agent to the [Postman](https://www.postman.com/) ecosystem.
This integration gives your agent the ability to access workspaces, manage
collections and environments, evaluate APIs, and automate workflows through
natural language interactions.

## Use cases

- **API testing**: Continuously test your APIs using your Postman collections.

- **Collection management**: Create and tag collections, update documentation,
  add comments, or perform actions across multiple collections without leaving
  your editor.

- **Workspace and environment management**: Create workspaces and environments,
  and manage your environment variables.

- **Client code generation**: Generate production-ready client code that
  consumes APIs following best practices and project conventions.

## Prerequisites

- Create a [Postman account](https://identity.getpostman.com/signup)
- Generate a [Postman API key](https://postman.postman.co/settings/me/api-keys)

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        --8<-- "examples/inline/python/integrations/postman/001-use-with-agent.py"
        ```

    === "Remote MCP Server"

        ```python
        --8<-- "examples/inline/python/integrations/postman/002-use-with-agent.py"
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        --8<-- "examples/inline/typescript/integrations/postman/003-use-with-agent.ts"
        ```

    === "Remote MCP Server"

        ```typescript
        --8<-- "examples/inline/typescript/integrations/postman/004-use-with-agent.ts"
        ```

## Configuration

Postman offers three tool configurations:

- **Minimal** (default): Essential tools for basic Postman operations. Best for
  simple modifications to collections, workspaces, or environments.
- **Full**: All available Postman API tools (100+ tools). Ideal for advanced
  collaboration and enterprise features.
- **Code**: Tools for searching API definitions and generating client code.
  Perfect for developers who need to consume APIs.

To select a configuration:

- **Local server**: Add `--full` or `--code` to the `args` list.
- **Remote server**: Change the URL path to `/minimal`, `/mcp` (full), or `/code`.

For EU region, use `--region eu` (local) or `https://mcp.eu.postman.com` (remote).

## Additional resources

- [Postman MCP Server on GitHub](https://github.com/postmanlabs/postman-mcp-server)
- [Postman API key settings](https://postman.postman.co/settings/me/api-keys)
- [Postman Learning Center](https://learning.postman.com/)
