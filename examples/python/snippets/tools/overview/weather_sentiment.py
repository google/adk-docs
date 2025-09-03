# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

APP_NAME="weather_sentiment_agent"
USER_ID="user1234"
SESSION_ID="1234"
MODEL_ID="gemini-2.0-flash"

# Tool 1
def get_weather_report(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Returns:
        dict: A dictionary containing the weather information with a 'status' key ('success' or 'error') and a 'report' key with the weather details if successful, or an 'error_message' if an error occurred.
    """
    if city.lower() == "london":
        return {"status": "success", "report": "The current weather in London is cloudy with a temperature of 18 degrees Celsius and a chance of rain."}
    elif city.lower() == "paris":
        return {"status": "success", "report": "The weather in Paris is sunny with a temperature of 25 degrees Celsius."}
    else:
        return {"status": "error", "error_message": f"Weather information for '{city}' is not available."}

weather_tool = FunctionTool(func=get_weather_report)


# Tool 2
def analyze_sentiment(text: str) -> dict:
    """Analyzes the sentiment of the given text.

    Returns:
        dict: A dictionary with 'sentiment' ('positive', 'negative', or 'neutral') and a 'confidence' score.
    """
    if "good" in text.lower() or "sunny" in text.lower():
        return {"sentiment": "positive", "confidence": 0.8}
    elif "rain" in text.lower() or "bad" in text.lower():
        return {"sentiment": "negative", "confidence": 0.7}
    else:
        return {"sentiment": "neutral", "confidence": 0.6}

sentiment_tool = FunctionTool(func=analyze_sentiment)


# Agent
weather_sentiment_agent = Agent(
    model=MODEL_ID,
    name='weather_sentiment_agent',
    instruction="""You are a helpful assistant that provides weather information and analyzes the sentiment of user feedback.
**If the user asks about the weather in a specific city, use the 'get_weather_report' tool to retrieve the weather details.**
**If the 'get_weather_report' tool returns a 'success' status, provide the weather report to the user.**
**If the 'get_weather_report' tool returns an 'error' status, inform the user that the weather information for the specified city is not available and ask if they have another city in mind.**
**After providing a weather report, if the user gives feedback on the weather (e.g., 'That's good' or 'I don't like rain'), use the 'analyze_sentiment' tool to understand their sentiment.** Then, briefly acknowledge their sentiment.
You can handle these tasks sequentially if needed.""",
    tools=[weather_tool, sentiment_tool]
)

async def main():
    """Main function to run the agent asynchronously."""
    # Session and Runner Setup
    session_service = InMemorySessionService()
    # Use 'await' to correctly create the session
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    
    runner = Runner(agent=weather_sentiment_agent, app_name=APP_NAME, session_service=session_service)

    # Agent Interaction
    query = "weather in london?"
    print(f"User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    # The runner's run method handles the async loop internally
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response:", final_response)

# Standard way to run the main async function
if __name__ == "__main__":
    asyncio.run(main())