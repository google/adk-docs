from google.adk.tools import agent_tool

# Placeholder definition for MyImageAgent
class MyImageAgent:
    def __init__(
        self, name="My Agent", description="A simple image agent."
    ):
        self.name = name
        # Added description attribute
        self.description = description 

# Example 1: Isolate MyImageAgent from parent plugins 
my_isolated_tool = agent_tool.AgentTool(
    agent=MyImageAgent(), # Instantiate MyImageAgent
    include_plugins=False
)

# Example 2: Inherit plugins
my_observable_tool = agent_tool.AgentTool(
    agent=MyImageAgent(), # Instantiate MyImageAgent
    include_plugins=True
)