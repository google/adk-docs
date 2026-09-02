import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from agent import app # import code from agent.py

load_dotenv() # load API keys and settings
# Set a Runner using the imported application object
runner = InMemoryRunner(app=app)

async def main():
    try:  # run_debug() requires ADK Python 1.18 or higher:
        response = await runner.run_debug("Hello there!")

    except Exception as e:
        print(f"An error occurred during agent execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())