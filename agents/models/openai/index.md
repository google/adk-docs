# OpenAI models for ADK agents

Supported in ADKGo v2.1.0Experimental

Experimental

The `openaimodel` package is experimental and its behavior may change or be removed in the future. We welcome your [feedback](https://github.com/google/adk-go/issues/new?template=feature_request.md)!

You can use OpenAI models with ADK. How you connect depends on the language:

- **Go — native support:** ADK Go provides a direct `openaimodel` package that implements the `model.LLM` interface, targeting the OpenAI Responses API. [Get started](#get-started).
- **Python — via LiteLLM:** ADK Python accesses OpenAI models (and many other providers) through the LiteLLM connector. See [LiteLLM](/agents/models/litellm/).

## Get started

The `openaimodel` package provides a client for interacting with OpenAI's API. It implements the `model.LLM` interface, making it compatible with providers that expose the OpenAI Responses API surface. The following code example shows a basic implementation for using OpenAI models in your agents:

```go
import (
    "context"
    "log"

    "github.com/openai/openai-go/v3"
    "google.golang.org/adk/v2/agent/llmagent"
    "google.golang.org/adk/v2/model/openaimodel"
)

// Instantiate the model
llm, err := openaimodel.NewModel(context.Background(), openai.ChatModelGPT4oMini, &openaimodel.ClientConfig{})
if err != nil {
  log.Fatal(err)
}

// Create the agent
agent, err := llmagent.New(llmagent.Config{
  Name:        "openai_agent",
  Model:       llm,
  Instruction: "You are a helpful AI assistant.",
})
if err != nil {
  log.Fatal(err)
}
```

For a complete, runnable sample, see [examples/openai/](https://github.com/google/adk-go/tree/main/examples/openai) in the ADK Go repository.

## Supported features

- Text generation (streaming and non-streaming)
- Function (tool) calling
- Structured output via `OutputSchema` (JSON schema)
- Reasoning models (e.g. o-series), including reasoning-token accounting
- Token logprobs

## Limitations

- **Text only** — multimodal input (images, audio, files) is not supported.
- **Function tools only** — built-in tools (Google Search, code execution, etc.) are not supported.
- **Structured output uses OpenAI strict mode** — every field declared in an `OutputSchema` is treated as required.
- Some `GenerateContentConfig` options return an error rather than being silently ignored: `TopK`, stop sequences, multiple candidates, frequency/presence penalties, request labels, and safety settings.

## Configuration options

The `ClientConfig` provides several options for configuring the client:

- `APIKey`: Your OpenAI API key.
- `BaseURL`: Custom endpoint URL, which can be useful for OpenAI-compatible endpoints.
- `HTTPClient`: A custom `*http.Client`.
- `Options`: Advanced `openai-go` request options (`[]option.RequestOption`).

If `APIKey` or `BaseURL` are left empty, they will automatically fall back to the `OPENAI_API_KEY` and `OPENAI_BASE_URL` environment variables, handled by the default behavior of the underlying `openai-go` SDK.

## OpenAI model authentication

When using OpenAI models, you must provide an API key to authenticate with the OpenAI API. The most direct way to provide this information is to use environment variables or an `.env` file.

The `openaimodel` package also supports OpenAI-compatible endpoints (such as local models served via Ollama, LM Studio, or vLLM) by configuring the base URL.

```bash
# .env configuration file
OPENAI_API_KEY="PASTE_YOUR_OPENAI_API_KEY_HERE"
```

```bash
# .env configuration file
OPENAI_API_KEY="api-key-if-required"
OPENAI_BASE_URL="http://localhost:11434/v1" # example: local Ollama endpoint
```
