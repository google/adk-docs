---
catalog_title: Medusa
catalog_description: Query store data, deployments, and logs of your commerce backend
catalog_icon: /integrations/assets/medusa.png
catalog_tags: ["mcp"]
---

# Medusa MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Medusa MCP Server](https://docs.medusajs.com/cloud/medusa-mcp) connects
your ADK agent to [Medusa](https://medusajs.com/), an open source commerce
platform, and to the stores you host on Medusa Cloud. This integration gives
your agent the ability to read your stores' commerce data, inspect deployments,
environment variables, and logs, and search the Medusa documentation using
natural language.

## Use cases

- **Answer questions about your store**: Look up products, orders, customers,
  and other commerce data through the store's Admin and Store APIs, including
  your own custom API routes.

- **Debug deployments**: Check whether the latest deployment succeeded, read
  build logs of a failed deployment, and search runtime logs around the time an
  error happened.

- **Review environment configuration**: List the projects and environments
  you connected, and check which environment variables are set on each one.

- **Learn how to build with Medusa**: Search the official Medusa documentation
  for concepts, modules, APIs, and configuration.

## Prerequisites

- [Sign up](https://cloud.medusajs.com/signup) for a Medusa Cloud account and
  create a project
- [Node.js](https://nodejs.org/) installed, to run `npx`
- For Python, ADK installed with its MCP extra:
  `pip install "google-adk[mcp]"`

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        root_agent = Agent(
            model="gemini-flash-latest",
            name="medusa_agent",
            instruction="Help users manage their Medusa stores and answer questions about Medusa",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://cloud.medusajs.com/mcp",
                            ]
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "medusa_agent",
            instruction: "Help users manage their Medusa stores and answer questions about Medusa",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "mcp-remote", "https://cloud.medusajs.com/mcp"],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    When you run this agent for the first time, a browser window opens
    automatically to sign in to Medusa Cloud via OAuth. Alternatively, you can
    use the authorization URL printed in the console. When you approve the
    request, you choose which store environments the agent can access.

## Available tools

Tool | Description
---- | -----------
`list_connected_organizations` | List the Medusa Cloud organizations that own the connected environments
`get_connected_organization` | Get an organization's details, including its subscription and members
`list_projects` | List the connected Medusa Cloud projects and their environments
`get_project` | Get a project's region, repository, environments, and domains
`list_connected_environments` | List the store environments the agent can access
`find_commerce_api` | Search a store's API, including custom routes, for the routes that perform an action
`describe_commerce_api` | Get the parameters and request details of one store API route
`read_admin_api` | Call a read-only route on a store's Admin API
`read_store_api` | Call a read-only route on a store's Store API as a guest customer
`list_medusa_publishable_keys` | List a store's publishable API keys and their sales channels
`list_medusa_deployments` | List an environment's deployments, newest first
`get_medusa_deployment` | Get a deployment's commit, status, and build metadata
`get_environment_logs` | Read the runtime or build logs of an environment's backend or storefront
`list_environment_variables` | List an environment's variables, without the values of secrets
`get_environment_variable` | Get one environment variable by its ID or key
`get_medusa_cloud_status` | Get the current status of the Medusa Cloud platform
`ask_medusa_question` | Search the official Medusa documentation
`submit_medusa_feedback` | Send feedback about Medusa to the Medusa team

## Additional resources

- [Medusa MCP Server Documentation](https://docs.medusajs.com/cloud/medusa-mcp)
- [Medusa Documentation](https://docs.medusajs.com/)
- [Medusa Repository](https://github.com/medusajs/medusa)
