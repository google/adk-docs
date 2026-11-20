---
catalog_title: Sanity Context
catalog_description: Give agents the right facts from your content
catalog_icon: /integrations/assets/sanity-context.png
catalog_tags: ["data", "mcp"]
---

# Sanity Context MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Sanity Context](https://www.sanity.io/context) turns your content into
knowledge your AI agents can read, wherever that content lives: a Sanity
dataset, a website you don't manage in Sanity, or a set of files. Agents connect
through a read-only remote MCP server. Each endpoint serves Knowledge Bases, a
live Sanity dataset, or both. A Knowledge Base is an index Sanity Context builds
ahead of time from your sources, and it flags conflicting sources for your team
to resolve. A dataset source lets the agent query documents with GROQ. Your ADK
agent connects to one endpoint and gets the tools for its sources.

## Use cases

- **Answer support questions**: Look up policies, products, and help articles
  so answers match the content your team maintains.

- **Query structured content**: Filter documents by field, follow references,
  and return only the fields the agent needs from a live dataset.

- **Scope agents to content**: Give each agent its own endpoint, so it reads
  only the Knowledge Bases or dataset meant for it.

## Prerequisites

- A Sanity Context MCP endpoint. Open the Context app in the Sanity Dashboard,
  create an endpoint from Knowledge Bases or a dataset, and copy its MCP URL. It
  looks like
  `https://api.sanity.io/v2026-11-03/context/organizations/YOUR_ORGANIZATION_ID/mcp/YOUR_ENDPOINT_NAME`.
  See [Configure a Context MCP endpoint](https://www.sanity.io/docs/context/configure-mcp).
- An organization API token. Create it in
  [Manage](https://www.sanity.io/manage/org/api/tokens) under **API > Tokens** at
  the organization level, and under **Organization permissions** select
  **Context** with the **Viewer** role. Project tokens don't work, however broad
  their permissions.

??? tip "Create the endpoint with the Sanity CLI"

    Replace `YOUR_ORGANIZATION_ID` with your organization ID and
    `YOUR_KNOWLEDGE_BASE_ID` with the ID that `context create` prints (it starts
    with `kb`).

    ```bash
    npx sanity@latest login

    # Create a Knowledge Base. The command prints its ID.
    npx sanity@latest context create --organization YOUR_ORGANIZATION_ID --title "Support" --description "Answers to customer support questions"

    # Add sources: files, a website to crawl (--url), or a dataset query
    npx sanity@latest context sources create YOUR_KNOWLEDGE_BASE_ID --file ./returns-policy.pdf

    # Build it and review open issues, such as conflicts between sources
    npx sanity@latest context build YOUR_KNOWLEDGE_BASE_ID --watch
    npx sanity@latest context issues list YOUR_KNOWLEDGE_BASE_ID --status open

    # Create the MCP endpoint. The command prints its URL.
    npx sanity@latest context mcp create support --title "Support" --organization YOUR_ORGANIZATION_ID --knowledge-base YOUR_KNOWLEDGE_BASE_ID
    ```

    To serve a live dataset instead, replace
    `--knowledge-base YOUR_KNOWLEDGE_BASE_ID` with
    `-p YOUR_PROJECT_ID -d production`.

## Installation

=== "Python"

    ```bash
    pip install "google-adk[mcp]"
    ```

=== "TypeScript"

    ```bash
    npm install @google/adk @modelcontextprotocol/sdk
    ```

## Use with agent

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    SANITY_CONTEXT_MCP_URL = "YOUR_SANITY_CONTEXT_MCP_URL"
    SANITY_ORGANIZATION_TOKEN = "YOUR_SANITY_ORGANIZATION_TOKEN"

    root_agent = Agent(
        model="gemini-flash-latest",
        name="sanity_context_agent",
        instruction=(
            "Answer questions using the Sanity Context tools. Call the initial_context tool "
            "before your first lookup to learn what content exists. Look up content before "
            "you answer, and say so when the content doesn't cover a question."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=SANITY_CONTEXT_MCP_URL,
                    headers={"Authorization": f"Bearer {SANITY_ORGANIZATION_TOKEN}"},
                    timeout=30,
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const SANITY_CONTEXT_MCP_URL = "YOUR_SANITY_CONTEXT_MCP_URL";
    const SANITY_ORGANIZATION_TOKEN = "YOUR_SANITY_ORGANIZATION_TOKEN";

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "sanity_context_agent",
        instruction:
            "Answer questions using the Sanity Context tools. Call the initial_context tool " +
            "before your first lookup to learn what content exists. Look up content before " +
            "you answer, and say so when the content doesn't cover a question.",
        tools: [
            new MCPToolset({
                type: "StreamableHTTPConnectionParams",
                url: SANITY_CONTEXT_MCP_URL,
                transportOptions: {
                    requestInit: {
                        headers: { Authorization: `Bearer ${SANITY_ORGANIZATION_TOKEN}` },
                    },
                },
            }),
        ],
    });

    export { rootAgent };
    ```

!!! note

    If the URL or token is wrong, Python and TypeScript behave differently. ADK
    Python logs `will run without the tools from toolset McpToolset, which failed
    to load` and runs the agent without the Sanity Context tools, so the agent
    answers without calling any tools. With `adk run`, that error goes to the
    agent log file, not the terminal. ADK TypeScript stops the run with
    `Failed to create MCP session`. In both cases, check that the URL is the
    endpoint's MCP URL and that the token is an organization API token with
    Context Viewer permissions.

## Available tools

The tools depend on the endpoint's sources. An endpoint with both source types
serves both sets.

### Knowledge Base tools

Tool | Description
---- | -----------
`initial_context` | Returns the outline of each Knowledge Base, plus the endpoint's instructions
`knowledge_base_search` | Searches entry content by keyword and returns ranked entries
`knowledge_base_read` | Reads the full content of up to 20 entries in one call

### Dataset tools

Tool | Description
---- | -----------
`initial_context` | Returns a compressed schema overview, plus the endpoint's instructions
`groq_query` | Queries the dataset with GROQ
`schema_explorer` | Returns a schema type's fields and references
`array_field_reader` | Reads large array fields, such as Portable Text, on a single document

## Configuration

- **Initial context**: To save a tool call per conversation, fetch the
  endpoint's initial context over HTTP and add it to the instruction. Then
  remove the `initial_context` sentence from the instruction and hide the tool
  with a tool filter. Pass the instruction as a function, because ADK fills
  `{placeholders}` in string instructions from session state, and the GROQ
  projections in initial context make that fail. See
  [Connect Sanity Context to ADK](https://www.sanity.io/docs/context/connect-google-adk)
  for a complete example, and
  [Inline initial context into your system prompt](https://www.sanity.io/docs/context/inline-initial-context)
  to keep the payload fresh in long-running agents.
- **Tool filters**: Pass `tool_filter` in Python, or the second argument of
  `MCPToolset` in TypeScript, to limit which tools the agent can call.
- **Timeouts**: The Python example raises the connection timeout from the
  5-second default with `timeout=30`.

## Agent skills

Install the
[Sanity Context agent skills](https://github.com/sanity-io/context#using-skills)
from your project directory:

```bash
npx skills add sanity-io/context --all
```

The skills give compatible coding agents guidance on creating the endpoint,
writing its instructions, and shaping your agent's system prompt.

## Additional resources

- [Sanity Context Documentation](https://www.sanity.io/docs/context/introduction)
- [Sanity Context ADK Guide](https://www.sanity.io/docs/context/connect-google-adk)
- [Sanity Context Knowledge Bases](https://www.sanity.io/docs/context/knowledge-bases)
- [Sanity Context MCP Tools](https://www.sanity.io/docs/context/mcp-tools)
- [Sanity Context Packages and Agent Skills](https://github.com/sanity-io/context)
