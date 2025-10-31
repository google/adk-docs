# Build agents with Agent Config

The ADK Agent Config feature lets you build an ADK workflow without writing
code. An Agent Config uses a YAML format text file with a brief description of
the agent, allowing just about anyone to assemble and run an ADK agent. The
following is a simple example of an basic Agent Config definition:

```
name: assistant_agent
model: gemini-2.5-flash
description: A helper agent that can answer users' questions.
instruction: You are an agent to help answer users' various questions.
```

You can use Agent Config files to build more complex agents which can
incorporate Functions, Tools, Sub-Agents, and more. This page describes how to
build and run ADK workflows with the Agent Config feature. For detailed
information on the syntax and settings supported by the Agent Config format,
see the
[Agent Config syntax reference](/adk-docs/api-reference/agentconfig/).

!!! example "Experimental"
    The Agent Config feature is experimental and has some
    [known limitations](#known-limitations). We welcome your
    [feedback](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=agent%20config)!

## Get started

This section describes how to set up and start building agents with the ADK and
the Agent Config feature, including installation setup, building an agent, and
running your agent.

### Setup

You need to install the Google Agent Development Kit libraries, and provide an
access key for a generative AI model such as Gemini API. This section provides
details on what you must install and configure before you can run agents with
the Agent Config files.

!!! note
    The Agent Config feature currently only supports Gemini models. For more
    information about additional; functional restrictions, see
    [Known limitations](#known-limitations).

To setup ADK for use with Agent Config:

1.  Install the ADK Python libraries by following the
    [Installation](/adk-docs/get-started/installation/#python)
    instructions. *Python is currently required.* For more information, see the
    [Known limitations](?tab=t.0#heading=h.xefmlyt7zh0i).
1.  Verify that ADK is installed by running the following command in your
    terminal:

        adk --version

    This command should show the ADK version you have installed.

!!! Tip
    If the `adk` command fails to run and the version is not listed in step 2, make
    sure your Python environment is active. Execute `source .venv/bin/activate` in
    your terminal on Mac and Linux. For other platform commands, see the
    [Installation](/adk-docs/get-started/installation/#python)
    page.

### Build an agent

You build an agent with Agent Config using the `adk create` command to create
the project files for an agent, and then editing the `root_agent.yaml` file it
generates for you.

To create an ADK project for use with Agent Config:

1.  In your terminal window, run the following command to create a
    config-based agent:

        adk create --type=config my_agent

    This command generates a `my_agent/` folder, containing a
    `root_agent.yaml` file and an `.env` file.

1.  In the `my_agent/.env` file, set environment variables for your agent to
    access generative AI models and other services:

    1.  For Gemini model access through Google API, add a line to the
        file with your API key:

            GOOGLE_GENAI_USE_VERTEXAI=0
            GOOGLE_API_KEY=<your-Google-Gemini-API-key>

        You can get an API key from the Google AI Studio
        [API Keys](https://aistudio.google.com/app/apikey) page.

    1.  For Gemini model access through Google Cloud, add these lines to the file:

            GOOGLE_GENAI_USE_VERTEXAI=1
            GOOGLE_CLOUD_PROJECT=<your_gcp_project>
            GOOGLE_CLOUD_LOCATION=us-central1

        For information on creating a Cloud Project, see the Google Cloud docs
        for
        [Creating and managing projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects).

1.  Using text editor, edit the Agent Config file
    `my_agent/root_agent.yaml`, as shown below:

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
name: assistant_agent
model: gemini-2.5-flash
description: A helper agent that can answer users' questions.
instruction: You are an agent to help answer users' various questions.
```

You can discover more configuration options for your `root_agent.yaml` agent
configuration file by referring to the ADK
[samples repository](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+.yaml&type=code)
or the
[Agent Config syntax](/adk-docs/api-reference/agentconfig/)
reference.

### Run the agent

Once you have completed editing your Agent Config, you can run your agent using
the web interface, command line terminal execution, or API server mode.

To run your Agent Config-defined agent:

1.  In your terminal, navigate to the `my_agent/` directory containing the
    `root_agent.yaml` file.
1.  Type one of the following commands to run your agent:
    -   `adk web` - Run web UI interface for your agent.
    -   `adk run` - Run your agent in the terminal without a user
        interface.
    -   `adk api_server` - Run your agent as a service that can be
        used by other applications.

For more information on the ways to run your agent, see the *Run Your Agent*
topic in the
[Quickstart](/adk-docs/get-started/quickstart/#run-your-agent).
For more information about the ADK command line options, see the
[ADK CLI reference](/adk-docs/api-reference/cli/).

## Example configs

This section shows examples of Agent Config files to get you started building
agents. For additional and more complete examples, see the ADK
[samples repository](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+root_agent.yaml&type=code).

### Built-in tool example

The following example uses a built-in ADK tool function for using google search
to provide functionality to the agent. This agent automatically uses the search
tool to reply to user requests.

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
name: search_agent
model: gemini-2.0-flash
description: 'an agent whose job it is to perform Google search queries and answer questions about the results.'
instruction: You are an agent whose job is to perform Google search queries and answer questions about the results.
tools:
  - name: google_search
```

For more details, see the full code for this sample in the
[ADK sample repository](https://github.com/google/adk-python/blob/main/contributing/samples/tool_builtin_config/root_agent.yaml).

### Custom tool example

The following example uses a custom tool built with Python code and listed in
the `tools:` section of the config file. The agent uses this tool to check if a
list of numbers provided by the user are prime numbers.

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: prime_agent
description: Handles checking if numbers are prime.
instruction: |
  You are responsible for checking whether numbers are prime.
  When asked to check primes, you must call the check_prime tool with a list of integers.
  Never attempt to determine prime numbers manually.
  Return the prime number results to the root agent.
tools:
  - name: ma_llm.check_prime
```

For more details, see the full code for this sample in the
[ADK sample repository](https://github.com/google/adk-python/blob/main/contributing/samples/multi_agent_llm_config/prime_agent.yaml).

### Sub-agents example

The following example shows an agent defined with two sub-agents in the
`sub_agents:` section, and an example tool in the `tools:` section of the config
file. This agent determines what the user wants, and delegates to one of the
sub-agents to resolve the request. The sub-agents are defined using Agent Config
YAML files.

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: root_agent
description: Learning assistant that provides tutoring in code and math.
instruction: |
  You are a learning assistant that helps students with coding and math questions.

  You delegate coding questions to the code_tutor_agent and math questions to the math_tutor_agent.

  Follow these steps:
  1. If the user asks about programming or coding, delegate to the code_tutor_agent.
  2. If the user asks about math concepts or problems, delegate to the math_tutor_agent.
  3. Always provide clear explanations and encourage learning.
sub_agents:
  - config_path: code_tutor_agent.yaml
  - config_path: math_tutor_agent.yaml
```

For more details, see the full code for this sample in the
[ADK sample repository](https://github.com/google/adk-python/blob/main/contributing/samples/multi_agent_basic_config/root_agent.yaml).

## Deploy agent configs

You can deploy Agent Config agents with
[Cloud Run](/adk-docs/deploy/cloud-run/) and
[Agent Engine](/adk-docs/deploy/agent-engine/),
using the same procedure as code-based agents. For more information on how
to prepare and deploy Agent Config-based agents, see the
[Cloud Run](/adk-docs/deploy/cloud-run/) and
[Agent Engine](/adk-docs/deploy/agent-engine/)
deployment guides.

## Known limitations {#known-limitations}

The Agent Config feature is experimental and includes the following
limitations:

-   **Model support:** Only Gemini models are currently supported.
    Integration with third-party models is in progress.
-   **Programming language:** The Agent Config feature currently supports
    only Python code for tools and other functionality requiring programming code.
-   **ADK Tool support:** The following ADK tools are supported by the Agent
    Config feature, but *not all tools are fully supported*:
    -   `google_search`
    -   `load_artifacts`
    -   `url_context`
    -   `exit_loop`
    -   `preload_memory`
    -   `get_user_choice`
    -   `enterprise_web_search`
    -   `load_web_page`: Requires a fully-qualified path to access web
        pages.
-   **Agent Type Support:** The `LangGraphAgent` and `A2aAgent` types are
    not yet supported.
    -   `AgentTool`
    -   `LongRunningFunctionTool`
    -   `VertexAiSearchTool`
    -   `MCPToolset`
    -   `ExampleTool`

## Next steps

For ideas on how and what to build with ADK Agent Configs, see the yaml-based
agent definitions in the ADK
[adk-samples](https://github.com/search?q=repo:google/adk-python+path:/%5Econtributing%5C/samples%5C//+root_agent.yaml&type=code)
repository. For detailed information on the syntax and settings supported by
the Agent Config format, see the
[Agent Config syntax reference](/adk-docs/api-reference/agentconfig/).
