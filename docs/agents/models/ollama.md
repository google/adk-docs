# Ollama model host for ADK agents

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

[Ollama](https://ollama.com/) allows you to host and run open-source models
locally.

## Model choice

If your agent is relying on tools, please make sure that you select a model with
tool support from [Ollama website](https://ollama.com/search?c=tools).

For reliable results, we recommend using a decent-sized model with tool support.

The tool support for the model can be checked with the following command:

```bash
ollama show mistral-small3.1
  Model
    architecture        mistral3
    parameters          24.0B
    context length      131072
    embedding length    5120
    quantization        Q4_K_M

  Capabilities
    completion
    vision
    tools
```

You are supposed to see `tools` listed under capabilities.

You can also look at the template the model is using and tweak it based on your
needs.

```bash
ollama show --modelfile llama3.2 > model_file_to_modify
```

For instance, the default template for the above model inherently suggests that
the model shall call a function all the time. This may result in an infinite
loop of function calls.

```
Given the following functions, please respond with a JSON for a function call
with its proper arguments that best answers the given prompt.

Respond in the format {"name": function name, "parameters": dictionary of
argument name and its value}. Do not use variables.
```

You can swap such prompts with a more descriptive one to prevent infinite tool
call loops.

For instance:

```
Review the user's prompt and the available functions listed below.
First, determine if calling one of these functions is the most appropriate way to respond. A function call is likely needed if the prompt asks for a specific action, requires external data lookup, or involves calculations handled by the functions. If the prompt is a general question or can be answered directly, a function call is likely NOT needed.

If you determine a function call IS required: Respond ONLY with a JSON object in the format {"name": "function_name", "parameters": {"argument_name": "value"}}. Ensure parameter values are concrete, not variables.

If you determine a function call IS NOT required: Respond directly to the user's prompt in plain text, providing the answer or information requested. Do not output any JSON.
```

Then you can create a new model with the following command:

```bash
ollama create llama3.2-modified -f model_file_to_modify
```

## Using ollama_chat provider

The LiteLLM wrapper can be used to create agents with Ollama-hosted models.

```py
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_agent",
    description=(
        "hello world agent that can roll a dice of 8 sides and check prime"
        " numbers."
    ),
    instruction="""
      You roll dice and answer questions about the outcome of the dice rolls.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

**It is important to set the provider `ollama_chat` instead of `ollama`. Using
`ollama` will result in unexpected behaviors such as infinite tool call loops
and ignoring previous context.**

While `api_base` can be provided inside LiteLLM for generation, LiteLLM library
is calling other APIs relying on the env variable instead as of v1.65.5 after
completion. So at this time, we recommend setting the env variable
`OLLAMA_API_BASE` to point to the ollama server.

```bash
export OLLAMA_API_BASE="http://localhost:11434"
adk web
```
