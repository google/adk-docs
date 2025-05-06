# Built-in tools

These built-in tools provide ready-to-use functionality such as Google Search or
code executors that provide agents with common capabilities. For instance, an
agent that needs to retrieve information from the web can directly use the
**google\_search** tool without any additional setup.

## How to Use

1. **Import:** Import the desired tool from the `agents.tools` module.
2. **Configure:** Initialize the tool, providing required parameters if any.
3. **Register:** Add the initialized tool to the **tools** list of your Agent.

Once added to an agent, the agent can decide to use the tool based on the **user
prompt** and its **instructions**. The framework handles the execution of the
tool when the agent calls it. Important: check the ***Limitations*** section of this page.

## Available Built-in tools

### Google Search

The `google_search` tool allows the agent to perform web searches using Google
Search. The `google_search` tool is only compatible with Gemini 2 models.

!!! warning "Additional requirements when using the `google_search` tool"
    When you use grounding with Google Search, and you receive Search suggestions in your response, you must display the Search suggestions in production and in your applications.
    For more information on grounding with Google Search, see Grounding with Google Search documentation for [Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) or [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions). The UI code (HTML) is returned in the Gemini response as `renderedContent`, and you will need to show the HTML in your app, in accordance with the policy.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/google_search.py"
```

### Code Execution

The `built_in_code_execution` tool enables the agent to execute code,
specifically when using Gemini 2 models. This allows the model to perform tasks
like calculations, data manipulation, or running small scripts.

````py
--8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
````

### Vertex AI Search

The `vertex_ai_search_tool` uses Google Cloud's Vertex AI Search, enabling the
agent to search across your private, configured data stores (e.g., internal
documents, company policies, knowledge bases). This built-in tool requires you
to provide the specific data store ID during configuration.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/vertexai_search.py"
```

## Use Built-in tools with other tools

The following code sample demonstrates how to use multiple built-in tools or how
to use built-in tools with other tools by using multiple agents:

```py
from google.adk.tools import agent_tool
from google.adk.agents import Agent
from google.adk.tools import google_search, built_in_code_execution

search_agent = Agent(
    model='gemini-2.0-flash',
    name='SearchAgent',
    instruction="""
    You're a specialist in Google Search
    """,
    tools=[google_search],
)
coding_agent = Agent(
    model='gemini-2.0-flash',
    name='CodeAgent',
    instruction="""
    You're a specialist in Code Execution
    """,
    tools=[built_in_code_execution],
)
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Root Agent",
    tools=[agent_tool.AgentTool(agent=search_agent), agent_tool.AgentTool(agent=coding_agent)],
)
```

### Limitations

!!! warning

    Currently, for each root agent or single agent, only one built-in tool is
    supported. No other tools of any type can be used in the same agent.

 For example, the following approach that uses ***a built-in tool along with
 other tools*** within a single agent is **not** currently supported:

```py
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Root Agent",
    tools=[built_in_code_execution, custom_function], # <-- not supported
)
```

!!! warning

    Built-in tools cannot be used within a sub-agent.

For example, the following approach that uses built-in tools within sub-agents
is **not** currently supported:

```py
search_agent = Agent(
    model='gemini-2.0-flash',
    name='SearchAgent',
    instruction="""
    You're a specialist in Google Search
    """,
    tools=[google_search],
)
coding_agent = Agent(
    model='gemini-2.0-flash',
    name='CodeAgent',
    instruction="""
    You're a specialist in Code Execution
    """,
    tools=[built_in_code_execution],
)
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Root Agent",
    sub_agents=[
        search_agent,
        coding_agent
    ],
)
```
