# LiteRT-LM model host for ADK agents

Supported in ADKPython v0.1.0Kotlin v0.4.0

You can use the [LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM) library to efficiently run language models locally on various compute devices without requiring specialized processors such as graphics processing units (GPU) or tensor processing units (TPU). LiteRT-LM supports many models, including Google Gemma models as well as third-party models. This guide provides instructions for setting up LiteRT-LM with ADK for the following languages:

- [Python](#python)
- [Kotlin](#kotlin)

## Python

These instructions describe how to use LiteRT-LM server with ADK in Python with a Gemma open weights model, including using LiteRT-LM 's local hosting model server `lit`.

### Install resources

You need to download a model to use with LiteRT-LM, and the `lit` CLI tool to help you find a model download it.

#### Install `lit` CLI tool

Download and install the `lit` CLI tool by following these [instructions](https://github.com/google-ai-edge/LiteRT-LM?tab=readme-ov-file#desktop-cli-lit) in the LiteRT-LM GitHub repository.

#### Download a model

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

### Configure your agent

Configure your agent to connect to LiteRT-LM and a hosted model. When running Gemma models with LiteRT-LM, you configure a `Gemini` model class with the model identifier and local network address.

To use LiteRT-LM with ADK and a Gemma model:

1. Set `base_url` to the LiteRT-LM server URL, for example: `localhost:8001`.
1. Set `model` to the LiteRT-LM model name, for example: `gemma3n-e2b`.

The following example code shows how to configure an agent to connect to the locally hosted LiteRT-LM instance serving the Gemma model configuration described above:

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

### Running the LiteRT-LM server

The LiteRT-LM server is a separate process that serves LiteRT-LM models. It is started by the LiteRT-LM CLI tool `lit`.

#### Run the server

After downloading a model, start the LiteRT-LM server locally by running the following command:

```bash
lit serve --port 8001
```

Local Server Port Number

You may choose any port number for the LiteRT-LM server as long as it matches the `base_url` you set in the `Gemini` class in your agent code.

#### Debugging

To see incoming requests to the LiteRT-LM server and the exact input sent to the model, use the `--verbose` flag:

```bash
lit serve --port 8001 --verbose
```

## Kotlin

These instructions describe how to use LiteRT-LM with ADK in Kotlin using the `com.google.adk.kt.litertlm` package.

### Install resources

You need to download a model to use with LiteRT-LM, and the `litert-lm` CLI tool to help you find a model download it.

#### Install LiteRT-LM CLI

Prerequisites: Python 3.10 or higher

To install the CLI, run:

```bash
pip install --upgrade litert-lm
```

For additional installation methods, such as using uv, see [LiteRT-LM CLI Installation Guide](https://developers.google.com/edge/litert-lm/cli/installation).

#### Download a model

Download a model compatible with LiteRT-LM to use the `litert-lm` CLI tool. Use `litert-lm` to download models directly from Hugging Face:

```bash
litert-lm import \
  --from-huggingface-repo litert-community/gemma-4-E2B-it-litert-lm \
  gemma-4-E2B-it.litertlm
```

Once downloaded, the model is stored locally at:

```text
~/.litert-lm/models/gemma-4-E2B-it.litertlm/model.litertlm
```

For more details about `litert-lm`, refer to the [LiteRT-LM CLI Usage Guide](https://developers.google.com/edge/litert-lm/cli/usage).

### Add dependencies

ADK Kotlin works with LiteRT-LM through an adapter package, `com.google.adk:google-adk-kotlin-litertlm`.

In your `build.gradle.kts`, add `com.google.adk:google-adk-kotlin-litertlm` and `com.google.ai.edge.litertlm:litertlm-jvm` to your dependencies:

```text
repositories {
    mavenCentral()
    google()
}

dependencies {
    implementation("com.google.adk:google-adk-kotlin-core:0.5.0")
    implementation("com.google.adk:google-adk-kotlin-litertlm:0.5.0")
    implementation("com.google.ai.edge.litertlm:litertlm-jvm:0.13.1")
    // other dependencies...
}
```

### Configure agent model

Run a local model for your agent with LiteRT-LM by configuring a `LiteRtLmModel` object as part of your `LlmAgent` object. If you do not already have a ADK Kotlin project, follow the [Kotlin Quickstart for ADK](/get-started/kotlin/) getting started guide. The following code example shows you how to configure an `LlmAgent`, and set the `model` parameter to a `LiteRtLmModel`:

```text
 object HelloTimeAgent {

    // Get model path from environment variable.
    private val modelPath: String by lazy {
        System.getenv("LITERT_LM_MODEL_PATH")
            ?: throw IllegalStateException(
                "LITERT_LM_MODEL_PATH environment variable must be set pointing to a .litertlm file."
            )
    }

    @JvmField
    val rootAgent =
        LlmAgent(
            name = "hello_time_agent",
            description = "Tells the current time in a specified city.",
            model =
                LiteRtLmModel.create(
                    EngineConfig(modelPath = modelPath, backend = Backend.CPU())
                ),
            instruction =
                Instruction(
                    "You are a helpful assistant that tells the current time in a city. " +
                        "Use the 'getCurrentTime' tool for this purpose."
                ),
            tools = TimeService().generatedTools(),
        )
}
```

In this example, the path to the LiteRT-LM model file is read from the environment variable `LITERT_LM_MODEL_PATH`. The model will be run on the CPU. You can run the model on a GPU by setting `backend = Backend.GPU()`.

When you run the agent, set `LITERT_LM_MODEL_PATH` to the location of the model file, for example: `~/.litert-lm/models/gemma-4-E2B-it.litertlm/model.litertlm`.

### Run your agent

If you followed the [Kotlin Quickstart for ADK](/get-started/kotlin/) with the above modifications, you can run your ADK agent using the command-line REPL with the environment variable `LITERT_LM_MODEL_PATH` set to the path of the model file:

```bash
LITERT_LM_MODEL_PATH=~/.litert-lm/models/gemma-4-E2B-it.litertlm/model.litertlm ./gradlew run
```

Example interaction:

```text
Agent hello_time_agent is ready. Type 'exit' to quit.

You > what's your name?

hello_time_agent > I am Gemma 4, a Large Language Model developed by Google DeepMind.

You > what time is it in paris?

hello_time_agent > calls tool: getCurrentTime

hello_time_agent > The time in Paris is 10:30 am.
```
