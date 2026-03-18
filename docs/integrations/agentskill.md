---
catalog_title: agentskill.sh
catalog_description: Search, discover, and install AI agent skills
catalog_icon: /adk-docs/integrations/assets/agentskill.png
catalog_tags: ["mcp"]
---

# agentskill.sh MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [agentskill.sh MCP Server](https://www.npmjs.com/package/agentskill-mcp)
connects your ADK agent to [agentskill.sh](https://agentskill.sh), a directory
of over 110,000 AI agent skills following the
[Agent Skill specification](https://agentskills.io). This integration allows
your agent to search, discover, and install skills from the registry using
natural language.

Skills installed from agentskill.sh follow the standard `SKILL.md` format and
can be loaded directly with ADK's
[SkillToolset](../skills/index.md).

## Use cases

- **Skill Discovery**: Search for skills by keyword, platform, or category.
  Find the right skill for a task from over 110,000 community-contributed
  options.

- **On-demand Installation**: Install skills directly to your agent's skills
  directory. Downloaded skills follow the Agent Skill specification and work
  with `load_skill_from_dir()`.

- **Trending and Popular Skills**: Browse trending and top-rated skills to find
  high-quality, community-vetted capabilities for your agent.

## Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later) for running the MCP server
  via `npx`.

No API key or account is required.

## Use with agent

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="skill_discovery_agent",
        instruction=(
            "You help users find and install AI agent skills. "
            "Search for skills based on what the user needs, "
            "show them the best options, and install skills "
            "when requested."
        ),
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="npx",
                        args=["-y", "agentskill-mcp"],
                    ),
                    timeout=30,
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const rootAgent = new LlmAgent({
        model: "gemini-2.5-pro",
        name: "skill_discovery_agent",
        instruction:
            "You help users find and install AI agent skills. " +
            "Search for skills based on what the user needs, " +
            "show them the best options, and install skills " +
            "when requested.",
        tools: [
            new MCPToolset({
                type: "StdioConnectionParams",
                serverParams: {
                    command: "npx",
                    args: ["-y", "agentskill-mcp"],
                },
            }),
        ],
    });

    export { rootAgent };
    ```

## Available tools

Tool | Description
---- | -----------
`search_skills` | Search for skills by keyword with optional platform filtering
`get_skill` | Get full details for a skill including its SKILL.md content
`install_skill` | Download and install a skill to a local directory
`get_trending` | Browse trending, hot, or top-rated skills

## Additional resources

- [agentskill.sh](https://agentskill.sh)
- [agentskill-mcp on npm](https://www.npmjs.com/package/agentskill-mcp)
- [Agent Skill specification](https://agentskills.io)
- [ADK Skills documentation](../skills/index.md)
