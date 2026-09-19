---
catalog_title: Google Cloud MCP servers
catalog_description: Call BigQuery, Cloud Logging, and other services as agent tools
catalog_icon: /integrations/assets/developer-tools-color.svg
catalog_tags: ["google", "mcp", "connectors"]
---

# Google Cloud MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

Many Google Cloud services, such as BigQuery, Cloud Logging, and Cloud Storage,
provide [remote MCP servers](https://docs.cloud.google.com/mcp/supported-products)
hosted by Google. Your agent connects to a server's endpoint URL over Streamable
HTTP and authenticates with your Google Cloud credentials. There is nothing to
install or run on your side.

To discover MCP servers at runtime instead of using fixed endpoint URLs, see
[Google Cloud Agent Registry](/integrations/agent-registry/).

## Use cases

- **Data analysis**: Let the agent list datasets and run SQL queries in
  BigQuery.
- **Operations and troubleshooting**: Read log entries from Cloud Logging and
  metrics from Cloud Monitoring to investigate an incident.
- **Resource management**: Inspect and manage resources such as Cloud Run
  services, Compute Engine instances, and GKE clusters.

## Prerequisites

- A [Google Cloud project](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects)
  with the service you want to use enabled. Enabling the service also enables
  its MCP server:

    ```bash
    gcloud services enable bigquery.googleapis.com
    ```

- The MCP Tool User role (`roles/mcp.toolUser`) for the account the agent runs
  as, plus the roles the tools need on the service itself, such as BigQuery
  Data Viewer and BigQuery Job User:

    ```bash
    gcloud projects add-iam-policy-binding PROJECT_ID \
        --member=user:EMAIL --role=roles/mcp.toolUser
    ```

- [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc).
  For local development, run `gcloud auth application-default login`.
- ADK installed with the MCP extra:

    ```bash
    pip install "google-adk[mcp]"
    ```

## Use with agent

The example below connects an agent to the BigQuery and Cloud Logging MCP
servers. The header provider runs before each request, so the access token is
refreshed when it expires (after about an hour) and long-running agents keep
working.

=== "Python"

    === "Remote MCP Server"

        ```python
        import google.auth
        from google.auth.transport.requests import Request

        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        PROJECT_ID = "YOUR_PROJECT_ID"

        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )


        def google_cloud_auth_headers(context):
            if not credentials.valid:
                credentials.refresh(Request())
            return {
                "Authorization": f"Bearer {credentials.token}",
                "x-goog-user-project": PROJECT_ID,
            }


        def google_cloud_mcp_toolset(url):
            return McpToolset(
                connection_params=StreamableHTTPConnectionParams(url=url),
                header_provider=google_cloud_auth_headers,
            )


        root_agent = Agent(
            model="gemini-flash-latest",
            name="cloud_ops_agent",
            instruction=(
                "Help users investigate their Google Cloud project. Use the"
                " BigQuery tools for data questions and the Cloud Logging tools"
                " for log questions."
            ),
            tools=[
                google_cloud_mcp_toolset("https://bigquery.googleapis.com/mcp"),
                google_cloud_mcp_toolset("https://logging.googleapis.com/mcp"),
            ],
        )
        ```

## Available MCP servers

Each server exposes its own set of tools. Some examples:

Service | Endpoint
------- | --------
BigQuery | `https://bigquery.googleapis.com/mcp`
Cloud Logging | `https://logging.googleapis.com/mcp`
Cloud Monitoring | `https://monitoring.googleapis.com/mcp`
Cloud Storage | `https://storage.googleapis.com/storage/mcp`
Cloud Run | `https://run.googleapis.com/mcp`
Compute Engine | `https://compute.googleapis.com/mcp`
Google Kubernetes Engine | `https://container.googleapis.com/mcp`

For the full list, see
[Supported products](https://docs.cloud.google.com/mcp/supported-products). To
see the tools a server provides, use the tool reference linked from that page.

## Configuration

- **Limit the tools**: Some servers provide many tools, including tools that
  change resources. Pass `tool_filter` to `McpToolset` to expose only the tools
  the agent needs, for example
  `tool_filter=["list_dataset_ids", "execute_sql_readonly"]`. Some servers also
  provide [toolsets](https://docs.cloud.google.com/mcp/configure-mcp-ai-application#toolsets),
  which are smaller sets of tools with their own endpoint URL.
- **Quota project**: The `x-goog-user-project` header sets the project used for
  quota and billing. Some services require it.
- **Production identity**: In production, run the agent as a dedicated service
  account or agent identity instead of your user account, and grant it only the
  roles the tools need. See
  [Authentication identities](https://docs.cloud.google.com/mcp/configure-mcp-ai-application#authentication-identities).

## Additional resources

- [Google Cloud MCP servers overview](https://docs.cloud.google.com/mcp/overview)
- [Supported products](https://docs.cloud.google.com/mcp/supported-products)
- [Configure MCP in an AI application](https://docs.cloud.google.com/mcp/configure-mcp-ai-application)
- [MCP tools in ADK](/tools-custom/mcp-tools/)
