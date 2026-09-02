import asyncio
from google.adk.agents import config_agent_utils
from google.adk.runners import Runner

async def main():
    # Load the agent directly from the YAML config file
    agent = config_agent_utils.from_config("my_agent/root_agent.yaml")
    # ...

if __name__ == "__main__":
    asyncio.run(main())