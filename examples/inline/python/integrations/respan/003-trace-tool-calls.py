from google.adk.agents import Agent


def get_weather(city: str) -> str:
    """Return a deterministic weather report for a city."""
    return f"{city}: sunny, 72F, light wind"


agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    instruction="Use the get_weather tool when weather is requested.",
    tools=[get_weather],
)