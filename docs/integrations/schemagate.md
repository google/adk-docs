---
catalog_title: schemagate
catalog_description: Give text-to-SQL agents only the tables each user may read
catalog_icon: /integrations/assets/schemagate.png
catalog_tags: ["data", "mcp"]
---

# schemagate MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [schemagate MCP Server](https://github.com/ashishsinha1602/schemagate)
connects your ADK agent to a SQL database for text-to-SQL. For each question it
returns the definitions of only the tables the question needs, chosen from the
tables the signed-in user may read. A table the user cannot read is left out of
the result entirely, and `run_query` refuses any query that names one. It works
with PostgreSQL, MySQL, SQL Server, Oracle and SQLite, and the selection runs
locally without a model call.

## Use cases

- **Text-to-SQL on large schemas**: Send the model the few tables a question
  needs instead of the whole schema. On Spider 2.0's warehouses with 50+
  tables, the median prompt is 91% smaller.
- **Per-user data access**: Hide tables and columns by role, from a policy file
  or from the database's own grants, so one agent can serve users with
  different permissions.
- **Safe query execution**: Run read-only queries that are checked against the
  same permissions before they reach the database.

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/), which provides
  the `uvx` command used below
- A SQLAlchemy database URL, such as `postgresql+psycopg://user:pass@host/db`.
  To try it first, use `demo`, a bundled sample schema that needs no database.

## Use with agent

The server takes the caller's identity in each tool call as `principal` and
`roles`. Set them from your app, not from the model: the `before_tool_callback`
below overwrites whatever the model passed with the signed-in user's identity,
which your app stores in session state.

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        # "demo" is a bundled sample schema. For your own database, pass its
        # SQLAlchemy URL in the SCHEMAGATE_DATABASE_URL environment variable.
        DATABASE_URL = "demo"


        def pin_caller(tool, args, tool_context):
            """Every schemagate call runs as the signed-in user, whatever the model passed."""
            args["principal"] = tool_context.state["principal"]  # for example "okta:jdoe"
            args["roles"] = tool_context.state["roles"]          # for example ["finance"]
            return None


        root_agent = Agent(
            model="gemini-flash-latest",
            name="schemagate_agent",
            instruction="Answer questions about the database. Call select_schema first and use only the tables it returns.",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["--from", "schemagate[mcp]", "schemagate-mcp", "--url", DATABASE_URL],
                        ),
                        timeout=60,
                    ),
                    tool_filter=["select_schema", "list_objects", "describe_object", "run_query"],
                )
            ],
            before_tool_callback=pin_caller,
        )
        ```

Create each session with the user's identity in its state, for example
`state={"principal": "okta:jdoe", "roles": ["finance"]}`. In the demo schema,
`hr_compensation` is restricted to the `payroll` role: an agent running for
`["finance"]` never sees it, even if the model asks for `payroll`.

For a real database, add its driver as an extra, for example
`schemagate[mcp,postgres]`, and pass the URL through the environment rather
than the command line:

```python
server_params=StdioServerParameters(
    command="uvx",
    args=["--from", "schemagate[mcp,postgres]", "schemagate-mcp"],
    env={"SCHEMAGATE_DATABASE_URL": "postgresql+psycopg://user:pass@host/db"},
)
```

## Configuration

Variable | Description
-------- | -----------
`SCHEMAGATE_DATABASE_URL` | SQLAlchemy URL of the database to serve
`SCHEMAGATE_CATALOG_CONFIG` | JSON file with role restrictions and table hints, for example `{"restrict": {"hr_compensation": ["payroll"]}}`
`SCHEMAGATE_RESTRICT_FROM_GRANTS` | Set to `1` to also read restrictions from the database's own grants, which take precedence over the file

## Available tools

Tool | Description
---- | -----------
`select_schema` | Table definitions for a question, limited to what the caller may read
`list_objects` | Tables and views the caller may read
`describe_object` | Full definition of one table or view
`run_query` | Run one read-only query, refused if it names anything the caller may not read
`semantic_query` | Run a query, then have the server's model filter or annotate rows by what a text column says (needs a model configured on the server)
`answer` | Answer a question end to end on the server (needs a model configured on the server)
`deep_answer` | Like `answer`, exploring in steps when a plain query is not enough (needs a model configured on the server)
`refresh_catalog` | Re-read the database schema
`health` | Server status

The example above enables the four tools that need no model on the server.

## Additional resources

- [schemagate Repository](https://github.com/ashishsinha1602/schemagate)
- [schemagate on PyPI](https://pypi.org/project/schemagate/)
- [Benchmarks](https://github.com/ashishsinha1602/schemagate/blob/main/BENCHMARKS.md)
- [schemagate LangChain retriever](https://pypi.org/project/langchain-schemagate/)
