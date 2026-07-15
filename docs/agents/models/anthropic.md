# Claude models for ADK agents

<div class="language-support-tag" title="Available for Java. Python support for direct Anthropic API (non-Vertex) is via LiteLLM.">
   <span class="lst-supported">Supported in ADK</span><span class="lst-java">Java v0.2.0</span>
</div>

You can integrate Anthropic's Claude models directly using an Anthropic API key
or from an Agent Platform backend into your Java ADK applications by using the ADK's
`Claude` wrapper class. You can also access Anthropic models through
Google Cloud Agent Platform services. For more information, see the
[Third-Party Models on Agent Platform](/agents/models/agent-platform/#anthropic-claude)
section. You can also use Anthropic models through the
[LiteLLM](/agents/models/litellm/) library for Python.

## Get started

The following code examples show a basic implementation for using Anthropic models
in your agents:

```java
public static LlmAgent createAgent() {

  AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
      .apiKey("ANTHROPIC_API_KEY")
      .build();

  Claude claudeModel = new Claude(
      "claude-sonnet-4-6", anthropicClient
  );

  return LlmAgent.builder()
      .name("claude_direct_agent")
      .model(claudeModel)
      .instruction("You are a helpful AI assistant powered by Anthropic Claude.")
      .build();
}
```

## Prerequisites

1.  **Dependencies:**
    *   **Anthropic SDK Classes (Transitive):** The Java ADK's `com.google.adk.models.Claude`
    wrapper relies on classes from Anthropic's official Java SDK. These are typically included
    as *transitive dependencies*. For more information, see the
    [Anthropic Java SDK](https://github.com/anthropics/anthropic-sdk-java).

2.  **Anthropic API Key:**
    *   Obtain an API key from Anthropic. Securely manage this key using a secret manager.

## Example implementation

Instantiate `com.google.adk.models.Claude`, providing the desired Claude model name and
an `AnthropicOkHttpClient` configured with your API key. Then, pass the `Claude` instance
to your `LlmAgent`, as shown in the following example:

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // From Anthropic's SDK

public class DirectAnthropicAgent {

  private static final String CLAUDE_MODEL_ID = "claude-sonnet-4-6"; // Or your preferred Claude model

  public static LlmAgent createAgent() {

    // It's recommended to load sensitive keys from a secure config
    AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
        .apiKey("ANTHROPIC_API_KEY")
        .build();

    Claude claudeModel = new Claude(
        CLAUDE_MODEL_ID,
        anthropicClient
    );

    return LlmAgent.builder()
        .name("claude_direct_agent")
        .model(claudeModel)
        .instruction("You are a helpful AI assistant powered by Anthropic Claude.")
        // ... other LlmAgent configurations
        .build();
  }

  public static void main(String[] args) {
    try {
      LlmAgent agent = createAgent();
      System.out.println("Successfully created direct Anthropic agent: " + agent.name());
    } catch (IllegalStateException e) {
      System.err.println("Error creating agent: " + e.getMessage());
    }
  }
}
```

### Anthropic reasoning and `thinking_blocks`

When you use Anthropic's Claude models (such as Claude 3.7 Sonnet) through the
`LiteLlm` connector, ADK provides full support for their structured reasoning
feature, known as "thinking blocks". ADK automatically extracts and preserves
the `thinking_blocks` and their signatures across tool call boundaries. Use
this automatic extraction to maintain Claude's reasoning in ADK agents across
complex multi-turn interactions.

#### Adaptive thinking and signatures

For newer Anthropic reasoning models utilizing dynamic adaptive thinking
with effort levels instead of fixed token budgets:

* **Omitted Content:** Anthropic hides the raw thought tokens by default on
  these models to reduce payload size and latency.
* **State Management:** ADK automatically captures the encrypted `signature`
  field from the API response and routes it back through the LiteLLM
  connector on the next turn.
* **Developer Impact:** You do not need to build custom state-tracking or
  session management to maintain the model's reasoning loop when adaptive
  thinking is active.
