# Context caching with Gemini

Supported in ADKPython v1.15.0

When working with agents to complete tasks, you may want to reuse extended instructions or large sets of data across multiple agent requests to a generative AI model. Resending this data for each agent request is slow, inefficient, and can be expensive. Using context caching features in generative AI models can significantly speed up responses and lower the number of tokens sent to the model for each request.

The ADK Context Caching feature allows you to cache request data with generative AI models that support it, including Gemini 2.0 and higher models. This document explains how to configure and use this feature.

## Configure context caching

You configure the context caching feature at the ADK `App` object level, which wraps your agent. Use the `ContextCacheConfig` class to configure these settings, as shown in the following code sample:

```python
from google.adk import Agent
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig

root_agent = Agent(
  # configure an agent using Gemini 2.0 or higher
)

# Create the app with context caching configuration
app = App(
    name='my-caching-agent-app',
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,    # Minimum tokens to trigger caching
        ttl_seconds=600,    # Store for up to 10 minutes
        cache_intervals=5,  # Refresh after 5 uses
    ),
)
```

## Configuration settings

The `ContextCacheConfig` class has the following settings that control how caching works for your agent. When you configure these settings, they apply to all agents within your app.

- **`min_tokens`** (int): The minimum number of tokens required in a request to enable caching. This setting allows you to avoid the overhead of caching for very small requests where the performance benefit would be negligible. Defaults to `0`.
- **`ttl_seconds`** (int): The time-to-live (TTL) for the cache in seconds. This setting determines how long the cached content is stored before it is refreshed. Defaults to `1800` (30 minutes).
- **`cache_intervals`** (int): The maximum number of times the same cached content can be used before it expires. This setting allows you to control how frequently the cache is updated, even if the TTL has not expired. Defaults to `10`.

## Next steps

For a full implementation of how to use and test the context caching feature, see the following sample:

- [`cache_analysis`](https://github.com/google/adk-python/tree/main/contributing/samples/cache_analysis): A code sample that demonstrates how to analyze the performance of context caching.

If your use case requires that you provide instructions that are used throughout a session, consider using the `static_instruction` parameter for an agent, which allows you to amend the system instructions for a generative model. For more details, see this sample code:

- [`static_instruction`](https://github.com/google/adk-python/tree/main/contributing/samples/static_instruction): An implementation of a digital pet agent using static instructions.
