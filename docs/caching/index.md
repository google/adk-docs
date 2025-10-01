# App-Level Context Caching

The Application Development Kit (ADK) provides an app-level context caching mechanism to improve performance and reduce costs. By caching the static parts of your agent's instructions, you can significantly speed up responses and lower the number of tokens sent to the model for each request.

This document explains how to configure and use this feature.

## `ContextCacheConfig`

To enable context caching, you need to provide a `ContextCacheConfig` object when you create your `App`. This configuration is applied to all LLM agents within the app.

`ContextCacheConfig` has the following fields:

- `min_tokens` (int): The minimum number of tokens required in a request to enable caching. This is useful for avoiding the overhead of caching for very small requests where the performance benefit would be negligible. Defaults to `0`.
- `ttl_seconds` (int): The time-to-live (TTL) for the cache in seconds. This determines how long the cached content will be stored before it's refreshed. Defaults to `1800` (30 minutes).
- `cache_intervals` (int): The maximum number of times the same cached content can be used before it's refreshed. This allows you to control how frequently the cache is updated, even if the TTL has not expired. Defaults to `10`.

## `static_instruction` vs. `instruction`

To use context caching, you need to separate the static and dynamic parts of your agent's instructions.

- `LlmAgent.static_instruction`: Use this field for the static, unchanging parts of your instructions. This is the content that will be cached. It should be a `google.genai.types.Content` object.
- `LlmAgent.instruction`: Use this field for the dynamic parts of your instructions that can change between requests. This can be a string or a function that returns a string.

When you use `static_instruction`, the ADK will automatically handle caching this content for you based on the `ContextCacheConfig` you provide.

## Code Example

Here's an example of how to use app-level context caching with a digital pet agent named "Bingo." Bingo's core personality is defined in `static_instruction`, while its mood, which changes based on when it was last fed, is provided in the dynamic `instruction`.

```python
import time
from google.adk.agents.llm_agent import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig

# Static instruction that doesn't change - perfect for context caching
STATIC_INSTRUCTION_TEXT = """You are Bingo, a lovable digital pet companion! ... """

# Mood-specific instructions for different hunger states
MOOD_INSTRUCTIONS = {
    "full": "CURRENT MOOD: Content and Well-Fed ...",
    "satisfied": "CURRENT MOOD: Happy and Content ...",
    # ... other moods
}

def eat(tool_context: ToolContext) -> str:
    """Feed Bingo the digital pet."""
    tool_context.state["last_fed_timestamp"] = time.time()
    return "🍖 Yum! Thank you for feeding me!"

def get_hunger_state(last_fed_timestamp: float) -> str:
    """Determine hunger state based on time since last feeding."""
    seconds_since_fed = time.time() - last_fed_timestamp
    if seconds_since_fed < 2:
        return "full"
    # ... other hunger states
    return "starving"

def provide_dynamic_instruction(ctx: ReadonlyContext | None = None):
    """Provides dynamic hunger-based instructions for Bingo."""
    hunger_level = "starving"
    if ctx and ctx._invocation_context.session and ctx._invocation_context.session.state:
        last_fed = ctx._invocation_context.session.state.get("last_fed_timestamp")
        if last_fed:
            hunger_level = get_hunger_state(last_fed)
        else:
            hunger_level = "hungry"
    return MOOD_INSTRUCTIONS.get(hunger_level, MOOD_INSTRUCTIONS["starving"])

# Create Bingo the digital pet agent
bingo_agent = Agent(
    model="gemini-1.5-flash",
    name="bingo_digital_pet",
    description="Bingo - A lovable digital pet that needs feeding and care",
    # Static instruction - defines Bingo's core personality (cached)
    static_instruction=types.Content(
        role="user", parts=[types.Part(text=STATIC_INSTRUCTION_TEXT)]
    ),
    # Dynamic instruction - changes based on hunger state from session
    instruction=provide_dynamic_instruction,
    tools=[eat],
)

# Create the app with context caching configuration
bingo_app = App(
    name="bingo_app",
    root_agent=bingo_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=600,  # 10 minutes
        cache_intervals=5, # Refresh after 5 uses
    ),
)
```

## Reference Samples

For more detailed examples of how to use and test the context caching feature, see the following samples in the `adk-python` repository:

- [`static_instruction`](https://github.com/google/adk-python/tree/main/contributing/samples/static_instruction): A complete implementation of the "Bingo the digital pet" agent.
- [`cache_analysis`](https://github.com/google/adk-python/tree/main/contributing/samples/cache_analysis): A sample that demonstrates how to analyze the performance of context caching.
