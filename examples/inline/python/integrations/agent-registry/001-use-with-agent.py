from google.adk.agents.llm_agent import LlmAgent
from google.adk.integrations.agent_registry import AgentRegistry
import os

# 1. Initialization
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

if not project_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")

registry = AgentRegistry(
    project_id=project_id,
    location=location,
)

# 2. Listing Resources
print("Listing Agents...")
agents_response = registry.list_agents()
for agent in agents_response.get("agents", []):
    print(f"  - {agent.get('name')} ({agent.get('displayName')})")

print("Listing MCP Servers...")
mcp_servers_response = registry.list_mcp_servers()
for server in mcp_servers_response.get("mcpServers", []):
    print(f"  - {server.get('name')} ({server.get('displayName')})")

# 3. Using a Remote A2A Agent
# Replace with the full resource name of your registered agent
agent_name = f"projects/{project_id}/locations/{location}/agents/YOUR_AGENT_ID"
my_remote_agent = registry.get_remote_a2a_agent(agent_name=agent_name)

# 4. Using an MCP Toolset
# Replace with the full resource name of your registered MCP server
mcp_server_name = f"projects/{project_id}/locations/{location}/mcpServers/YOUR_MCP_SERVER_ID"
my_mcp_toolset = registry.get_mcp_toolset(mcp_server_name=mcp_server_name)

# 5. Example Agent Composition
main_agent = LlmAgent(
    model="gemini-flash-latest", # Or your preferred model
    name="demo_agent",
    instruction="You can leverage registered tools and sub-agents.",
    tools=[my_mcp_toolset],
    sub_agents=[my_remote_agent],
)