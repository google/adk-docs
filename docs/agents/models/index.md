# AI Models for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

Agent Development Kit (ADK) is designed for flexibility, allowing you to
integrate various Large Language Models (LLMs) into your agents. This section
details how to leverage Gemini and integrate other popular models effectively,
including those hosted externally or running locally.

ADK provides several mechanisms for model integration:

1. **Direct String / Registry:** For models tightly integrated with Google
   Cloud, such as Gemini models accessed via Google AI Studio or Agent Platform,
   or models hosted on Agent Platform endpoints. You access these models by
   providing the model name or endpoint resource string and ADK's internal
   registry resolves this string to the appropriate backend client.

      *  [Gemini models](/agents/models/google-gemini/)
      *  [Claude models](/agents/models/anthropic/)
      *  [Agent Platform hosted models](/agents/models/agent-platform/)

2. **Model connectors:** For broader compatibility, especially models outside
   the Google ecosystem or those requiring specific client configurations, such
   as models accessed via Apigee or LiteLLM. You instantiate a specific wrapper
   class, such as `ApigeeLlm` or `LiteLlm`, and pass this object as the `model`
   parameter to your `LlmAgent`.

      *  [Apigee models](/agents/models/apigee/)
      *  [LiteLLM models](/agents/models/litellm/)
      *  [Ollama model hosting](/agents/models/ollama/)
      *  [vLLM model hosting](/agents/models/vllm/)
      *  [LiteRT-LM model hosting](/agents/models/litert-lm/)

3. **[Model routing](/agents/models/routing/):** For dynamically selecting
   between multiple models at runtime using a router function, with automatic
   failover on error.

## Register model factories in Go

In Go, `llmagent.Config.Model` takes a `model.LLM` instance. You can construct
the provider's model directly, or use `model.NewLLM` after explicitly
registering a factory. Importing a provider package does not register it.

Register each pattern once during initialization. For example:

```go
import (
	"context"

	"google.golang.org/adk/v2/model"
	"google.golang.org/adk/v2/model/gemini"
)

func init() {
	model.Register("^gemini-.*$", func(ctx context.Context, name string) (model.LLM, error) {
		return gemini.NewModel(ctx, name, nil)
	})
}

func newRegisteredModel(ctx context.Context) (model.LLM, error) {
	return model.NewLLM(ctx, "gemini-2.5-flash")
}
```

`NewLLM` requires exactly one matching pattern. It returns an error when no
factory matches or when several patterns match, so keep patterns distinct.
`Register` panics for an invalid regular expression or a duplicate pattern.
