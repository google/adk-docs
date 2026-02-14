# Claude models for ADK agents

Supported in ADKJava v0.2.0

You can integrate Anthropic's Claude models directly using an Anthropic API key or from a Vertex AI backend into your Java ADK applications by using the ADK's `Claude` wrapper class. You can also access Anthropic models through Google Cloud Vertex AI services. For more information, see the [Third-Party Models on Vertex AI](/adk-docs/agents/models/vertex/#third-party-models-on-vertex-ai-eg-anthropic-claude) section. You can also use Anthropic models through the [LiteLLM](/adk-docs/agents/models/litellm/) library for Python.

## Get started

The following code examples show a basic implementation for using Gemini models in your agents:

```java
public static LlmAgent createAgent() {

  AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
      .apiKey("ANTHROPIC_API_KEY")
      .build();

  Claude claudeModel = new Claude(
      "claude-3-7-sonnet-latest", anthropicClient
  );

  return LlmAgent.builder()
      .name("claude_direct_agent")
      .model(claudeModel)
      .instruction("You are a helpful AI assistant powered by Anthropic Claude.")
      .build();
}
```

## Prerequisites

1. **Dependencies:**

   - **Anthropic SDK Classes (Transitive):** The Java ADK's `com.google.adk.models.Claude` wrapper relies on classes from Anthropic's official Java SDK. These are typically included as *transitive dependencies*. For more information, see the [Anthropic Java SDK](https://github.com/anthropics/anthropic-sdk-java).

1. **Anthropic API Key:**

   - Obtain an API key from Anthropic. Securely manage this key using a secret manager.

## Example implementation

Instantiate `com.google.adk.models.Claude`, providing the desired Claude model name and an `AnthropicOkHttpClient` configured with your API key. Then, pass the `Claude` instance to your `LlmAgent`, as shown in the following example:

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // From Anthropic's SDK

public class DirectAnthropicAgent {

  private static final String CLAUDE_MODEL_ID = "claude-3-7-sonnet-latest"; // Or your preferred Claude model

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
