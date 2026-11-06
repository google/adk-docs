---
catalog_title: Varity
catalog_description: Deploy apps, AI agents, and LLMs, with the cost shown before you deploy
catalog_tags: ["mcp"]
catalog_icon: /integrations/assets/varity.png
---

# Varity MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Varity MCP server](https://github.com/varity-labs/varity-mcp) connects
ADK agents to [Varity](https://varity.so), a cloud for applications, AI
agents, virtual machines, GPUs, and self-hosted LLMs. Your agent can estimate
what a deployment will cost, deploy a project from its Git repository or a
container image, deploy open-source app templates, follow a deployment's status
and logs, and manage CPU virtual machines.

## Use cases

- **Ship what the agent builds**: Push a project to GitHub and deploy it to a
  live URL. Varity detects the framework, builds it, and attaches the databases
  it needs.
- **Price before deploying**: Ask "What would it cost to host this app?" and
  get the monthly cost before anything is created.
- **Run open-source apps**: Deploy certified templates such as Open WebUI,
  Langflow, Uptime Kuma, or Metabase without managing servers.
- **Operate deployments**: Check status, read runtime logs, redeploy, and
  delete a deployment to stop its billing.

## Prerequisites

- [Node.js](https://nodejs.org/) 22.11 or later (the server runs with `npx`)
- A Varity account and deploy key from the
  [developer portal](https://developer.store.varity.so)
- The Varity CLI for deploys, signed in with that key:

    ```bash
    pipx install varitykit
    varitykit auth login
    ```

The deploy key is entered only in the CLI prompt. It is never passed to the
agent or to MCP tool arguments.

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        varity_tools = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["-y", "@varity-labs/mcp"],
                ),
                timeout=120,
            )
        )

        root_agent = Agent(
            model="gemini-flash-latest",
            name="varity_agent",
            instruction="Help users deploy and manage apps on Varity. "
            "Always show the monthly cost with varity_cost_calculator and "
            "get the user's confirmation before deploying.",
            tools=[varity_tools],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "varity_agent",
            instruction:
                "Help users deploy and manage apps on Varity. Always show the " +
                "monthly cost with varity_cost_calculator and get the user's " +
                "confirmation before deploying.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@varity-labs/mcp"],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Safety

Deployments and virtual machines are billed to the Varity account that owns
the deploy key. Keep cost checks and user confirmation in the agent's
instructions, and use `tool_filter` to expose only read-only tools (for
example `varity_search_docs`, `varity_cost_calculator`,
`varity_list_templates`, `varity_deploy_status`) when the agent should not
create resources.

## Available tools

Tool | Description
---- | -----------
`varity_search_docs` | Search the Varity documentation
`varity_cost_calculator` | Estimate the monthly cost of a deployment before deploying
`varity_balance` | Read the account balance in USD
`varity_doctor` | Check that Node.js, npm, the Varity CLI, and sign-in are ready
`varity_login` | Check for a configured deploy key and open the portal settings page when one is needed
`varity_create_repo` | Create a GitHub repository and push a local project to it
`varity_install_deps` | Install npm dependencies in a project
`varity_build` | Build a project for production
`varity_dev_server` | Start, stop, or check the local development server
`varity_open_browser` | Open a URL in the user's browser
`varity_deploy` | Deploy a Git repository or a prebuilt container image
`varity_deploy_status` | List deployments or get one deployment's status and URL
`varity_deploy_logs` | Read recent runtime logs for a deployment
`varity_redeploy` | Reapply the saved configuration of a deployed app
`varity_delete_deployment` | Delete a deployment and stop its billing
`varity_set_env` | Point to the secret-safe place to set environment variables (never accepts values)
`varity_list_templates` | List certified open-source app templates
`varity_template_info` | Show a template's resources, hardware, and requirements
`varity_deploy_template` | Deploy a public certified template
`varity_list_agents` | Alias of `varity_list_templates`
`varity_agent_info` | Alias of `varity_template_info`
`varity_deploy_agent` | Alias of `varity_deploy_template`
`varity_machines_list` | List CPU virtual machines and available profiles
`varity_machines_create` | Create a CPU virtual machine with the user's SSH public key
`varity_machines_delete` | Delete a CPU virtual machine
`varity_migrate` | Preview the changes needed to move a Vercel project to Varity

## Additional resources

- [Varity MCP server on GitHub](https://github.com/varity-labs/varity-mcp)
- [Varity documentation](https://docs.varity.so)
- [Varity app templates](https://varity.so/templates)
