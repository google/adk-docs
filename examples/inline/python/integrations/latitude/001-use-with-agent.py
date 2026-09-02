import asyncio
import os

import google.adk
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from latitude_telemetry import Latitude, capture

latitude = Latitude(
    api_key=os.environ["LATITUDE_API_KEY"],
    project=os.environ["LATITUDE_PROJECT"],
    instrumentations={"google_adk": google.adk},
)


def get_weather(city: str) -> dict:
    """Returns the current weather for a city."""
    return {"status": "success", "report": f"The weather in {city} is sunny."}


agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    description="Agent that answers weather questions using tools.",
    instruction="Answer weather questions using get_weather.",
    tools=[get_weather],
)


async def weather_agent_run():
    runner = InMemoryRunner(agent=agent, app_name="weather_app")
    await runner.session_service.create_session(
        app_name="weather_app",
        user_id="user_123",
        session_id="session_abc",
    )

    async for event in runner.run_async(
        user_id="user_123",
        session_id="session_abc",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What's the weather in Barcelona?")],
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text


# Wrap a request or job with capture() to attach a user_id, session_id, tags,
# or metadata to every span produced inside it.
capture("weather-agent-run", lambda: asyncio.run(weather_agent_run()))

# Flush any pending spans and shut down before the process exits.
latitude.shutdown()