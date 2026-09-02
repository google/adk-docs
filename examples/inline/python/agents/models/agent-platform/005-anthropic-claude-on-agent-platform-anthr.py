from google.adk.agents import LlmAgent
from google.genai import types

# --- Example Agent using Claude 3 Sonnet on Agent Platform ---

# Standard model name for Claude 3 Sonnet on Agent Platform
claude_model_vertexai = "claude-3-sonnet@20240229"

agent_claude_vertexai = LlmAgent(
    model=claude_model_vertexai, # Pass the direct model string
    name="claude_vertexai_agent",
    instruction="You are an assistant powered by Claude 3 Sonnet on Agent Platform.",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
    # ... other agent parameters
)