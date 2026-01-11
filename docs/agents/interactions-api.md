# Using the Gemini Interactions API

The Gemini Interactions API provides stateful conversation capabilities, allowing you to chain interactions using a `previous_interaction_id` instead of sending the full conversation history with each request. This can be more efficient for long conversations.

To enable the Interactions API, set the `use_interactions_api=True` parameter in the `Gemini` model configuration.

## Example

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini

root_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash",
        use_interactions_api=True,
    ),
    name="interactions_test_agent",
    description="An agent for testing the Interactions API integration",
    instruction="You are a helpful assistant.",
)
```

For a more detailed example, see the [Interactions API sample](https://github.com/google/adk-python/tree/main/contributing/samples/interactions_api).
