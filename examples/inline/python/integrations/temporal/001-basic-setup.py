from contextlib import aclosing
from datetime import timedelta
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.contrib.google_adk_agents import TemporalModel
from temporalio.contrib.google_adk_agents.workflow import activity_tool
from temporalio.workflow import ActivityConfig

# A Temporal Activity

@activity.defn
async def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Your weather API call here
    return f"72°F and sunny in {city}"

# Wrap the activity as an ADK tool.  This tool will get memoized, retried, and timed out.
weather_tool = activity_tool(
    get_weather,
    start_to_close_timeout=timedelta(seconds=30),
    retry_policy=RetryPolicy(maximum_attempts=3),
)

# Use your agent
agent = Agent(
    name="weather_agent",
    model=TemporalModel(
      "gemini-flash-latest",
      activity_config=ActivityConfig(summary="Weather Agent")),
    tools=[weather_tool],
)

# Drop your agent in a Workflow to give it durable execution.

@workflow.defn
class WeatherAgentWorkflow:
    @workflow.run
    async def run(self, user_message: str) -> str:
        # For testing; for production, use Runner()
        runner = InMemoryRunner(agent=agent, app_name="weather_app")
        session = await runner.session_service.create_session(
            user_id="user", app_name="weather_app"
        )
        result = ""
        async with aclosing(runner.run_async(
            user_id="user",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part.from_text(text=user_message)]
            ),
        )) as events:
            async for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            result = part.text
        return result