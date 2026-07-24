# OpenAI models for ADK agents

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-go">Go v2.1.0</span><span class="lst-preview">Experimental</span>
</div>

!!! example "Experimental"

    The `openaimodel` package is experimental and its behavior may change or be removed in the future. We welcome your
		[feedback](https://github.com/google/adk-go/issues/new?template=feature_request.md)!

You can use OpenAI models (such as GPT-4o and GPT-4o Mini) with ADK. This allows for easy integration of OpenAI's language models into ADK agents.

## Get started

The `openaimodel` package provides a client for interacting with OpenAI's API. It implements the `model.LLM` interface, making it compatible with providers that expose the OpenAI Responses API surface.
The following code example shows a basic implementation for using OpenAI models in your agents:

=== "Go"

    ```go
    import (
    	"github.com/openai/openai-go/v3"
    	"google.golang.org/adk/v2/agent/llmagent"
    	"google.golang.org/adk/v2/model/openaimodel"
    )

    // Instantiate the model
    llm, err := openaimodel.NewModel(ctx, openai.ChatModelGPT4oMini, &openaimodel.ClientConfig{})
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

## OpenAI model authentication

When using OpenAI models, you must provide an API key to authenticate with the OpenAI API. The most direct way to provide this information is to use environment variables or an `.env` file.

The `openaimodel` package also supports OpenAI-compatible endpoints (such as local models served via Ollama, LM Studio, or vLLM) by configuring the base URL.

=== "OpenAI API"

    ```bash
    # .env configuration file
    OPENAI_API_KEY="PASTE_YOUR_OPENAI_API_KEY_HERE"
    ```

=== "OpenAI-compatible Endpoint"

    ```bash
    # .env configuration file
    OPENAI_API_KEY="api-key-if-required"
    OPENAI_BASE_URL="http://localhost:11434/v1" # example: local Ollama endpoint
    ```

## Configuration Options

The `ClientConfig` provides several options for configuring the client:

- `APIKey`: Your OpenAI API key.
- `BaseURL`: Custom endpoint URL, which can be useful for OpenAI-compatible endpoints.
- `HTTPClient`: A custom `*http.Client`.
- `Options`: Advanced `openai-go` request options (`[]option.RequestOption`).

If `APIKey` or `BaseURL` are left empty, they will automatically fall back to the `OPENAI_API_KEY` and `OPENAI_BASE_URL` environment variables, handled by the default behavior of the underlying `openai-go` SDK.
