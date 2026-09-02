from sprites_adk import SpritesPlugin
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

# SpritesPlugin() gives each run a fresh sandbox; SpritesPlugin(sprite_name="my-project")
# reuses one persistent environment across sessions.
plugin = SpritesPlugin(
  # token="your-sprites-token"  # Or set the SPRITES_TOKEN environment variable
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="sandbox_agent",
    instruction="Run code and commands in the Sprite sandbox, not locally.",
    tools=plugin.get_tools(),
)

# Register the plugin on the runner so its lifecycle callbacks and cleanup run.
runner = InMemoryRunner(agent=root_agent, plugins=[plugin])