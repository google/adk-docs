# Use Anthropic Claude models with ADK

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v2.4.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

You can use Anthropic's Claude models as the model for your Agent Development
Kit (ADK) agents. The framework provides Claude model classes that translate ADK requests,
tools, and responses into calls to Claude, so you can build agents with Claude
the same way you build them with Gemini, allowing you to:

-   Run an agent on Claude while keeping your ADK tools, sessions, and
    callbacks unchanged.
-   Combine Claude and Gemini agents in one multi-agent system, and choose
    the model for each agent based on its task.
-   Give Claude more reasoning time on complex tasks with extended thinking.

You can reach Claude through two backends: the **Anthropic API**, using an
Anthropic API key, or **Google Cloud Agent Platform**, using your Google Cloud
project and credentials. For help choosing, see [Choose a backend](#choose-a-backend).

## Get started

The following examples create an agent that calls Claude through the Anthropic
API. Before you run them, get an API key from the
[Anthropic Console](https://console.anthropic.com/) and set it as an
environment variable. In production, store the key in a secret manager rather
than in source code or shell history:

```shell
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
```

=== "Python"

    Install ADK with the Anthropic SDK:

    ```shell
    pip install "google-adk[extensions]"
    ```

    Create an `AnthropicLlm` instance and pass it to your agent. It reads your
    API key from the `ANTHROPIC_API_KEY` environment variable. The
    `AnthropicLlm` class is available in ADK Python v1.20.0 and later.

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models.anthropic_llm import AnthropicLlm

    root_agent = LlmAgent(
        name="claude_agent",
        model=AnthropicLlm(model="claude-sonnet-4-6"),
        instruction="You are a helpful assistant.",
    )
    ```

=== "TypeScript"

    In TypeScript, Claude is available through Google Cloud Agent Platform only. 
    Install the ADK integrations package and the Anthropic SDKs:

    ```shell
    npm install @google/adk @google/adk-integrations @anthropic-ai/sdk @anthropic-ai/vertex-sdk
    ```

    Complete the [Agent Platform setup](#connect-through-agent-platform), then
    create a `Claude` instance and pass it to your agent:

    ```typescript
    import {LlmAgent} from '@google/adk';
    import {Claude} from '@google/adk-integrations';

    export const rootAgent = new LlmAgent({
      name: 'claude_agent',
      model: new Claude({model: 'claude-sonnet-4-6@default'}),
      instruction: 'You are a helpful assistant.',
    });
    ```

=== "Go"

    !!! example "Experimental"

        The `anthropicmodel` package is experimental. Its API and behavior may
        have limitations and it is not recommended for production use.

    Create a model with `anthropicmodel.NewModel` and pass it to your agent.
    When `APIKey` is empty, the model reads your key from the
    `ANTHROPIC_API_KEY` environment variable.

    ```go
    import (
    	"context"
    	"log"

    	"google.golang.org/adk/v2/agent/llmagent"
    	"google.golang.org/adk/v2/model/anthropicmodel"
    )

    llm, err := anthropicmodel.NewModel(context.Background(), "claude-sonnet-4-6", anthropicmodel.ClientConfig{
    	Backend: anthropicmodel.BackendAnthropic,
    })
    if err != nil {
    	log.Fatal(err)
    }

    agent, err := llmagent.New(llmagent.Config{
    	Name:        "claude_agent",
    	Model:       llm,
    	Instruction: "You are a helpful assistant.",
    })
    if err != nil {
    	log.Fatal(err)
    }
    ```

    For a complete, runnable sample, see
    [examples/anthropic/](https://github.com/google/adk-go/tree/main/examples/anthropic)
    in the ADK Go repository.

=== "Java"

    The ADK Java core library includes the
    [Anthropic Java SDK](https://github.com/anthropics/anthropic-sdk-java) as a
    dependency. Create an `AnthropicClient`, wrap it in a `Claude` instance,
    and pass that to your agent:

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude;

    public class ClaudeAgent {

      public static LlmAgent createAgent() {
        AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
            .apiKey(System.getenv("ANTHROPIC_API_KEY"))
            .build();

        return LlmAgent.builder()
            .name("claude_agent")
            .model(new Claude("claude-sonnet-4-6", anthropicClient))
            .instruction("You are a helpful assistant.")
            .build();
      }
    }
    ```

=== "Kotlin"

    Add the ADK Anthropic integration to your Gradle build. This module is
    JVM-only.

    ```kotlin
    implementation("com.google.adk:google-adk-kotlin-integrations-anthropic:1.5.0")
    ```

    Create a `Claude` instance and pass it to your agent. When you omit
    `apiKey`, the model reads your key from the `ANTHROPIC_API_KEY` environment
    variable.

    ```kotlin
    import com.google.adk.kt.agents.Instruction
    import com.google.adk.kt.agents.LlmAgent
    import com.google.adk.kt.models.anthropic.Claude

    val rootAgent =
      LlmAgent(
        name = "claude_agent",
        model = Claude(name = "claude-sonnet-4-6"),
        instruction = Instruction("You are a helpful assistant."),
      )
    ```

## Choose a backend

Choose a backend based on where you manage billing, access, and quotas:

-   **Anthropic API:** Use this backend if you already have an Anthropic
    account and manage Claude usage there. You authenticate with an Anthropic
    API key.
-   **Google Cloud:** Use this backend if your application runs
    on Google Cloud, or you want Claude usage governed by your Google Cloud
    project's IAM permissions, quotas, and billing. You
    authenticate with Application Default Credentials (ADC), and you don't
    manage a separate API key.

The following table shows how each language selects a backend:

| Language   | Anthropic API                                       | Agent Platform                                                       |
| :--------- | :-------------------------------------------------- | :------------------------------------------------------------------- |
| Python     | `AnthropicLlm` instance                             | `Claude` instance, or a `claude-*` model string                      |
| TypeScript | Not supported                                       | `Claude` instance, or a `claude-*` string after registering `Claude` |
| Go         | `ClientConfig.Backend` set to `BackendAnthropic`    | `ClientConfig.Backend` set to `BackendVertex`                        |
| Java       | `Claude` with an `AnthropicClient` using an API key | `Claude` with an `AnthropicClient` using a `VertexBackend`           |
| Kotlin     | `Claude(name, apiKey)`                              | `Claude(name, vertexCredentials)`                                    |

!!! warning "Python model strings use Google Cloud Agent Platform"

    In Python, a bare `claude-*` model string, such as
    `model="claude-sonnet-4-6"`, routes to the Agent Platform backend and
    requires Google Cloud project settings. To use the Anthropic API from
    Python, pass an `AnthropicLlm` instance instead of a string.

## Connect through Google Cloud

To use Claude through Google Cloud, set up your Google Cloud environment:

1.  Enable the Claude models you want to use in
    [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
    for your Google Cloud project.
2.  Set up Application Default Credentials:

    ```shell
    gcloud auth application-default login
    ```

3.  Set your project and a region where the model is available, such as
    `global` or `us-east5`:

    ```shell
    export GOOGLE_CLOUD_PROJECT="your-project-id"
    export GOOGLE_CLOUD_LOCATION="global"
    ```

For more details on connecting ADK to Google Cloud, see
[Connect to Google Cloud and Agent Platform](/get-started/google-cloud/).

The following examples create an agent that calls Claude through Google
Cloud:

=== "Python"

    Pass a Claude model string to your agent. ADK routes `claude-*` strings to
    the `Claude` class, which reads `GOOGLE_CLOUD_PROJECT` and
    `GOOGLE_CLOUD_LOCATION`.

    ```python
    from google.adk.agents import LlmAgent

    root_agent = LlmAgent(
        name="claude_agent",
        model="claude-sonnet-4-6",
        instruction="You are a helpful assistant.",
    )
    ```

    ADK Python v2.9.0 and later routes every `claude-*` model string to
    `Claude`. In earlier versions, if ADK doesn't recognize a model string,
    pass an instance instead: `model=Claude(model="claude-sonnet-4-6")`, with
    `Claude` imported from `google.adk.models`.

=== "TypeScript"

    Register `Claude` once at startup so any agent can reference a `claude-*`
    model string by name:

    ```typescript
    import {LLMRegistry, LlmAgent} from '@google/adk';
    import {Claude} from '@google/adk-integrations';

    LLMRegistry.register(Claude);

    export const rootAgent = new LlmAgent({
      name: 'claude_agent',
      model: 'claude-sonnet-4-6@default',
      instruction: 'You are a helpful assistant.',
    });
    ```

=== "Go"

    Set `Backend` to `BackendVertex`. When `Project` and `Location` are empty,
    the model reads `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`, and
    uses ADC for credentials.

    ```go
    llm, err := anthropicmodel.NewModel(ctx, "claude-sonnet-4-6", anthropicmodel.ClientConfig{
    	Backend: anthropicmodel.BackendVertex,
    })
    if err != nil {
    	log.Fatal(err)
    }
    ```

=== "Java"

    Configure the `AnthropicClient` with a `VertexBackend`:

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.vertex.backends.VertexBackend;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude;
    import com.google.auth.oauth2.GoogleCredentials;
    import java.io.IOException;

    public class ClaudeAgentPlatformAgent {

      public static LlmAgent createAgent() throws IOException {
        AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
            .backend(
                VertexBackend.builder()
                    .project("your-project-id")
                    .region("global")
                    .googleCredentials(GoogleCredentials.getApplicationDefault())
                    .build())
            .build();

        return LlmAgent.builder()
            .name("claude_agent")
            .model(new Claude("claude-sonnet-4-6", anthropicClient))
            .instruction("You are a helpful assistant.")
            .build();
      }
    }
    ```

=== "Kotlin"

    Pass `VertexCredentials` to the `Claude` constructor. Unset values fall back
    to `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and ADC.

    ```kotlin
    import com.google.adk.kt.agents.Instruction
    import com.google.adk.kt.agents.LlmAgent
    import com.google.adk.kt.models.VertexCredentials
    import com.google.adk.kt.models.anthropic.Claude

    val rootAgent =
      LlmAgent(
        name = "claude_agent",
        model = Claude(name = "claude-sonnet-4-6", vertexCredentials = VertexCredentials()),
        instruction = Instruction("You are a helpful assistant."),
      )
    ```

## Configure extended thinking

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.34.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

Extended thinking lets Claude reason through a problem before it responds,
which can help on multi-step tasks such as planning, analysis, and choosing
between tools. You configure it with the `thinking_budget` field of
the standard thinking configuration:

| `thinking_budget` | Behavior |
| :--- | :--- |
| Negative, such as `-1` | **Adaptive thinking.** Claude chooses how much to reason for each request. |
| `0` | **No thinking.** Claude responds without extended thinking. |
| Positive | **Manual thinking.** Claude uses up to this many tokens to reason. For minimum and maximum budgets, see Anthropic's extended thinking documentation. |

Use adaptive thinking unless you need a fixed token budget. Some newer Claude
models accept only adaptive thinking; see Anthropic's extended thinking 
documentation for the model you use. When you set a thinking configuration, 
you must set a `thinking_budget` value.

To control how much reasoning effort Claude spends, set the **effort** level:
`low`, `medium`, `high`, `xhigh`, or `max`. Claude doesn't support the
standard `thinking_level` setting; use effort instead. While thinking or effort
is active, ADK doesn't send `temperature`, `top_p`, or `top_k` to Claude.

=== "Python"

    Set `effort` on `AnthropicGenerateContentConfig`, available in ADK Python
    v2.4.0 and later:

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models import AnthropicGenerateContentConfig
    from google.genai import types

    root_agent = LlmAgent(
        name="claude_reasoning_agent",
        model="claude-sonnet-4-6",
        instruction="You are a helpful assistant.",
        generate_content_config=AnthropicGenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            effort="high",
        ),
    )
    ```

    Setting `thinking_level` on `AnthropicGenerateContentConfig` raises a
    validation error. On a plain `types.GenerateContentConfig`, ADK ignores it
    and logs a warning.

=== "Go"

    Set the thinking budget on the agent's `GenerateContentConfig`, and the
    effort level on the model's `ClientConfig`:

    ```go
    llm, err := anthropicmodel.NewModel(ctx, "claude-sonnet-4-6", anthropicmodel.ClientConfig{
    	Effort: anthropicmodel.EffortHigh,
    })
    if err != nil {
    	log.Fatal(err)
    }

    agent, err := llmagent.New(llmagent.Config{
    	Name:        "claude_reasoning_agent",
    	Model:       llm,
    	Instruction: "You are a helpful assistant.",
    	GenerateContentConfig: &genai.GenerateContentConfig{
    		ThinkingConfig: &genai.ThinkingConfig{ThinkingBudget: genai.Ptr[int32](-1)},
    	},
    })
    ```

=== "Kotlin"

    Set the thinking budget on the agent's `GenerateContentConfig`, and the
    effort level on the `Claude` constructor:

    ```kotlin
    import com.anthropic.models.messages.OutputConfig
    import com.google.adk.kt.agents.Instruction
    import com.google.adk.kt.agents.LlmAgent
    import com.google.adk.kt.models.anthropic.Claude
    import com.google.adk.kt.types.GenerateContentConfig
    import com.google.adk.kt.types.ThinkingConfig

    val rootAgent =
      LlmAgent(
        name = "claude_reasoning_agent",
        model = Claude(name = "claude-sonnet-4-6", effort = OutputConfig.Effort.HIGH),
        instruction = Instruction("You are a helpful assistant."),
        generateContentConfig =
          GenerateContentConfig(thinkingConfig = ThinkingConfig(thinkingBudget = -1)),
      )
    ```

ADK returns Claude's reasoning as thought parts in the response, and preserves
thinking blocks and their signatures across tool calls within a turn,
as the Anthropic API requires.

## Advanced applications

ADK supports some advanced uses of Anthropic models, including prompt caching
and accessing models through the LiteLLM library.

### Cache prompts

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.8.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

Agents with long instructions or many tools send the same prompt prefix on
every request. Claude prompt caching stores that prefix so later requests
reuse it, which can reduce cost and latency. ADK places cache breakpoints on the
tool declarations, the system instruction, and the latest conversation
content.

Anthropic supports a 5-minute cache lifetime, which is the default, and a 1-hour
cache lifetime. Use the 1-hour lifetime when requests to the same agent are
usually more than 5 minutes apart.

=== "Python"

    Set a `ContextCacheConfig` on your `App`. A `ttl_seconds` value of 3600 or
    more selects the 1-hour cache. For more on this configuration, see
    [Context caching](/context/caching/).

    ```python
    from google.adk.agents.context_cache_config import ContextCacheConfig
    from google.adk.apps.app import App

    app = App(
        name="claude_caching_app",
        root_agent=root_agent,
        context_cache_config=ContextCacheConfig(
            min_tokens=2048,  # Skip caching for short prompts.
            ttl_seconds=600,
        ),
    )
    ```

=== "Go"

    Set `PromptCache` on the model's `ClientConfig`. Set `TTL` to
    `PromptCacheTTL1h` to select the 1-hour cache.

    ```go
    llm, err := anthropicmodel.NewModel(ctx, "claude-sonnet-4-6", anthropicmodel.ClientConfig{
    	PromptCache: &anthropicmodel.PromptCacheConfig{TTL: anthropicmodel.PromptCacheTTL5m},
    })
    ```

=== "Kotlin"

    Set a `ContextCacheConfig` on your `App`. A `ttl` of one hour or more
    selects the 1-hour cache.

    ```kotlin
    @OptIn(ExperimentalContextCachingFeature::class)
    import com.google.adk.kt.agents.ContextCacheConfig
    import com.google.adk.kt.apps.App
    import kotlin.time.Duration.Companion.minutes

    val app =
      App(
        appName = "claude_caching_app",
        rootAgent = rootAgent,
        contextCacheConfig = ContextCacheConfig(minTokens = 2048, ttl = 10.minutes),
      )
    ```

### Use Claude through LiteLLM

In Python, you can also reach Claude through the `LiteLlm` connector with an
`anthropic/` model string. Use this path if your application already routes
models through LiteLLM. For setup, see
[LiteLLM](/agents/models/litellm/#anthropic-thinking-blocks).

## Configuration options

The Claude model classes accept the following options:

=== "Python"

    These options apply to both `AnthropicLlm` and `Claude`.

    | Option | Type | Default | Description |
    | :--- | :--- | :--- | :--- |
    | `model` | `str` | `"claude-sonnet-4-20250514"` (`AnthropicLlm`), `"claude-3-5-sonnet-v2@20241022"` (`Claude`) | The Claude model ID. |
    | `max_tokens` | `int` | `8192` | Maximum output tokens when the request sets no `max_output_tokens`. |
    | `client` | `AsyncAnthropic` or `AsyncAnthropicVertex` | `None` | A preconfigured Anthropic client. The `Claude` class requires an `AsyncAnthropicVertex` client. |

=== "TypeScript"

    | Option | Type | Default | Description |
    | :--- | :--- | :--- | :--- |
    | `model` | `string` | `'claude-sonnet-4-6@default'` | The Claude model ID on Agent Platform. |
    | `maxTokens` | `number` | `8192` | Maximum output tokens when the request sets no `maxOutputTokens`. |

=== "Go"

    Selected `ClientConfig` fields:

    | Option | Type | Default | Description |
    | :--- | :--- | :--- | :--- |
    | `Backend` | `Backend` | `BackendAnthropic` | The serving backend: `BackendAnthropic` or `BackendVertex`. |
    | `APIKey` | `string` | `ANTHROPIC_API_KEY` | Anthropic API key for `BackendAnthropic`. |
    | `Project` | `string` | `GOOGLE_CLOUD_PROJECT` | Google Cloud project for `BackendVertex`. |
    | `Location` | `string` | `GOOGLE_CLOUD_LOCATION` | Google Cloud region for `BackendVertex`. |
    | `MaxTokens` | `int` | `8192` | Maximum output tokens when the request sets no `MaxOutputTokens`. |
    | `MaxRetries` | `*int` | `2` | Number of retries the Anthropic SDK makes for failed requests. |
    | `Effort` | `Effort` | Model default | Reasoning effort level. |
    | `PromptCache` | `*PromptCacheConfig` | `nil` | Enables prompt caching when set. |

    For the full list, see the
    [`anthropicmodel` package reference](https://pkg.go.dev/google.golang.org/adk/v2/model/anthropicmodel).

=== "Java"

    | Option | Type | Default | Description |
    | :--- | :--- | :--- | :--- |
    | `modelName` | `String` | Required | The Claude model ID. |
    | `anthropicClient` | `AnthropicClient` | Required | The Anthropic client, configured for the Anthropic API or a `VertexBackend`. |
    | `maxTokens` | `int` | `8192` | Maximum output tokens for each request. |

=== "Kotlin"

    | Option | Type | Default | Description |
    | :--- | :--- | :--- | :--- |
    | `name` | `String` | Required | The Claude model ID. |
    | `apiKey` | `String?` | `ANTHROPIC_API_KEY` | Anthropic API key. Selects the Anthropic API backend. |
    | `vertexCredentials` | `VertexCredentials` | None | Project, location, and credentials. Selects the Agent Platform backend. |
    | `client` | `AnthropicClient` | None | A preconfigured Anthropic client, used instead of `apiKey` or `vertexCredentials`. |
    | `maxTokens` | `Int` | `8192` | Maximum output tokens when the request sets none. |
    | `effort` | `OutputConfig.Effort?` | `null` | Reasoning effort level. |

## Limitations

-   **Live API:** Claude models don't support ADK bidirectional streaming with
    the Live API.
-   **TypeScript:** The `Claude` class returns complete responses without
    streaming, and accepts text, function call, and function response parts
    only. For the full list, see the
    [Claude integration guide](https://github.com/google/adk-js/blob/main/docs/guides/integrations/models/anthropic_llm/index.md#limitations).

## Next steps

-   [Agent Platform hosted models](/agents/models/agent-platform/): Use other
    models deployed on Agent Platform.
-   [LiteLLM](/agents/models/litellm/): Connect to models from other
    providers.
-   [Context caching](/context/caching/): Learn more about cache settings.
