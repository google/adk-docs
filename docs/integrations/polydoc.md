---
catalog_title: "Polydoc"
catalog_description: "Automatically generate comprehensive database documentation from your codebase for AI agents"
catalog_icon: "/adk-docs/integrations/assets/polydoc.png"
catalog_tags:
  - "database"
  - "mcp"
---

# Polydoc

<div class="language-support">
  <span class="language-badge">Python</span>
  <span class="language-badge">TypeScript</span>
</div>

Polydoc is an MCP server that automatically scans your codebase to generate comprehensive database documentation from models, entities, migrations, and schema files. It supports TypeORM, Sequelize, Prisma, SQL migrations, and Active Record, enabling AI agents to understand your database schema for query generation and data operations.

## Use cases

- **Query generation assistance**: AI agents can generate accurate SQL queries by understanding your database schema, table relationships, and column types.
- **Schema understanding**: Agents can answer questions about your database structure, explain relationships between tables, and identify available data fields.
- **Data operation planning**: Agents can plan complex data operations by understanding constraints, indexes, and relationships defined in your models.
- **Migration analysis**: Agents can review migration files to understand schema evolution and suggest compatible changes.

## Prerequisites

- Node.js 18 or higher
- A codebase using TypeORM, Sequelize, Prisma, SQL migrations, or Active Record

## Installation

Polydoc can be run directly with npx without installation:

```bash
npx polydoc-mcp-server
```

Or install globally:

```bash
npm install -g polydoc-mcp-server
```

## Use with agent

=== "Python"
    ```python
    from google.genai.adk import Agent
    from google.genai.adk.mcp import RemoteMCPServer

    # Create MCP server connection
    polydoc_server = RemoteMCPServer(
        command="npx",
        args=["polydoc-mcp-server"],
        env={"WORKSPACE_PATH": "/path/to/your/codebase"}
    )

    # Create agent with Polydoc tools
    agent = Agent(
        model="gemini-2.0-flash-exp",
        mcp_servers=[polydoc_server]
    )

    # Use the agent
    try:
        response = agent.generate_content(
            "What tables are in my database and how are they related?"
        )
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")
    ```

=== "TypeScript"
    ```typescript
    import { Agent } from '@google/genai-adk';
    import { RemoteMCPServer } from '@google/genai-adk/mcp';

    // Create MCP server connection
    const polydocServer = new RemoteMCPServer({
      command: 'npx',
      args: ['polydoc-mcp-server'],
      env: { WORKSPACE_PATH: '/path/to/your/codebase' }
    });

    // Create agent with Polydoc tools
    const agent = new Agent({
      model: 'gemini-2.0-flash-exp',
      mcpServers: [polydocServer]
    });

    // Use the agent
    try {
      const response = await agent.generateContent(
        'What tables are in my database and how are they related?'
      );
      console.log(response.text);
    } catch (error) {
      console.error(`Error: ${error}`);
    }
    ```

## Available tools

| Tool | Description |
|------|-------------|
| `build-database-documentation` | Scans the workspace and generates comprehensive database documentation including tables, columns, relationships, and constraints |
| `scan-database-files` | Lists all detected database-related files in the workspace (models, migrations, schemas) |
| `debug-workspace-info` | Returns workspace path and configuration information for troubleshooting |
| `debug-client-capabilities` | Returns MCP client capabilities for debugging connection issues |

## Configuration

Polydoc accepts the following environment variables:

- `WORKSPACE_PATH`: Path to the codebase to scan (required)
- `INCLUDE_PATTERNS`: Comma-separated glob patterns for files to include (optional)
- `EXCLUDE_PATTERNS`: Comma-separated glob patterns for files to exclude (optional)

## Additional resources

- [Polydoc GitHub Repository](https://github.com/polygraphe/polydoc-mcp)
- [Polydoc on npm](https://www.npmjs.com/package/polydoc-mcp-server)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
