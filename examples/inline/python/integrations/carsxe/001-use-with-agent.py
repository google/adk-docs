from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

CARSXE_API_KEY = "YOUR_CARSXE_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="carsxe_agent",
    instruction=(
        "You are a vehicle data assistant. Use the CarsXE tools to decode "
        "VINs and license plates and to look up specifications, market value, "
        "history, recalls, and OBD-II codes."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.carsxe.com/mcp",
                headers={"X-API-Key": CARSXE_API_KEY},
            ),
        )
    ],
)