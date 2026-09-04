# Context caching with Gemini

Supported in ADKPython v1.15.0Java v0.1.0Kotlin v0.7.0

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

```java
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.ContextCacheConfig;
import com.google.adk.apps.App;
import java.time.Duration;

// Create the app with context caching configuration
App app = App.builder()
             .name("my-caching-agent-app")
             .rootAgent(rootAgent)
             .contextCacheConfig(
                 new ContextCacheConfig(
                     5, /* cache_intervals (max invocations) */
                     Duration.ofMinutes(10), /* ttl */
                     2048 /* min_tokens */))
             .build();
```

```kotlin
import com.google.adk.kt.agents.ContextCacheConfig
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.ExperimentalContextCachingFeature
import com.google.adk.kt.apps.App
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.types.HttpOptions
import kotlin.time.Duration.Companion.minutes
import kotlin.time.Duration.Companion.seconds

val rootAgent =
    LlmAgent(
        name = "my_caching_agent",
        // configure an agent using Gemini 2.0 or higher
        model = Gemini(name = "gemini-flash-latest"),
    )

// Create the app with context caching configuration
@OptIn(ExperimentalContextCachingFeature::class)
val app =
    App(
        appName = "my-caching-agent-app",
        rootAgent = rootAgent,
        contextCacheConfig =
            ContextCacheConfig(
                // Gemini applies its own minimum cacheable size, which varies by model
                minTokens = 8192,
                ttl = 10.minutes, // Store for up to 10 minutes
                cacheIntervals = 5, // Refresh after 5 uses
                // On timeout the create fails and the request proceeds uncached.
                createHttpOptions = HttpOptions(timeout = 10.seconds),
            ),
    )
```

## Configuration settings

The `ContextCacheConfig` class has the following settings that control how caching works for your agent. When you configure these settings, they apply to all agents within your app.

- **`min_tokens`** (int): The minimum number of tokens required in a request to enable caching. This setting allows you to avoid the overhead of caching for very small requests where the performance benefit would be negligible. Defaults to `0`.
- **`ttl_seconds`** (int): The time-to-live (TTL) for the cache in seconds. This setting determines how long the cached content is stored before it is refreshed. Defaults to `1800` (30 minutes).
- **`cache_intervals`** (int): The maximum number of times the same cached content can be used before it expires. This setting allows you to control how frequently the cache is updated, even if the TTL has not expired. Defaults to `10`.
- **`create_http_options`** (HttpOptions): The HTTP options for the cache creation call, which lets you set a timeout on it. If the call times out, it fails and the request proceeds without caching. Available in Python and Kotlin; defaults to none.

## Check whether the cache is being used

Supported in ADKKotlin v0.6.0

When caching is enabled, an event backed by an LLM response can carry a `CacheMetadata` reporting what the cache did for that call. It is null when caching is disabled, and also when the call produced no cache information, so check for it before reading it. When present it has two states: an **active cache**, where `cacheName`, `expireTime` and `invocationsUsed` are all set, and a **fingerprint-only** state, where all three are null.

```kotlin
/** Reports whether the context cache was used for the LLM call behind [event]. */
fun logCacheUse(event: Event) {
    // Null when caching is disabled, and on any event whose LLM call produced
    // no cache information.
    val cache = event.cacheMetadata ?: return

    if (!cache.isActive) {
        // Fingerprint-only: ADK measured the cacheable prefix but no cache is in
        // use. That is the first turn, a prefix that changed since the last turn,
        // or a cache ADK did not create -- most often because the cacheable
        // prefix was below minTokens.
        println("Not cached yet; fingerprinted ${cache.contentsCount} contents.")
        return
    }

    println("Cache ${cache.cacheName} reused ${cache.invocationsUsed} time(s).")
    if (cache.expireSoon) {
        // Advisory only. ADK goes on reusing the cache until it actually expires,
        // so this is a heads-up for your own code, not a prediction about the
        // next turn.
        println("Cache is at or near expiry.")
    }
}
```

`expireSoon` means the cache expires within about two minutes, or has already expired. It is a signal for your own code, not something ADK acts on: ADK keeps reusing a cache until it is actually past `expireTime`, has run past `cacheIntervals`, or its cached prefix changes.

Token counts are not on `CacheMetadata`; read them from `LlmResponse.usageMetadata`.

## Next steps

For a full implementation of how to use and test the context caching feature, see the following sample:

- [`cache_analysis`](https://github.com/google/adk-python/tree/main/contributing/samples/context_management/cache_analysis): A code sample that demonstrates how to analyze the performance of context caching.

If your use case requires that you provide instructions that are used throughout a session, consider using the `static_instruction` parameter for an agent, which allows you to amend the system instructions for a generative model. For more details, see this sample code:

- [`static_instruction`](https://github.com/google/adk-python/tree/main/contributing/samples/context_management/static_instruction): An implementation of a digital pet agent using static instructions.
