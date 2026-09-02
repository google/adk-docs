from google.adk.agents.llm_agent import Agent
from google.adk.apps import App

root_agent = Agent(
    model='gemini-flash-latest',
    name='greeter_agent',
    description='An agent that provides a friendly greeting.',
    instruction='Reply with Hello, World!',
)

app = App(
    name="agents",
    root_agent=root_agent,
    # Optionally include App-level features:
    # plugins, context_cache_config, events_compaction_config,
    # resumability_config
)