# 1. Correct the import path to use the google.adk namespace
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.agents import Agent

# 2. Initialize your root agent (required for App setup)
root_agent = Agent(
    name="my_root_agent",
    description="Main coordinating agent for the workflow."
)

# 3. Token-based configuration: Activates the priority/pre-call layer
compaction_config = EventsCompactionConfig(
    token_threshold=4000,     # Triggers compaction when actual token count exceeds this
    event_retention_size=5    # Number of recent raw events to keep intact when token limit is hit
)

# 4. Register with required name and root_agent fields, and the config object
app = App(
    name="my_compacting_agent_app",
    root_agent=root_agent,
    events_compaction_config=compaction_config
)