# Built-in tools

These are ready-to-use functionalities, like Google Search, Code Executors, that provide agents with common capabilities immediately. For instance, an agent needing to retrieve information from the web can directly use the **built\_in\_google\_search** tool without any additional setup.

## How to Use

1. **Import:** Import the desired tool from the `agents.tools` module.  
2. **Configure:** Initialize the tool, providing required parameters if any.  
3. **Register:** Add the initialized tool to the **tools** list of your Agent.  

Once added to an agent, the agent can decide to use the tool based on the **user prompt** and its **instructions**. The framework handles the execution of the tool when the agent calls it.

## Available Built-in tools

### Google Search

`google_search`: Allows the agent to perform web searches using Google Search. You simply add this tool to the agent's tools list. It is compatible with Gemini 2 models.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/google_search.py"
```

### Code Execution

`built_in_code_execution`: Enables the agent to execute code, specifically when using Gemini 2 models. This allows the model to perform tasks like calculations, data manipulation, or running small scripts. This capability is built-in and automatically activated for compatible models, requiring no explicit configuration.

````py
--8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
````

### Retrieval tools

This is a category of tools designed to fetch information from various sources. Examples include:

#### Vertex AI Search

`built_in_vertexai_search`: Leverages Google Cloud's Vertex AI Search, enabling the agent to search across your private, configured data stores (e.g., internal documents, company policies, knowledge bases). This built-in tool requires you to provide the specific data store ID during configuration.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/vertexai_search.py"
```

## Use Built-in tools with other tools

Here is how to use multiple built-in tools or use built-in tools with other tools:
```py
from google.adk.tools import agent_tool

from google.adk.agents import Agent
from google.adk.tools import google_search, built_in_code_execution

search_agent = Agent(
    model='gemini-2.0-flash',
    name='SearchAgent',
    instruction="""
    You're a spealist in Google Search
    """,
    tools=[google_search]
)
coding_agent = Agent(
    model='gemini-2.0-flash',
    name='CodeAgent',
    instruction="""
    You're a specialist in Code Execution
    """,
    tools=[built_in_code_execution]
)
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Root Agent",
    tools=[agent_tool.AgentTool(agent=search_agent), agent_tool.AgentTool(agent=coding_agent)]
)
```

### Limitations

There are some known limitations.

Right now, for each root agent or single agent, only one built-in tool is supported. For example, this is NOT supported:
```py
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Root Agent",
    tools=[built_in_code_execution, custom_function]
)
```

Built-in tool can not be used in subagent. For example, this is NOT supported:
```py
search_agent = Agent(
    model='gemini-2.0-flash',
    name='SearchAgent',
    instruction="""
    You're a spealist in Google Search
    """,
    tools=[google_search]
)
coding_agent = Agent(
    model='gemini-2.0-flash',
    name='CodeAgent',
    instruction="""
    You're a specialist in Code Execution
    """,
    tools=[built_in_code_execution]
)
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Root Agent",
    sub_agents=[ # Assign sub_agents here
        Agent_Search,
        Agent_Code
    ]
)
```
