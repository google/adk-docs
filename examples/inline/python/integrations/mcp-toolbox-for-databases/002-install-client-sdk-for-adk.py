from google.adk.tools.toolbox_toolset import ToolboxToolset
from toolbox_adk import CredentialStrategy

# target_audience: The URL of your MCP Toolbox server
creds = CredentialStrategy.workload_identity(target_audience="<TOOLBOX_URL>")

toolset = ToolboxToolset(
    server_url="<TOOLBOX_URL>",
    credentials=creds
)