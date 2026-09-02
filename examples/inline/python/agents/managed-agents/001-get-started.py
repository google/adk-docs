import os
from google.adk.agents import ManagedAgent
from google.adk.tools import google_search
from google.genai import types

# Ensure you have the MANAGED_AGENT_ID and the proper environment config
_AGENT_ID = os.environ.get('MANAGED_AGENT_ID', 'antigravity-preview-05-2026')

managed_search_agent = ManagedAgent(
    name='managed_search_agent',
    description='Answers questions that need fresh, grounded information from the web.',
    agent_id=_AGENT_ID,
    environment={'type': 'remote'},
    tools=[google_search],
)

# A managed code execution agent using raw types.Tool
managed_code_execution_agent = ManagedAgent(
    name='managed_code_execution_agent',
    description='Solves computational questions by running code server-side.',
    agent_id=_AGENT_ID,
    environment={'type': 'remote'},
    tools=[types.Tool(code_execution=types.ToolCodeExecution())],
)