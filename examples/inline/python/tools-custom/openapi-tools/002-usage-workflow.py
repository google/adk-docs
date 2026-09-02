from google.adk.agents import LlmAgent

my_agent = LlmAgent(
    name="api_interacting_agent",
    model="gemini-flash-latest", # Or your preferred model
    tools=[toolset], # Pass the toolset
    # ... other agent config ...
)