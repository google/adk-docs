from google.adk.agents import LlmAgent
from google.adk.models import AnthropicGenerateContentConfig

agent = LlmAgent(
    model="claude-sonnet-4@20250514",  # Your Agent Platform Claude model ID.
    name="claude_reasoning_agent",
    instruction="You are a helpful assistant.",
    generate_content_config=AnthropicGenerateContentConfig(
        effort="high",  # One of: "low", "medium", "high", "xhigh", "max".
    ),
)