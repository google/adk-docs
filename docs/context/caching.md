# Context caching with Gemini

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.15.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.7.0</span>
</div>

When working with agents to complete tasks, you may want to reuse extended
instructions or large sets of data across multiple agent requests to a
generative AI model. Resending this data for each agent request is slow,
inefficient, and can be expensive. Using context caching features in generative
AI models can significantly speed up responses and lower the number of tokens
sent to the model for each request.

The ADK Context Caching feature allows you to cache request data with generative
AI models that support it, including Gemini 2.0 and higher models. This document
explains how to configure and use this feature.

## Configure context caching

You configure the context caching feature at the ADK `App` object level,
which wraps your agent. Use the `ContextCacheConfig` class to configure
these settings, as shown in the following code sample:

=== "Python"

    ```python
    --8<-- "examples/inline/python/context/caching/001-configure-context-caching.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/context/caching/002-configure-context-caching.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/inline/kotlin/context/caching/003-configure-context-caching.kt"
    ```

## Configuration settings

The `ContextCacheConfig` class has the following settings that control how
caching works for your agent. When you configure these settings, they apply to
all agents within your app.

-   **`min_tokens`** (int): The minimum number of tokens required in a request
    to enable caching. This setting allows you to avoid the overhead of caching
    for very small requests where the performance benefit would be negligible.
    Defaults to `0`.
-   **`ttl_seconds`** (int): The time-to-live (TTL) for the cache in seconds.
    This setting determines how long the cached content is stored before it is
    refreshed. Defaults to `1800` (30 minutes).
-   **`cache_intervals`** (int): The maximum number of times the same cached
    content can be used before it expires. This setting allows you to
    control how frequently the cache is updated, even if the TTL has not
    expired. Defaults to `10`.
-   **`create_http_options`** (HttpOptions): The HTTP options for the cache
    creation call, which lets you set a timeout on it. If the call times out,
    it fails and the request proceeds without caching. Available in Python and
    Kotlin; defaults to none.

## Check whether the cache is being used

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-kotlin">Kotlin v0.6.0</span>
</div>

When caching is enabled, an event backed by an LLM response can carry a
`CacheMetadata` reporting what the cache did for that call. It is null when
caching is disabled, and also when the call produced no cache information, so
check for it before reading it. When present it has two states: an **active
cache**, where `cacheName`, `expireTime` and `invocationsUsed` are all set, and
a **fingerprint-only** state, where all three are null.

```kotlin
--8<-- "examples/kotlin/snippets/context/CacheMetadataExample.kt:cache_metadata"
```

`expireSoon` means the cache expires within about two minutes, or has already
expired. It is a signal for your own code, not something ADK acts on: ADK keeps
reusing a cache until it is actually past `expireTime`, has run past
`cacheIntervals`, or its cached prefix changes.

Token counts are not on `CacheMetadata`; read them from `LlmResponse.usageMetadata`.

## Next steps

For a full implementation of how to use and test the context caching feature,
see the following sample:

-   [`cache_analysis`](https://github.com/google/adk-python/tree/main/contributing/samples/context_management/cache_analysis):
    A code sample that demonstrates how to analyze the performance of context
    caching.

If your use case requires that you provide instructions that are used throughout
a session, consider using the `static_instruction` parameter for an agent, which
allows you to amend the system instructions for a generative model. For more
details, see this sample code:

-   [`static_instruction`](https://github.com/google/adk-python/tree/main/contributing/samples/context_management/static_instruction):
    An implementation of a digital pet agent using static instructions.