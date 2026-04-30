# LiteRT-LM model host for ADK agents

Supported in ADKPython v0.1.0

[LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM) is a C++ library to efficiently run language models across edge platforms. On desktop (Linux, macOS, and Windows), ADK integrates with LiteRT-LM-hosted models through the LiteRT-LM server launched by the LiteRT-LM CLI `lit`.

## Get started

LiteRT-LM works with the `Gemini` class. You only have to set the `base_url` and `model` parameters.

1. Set `base_url` to the LiteRT-LM server URL, for example: `localhost:8001`.
1. Set `model` to the LiteRT-LM model name, for example: `gemma3n-e2b`.

```py
from google.adk.agents import Agent
from google.adk.models import Gemini

root_agent = Agent(
    model=Gemini(
        model="gemma3n-e2b",
        base_url="http://localhost:8001",
    ),
    name="dice_agent",
    description=(
        "hello world agent that can roll a die of 8 sides and check prime"
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

Then run the agent as usual:

```bash
adk web
```

## Running the LiteRT-LM Server

The LiteRT-LM server is a separate process that serves LiteRT-LM models. It is started by the LiteRT-LM CLI tool `lit`.

### Download the `lit` CLI tool

Download the `lit` CLI tool by following these [instructions](https://github.com/google-ai-edge/LiteRT-LM?tab=readme-ov-file#desktop-cli-lit) in the LiteRT-LM GitHub repository.

### Download a model

Before you start the server, you need to download a model. You'll need a *Hugging Face* user access token to download a LiteRT-LM model using `lit`. You can get a token for your *Hugging Face* account [here](https://huggingface.co/settings/tokens).

To see a list of models available for download, use the `lit list` command:

```bash
lit list --show_all
```

Download a model using the `lit pull` command:

```bash
export HUGGING_FACE_HUB_TOKEN="**your Hugging Face token**"
lit pull gemma3n-e2b
```

### Run the server

After downloading a model, start the LiteRT-LM server locally by running the following command:

```bash
lit serve --port 8001
```

Local Server Port Number

You may choose any port number for the LiteRT-LM server as long as it matches the `base_url` you set in the `Gemini` class in your agent code.

### Debugging

To see incoming requests to the LiteRT-LM server and the exact input sent to the model, use the `--verbose` flag:

```bash
lit serve --port 8001 --verbose
```
