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