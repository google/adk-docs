"""Google Search Agent definition for ADK Gemini Live API Toolkit demo."""

import os
from google.adk.agents import Agent
from google.adk.tools import google_search

# Default models for Live API with native audio support:
# - Gemini Live API: gemini-2.5-flash-native-audio-preview-12-2025
# - Gemini Live API (Agent Platform): gemini-live-2.5-flash-native-audio
agent = Agent(
    name="google_search_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[google_search],
    instruction="You are a helpful assistant that can search the web."
)