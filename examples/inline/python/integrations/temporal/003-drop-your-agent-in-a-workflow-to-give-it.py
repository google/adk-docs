import asyncio
from temporalio.client import Client
from temporalio.contrib.google_adk_agents import GoogleAdkPlugin

async def start():
    client = await Client.connect(
        "localhost:7233",
        plugins=[GoogleAdkPlugin()]
    )
    result = await client.execute_workflow(
        WeatherAgentWorkflow.run,
        "What's the weather in San Francisco?",
        id="weather-agent-1",
        task_queue="my-agent-task-queue",
    )
    print(result)

asyncio.run(start())