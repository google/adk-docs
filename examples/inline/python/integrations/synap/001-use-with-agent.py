import os

from google.adk.agents.llm_agent import Agent
from maximem_synap import MaximemSynapSDK
from synap_google_adk import create_synap_tools

sdk = MaximemSynapSDK(api_key=os.environ["SYNAP_API_KEY"])

synap_tools = create_synap_tools(
    sdk=sdk,
    user_id="alice",
    customer_id="acme_corp",
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="memory_assistant",
    instruction=(
        "You are a helpful assistant with long-term memory. "
        "Use search_memory to recall what you know about the user. "
        "Use store_memory to save important new facts the user mentions."
    ),
    tools=synap_tools,
)