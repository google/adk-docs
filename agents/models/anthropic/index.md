# Claude models for ADK agents

Supported in ADKPython v0.1.0Java v0.2.0

You can use Anthropic's Claude models with ADK in both Python and Java. Choose the path that matches your language and backend below.

## Python

You can use Claude models from Python in the following ways:

- **Native, on Agent Platform:** Register the `Claude` wrapper and use a Claude model string. See [Anthropic Claude on Agent Platform](/agents/models/agent-platform/#anthropic-claude).
- **Direct Anthropic API, via LiteLLM:** Use the `LiteLlm` connector with an Anthropic API key. See [LiteLLM](/agents/models/litellm/#anthropic-thinking-blocks).

## Java

In Java, you can integrate Claude models directly using an Anthropic API key or an Agent Platform backend with the ADK `Claude` wrapper class. You can also access Claude through Google Cloud Agent Platform services; see [Third-Party Models on Agent Platform](/agents/models/agent-platform/#anthropic-claude).

### Get started

The following code examples show a basic implementation for using Claude models in your agents:

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

### Prerequisites

- **Dependencies:** The Java ADK's `com.google.adk.models.Claude` wrapper relies on classes from Anthropic's official Java SDK, typically included as *transitive dependencies*. For more information, see the [Anthropic Java SDK](https://github.com/anthropics/anthropic-sdk-java).
- **Anthropic API key:** Obtain an API key from Anthropic, and securely manage it using a secret manager.

### Example implementation

Instantiate `com.google.adk.models.Claude`, providing the desired Claude model name and an `AnthropicOkHttpClient` configured with your API key. Then, pass the `Claude` instance to your `LlmAgent`, as shown in the following example:

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
