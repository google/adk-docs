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