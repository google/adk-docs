# Claude models for ADK agents

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

You can use Anthropic's Claude models with ADK in both Python and Java. Choose
the path that matches your language and backend below.

## Python

You can use Claude models from Python in the following ways:

- **Native, on Agent Platform:** Pass a Claude model string directly; ADK's
  registry routes it to the `Claude` wrapper. See [Anthropic Claude on Agent
  Platform](/agents/models/agent-platform/#anthropic-claude).
- **Direct Anthropic API, via LiteLLM:** Use the `LiteLlm` connector with an
  Anthropic API key. See
  [LiteLLM](/agents/models/litellm/#anthropic-thinking-blocks).

## Java

In Java, you can integrate Claude models directly using an Anthropic API key or
an Agent Platform backend with the ADK `Claude` wrapper class. You can also
access Claude through Google Cloud Agent Platform services; see [Third-Party
Models on Agent Platform](/agents/models/agent-platform/#anthropic-claude).

### Get started

The following code examples show a basic implementation for using Claude models
in your agents:

```java
--8<-- "examples/inline/java/agents/models/anthropic/001-get-started.java"
```

### Prerequisites

- **Dependencies:** The Java ADK's `com.google.adk.models.Claude` wrapper relies
  on classes from Anthropic's official Java SDK, typically included as
  *transitive dependencies*. For more information, see the [Anthropic Java
  SDK](https://github.com/anthropics/anthropic-sdk-java).
- **Anthropic API key:** Obtain an API key from Anthropic, and securely manage
  it using a secret manager.

### Example implementation

Instantiate `com.google.adk.models.Claude`, providing the desired Claude model
name and an `AnthropicOkHttpClient` configured with your API key. Then, pass the
`Claude` instance to your `LlmAgent`, as shown in the following example:

```java
--8<-- "examples/inline/java/agents/models/anthropic/002-example-implementation.java"
```
