# Third Party Tools

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python. Java support is planned/ coming soon."}

ADK is designed to be **highly extensible, allowing you to seamlessly integrate tools from other AI Agent frameworks** like CrewAI and LangChain. This interoperability is crucial because it allows for faster development time and allows you to reuse existing tools.

## Using LangChain Tools

ADK provides the `LangchainTool` wrapper to integrate tools from the LangChain ecosystem into your agents.

### Example: Web Search using LangChain's Tavily tool

[Tavily](https://tavily.com/) provides a search API that returns answers derived from real-time search results, intended for use by applications like AI agents.

1. Follow [ADK installation and setup](/adk-docs/get-started/installation.md) guide.

2. **Install Dependencies:** Ensure you have the necessary LangChain packages installed. For example, to use the Tavily search tool, install its specific dependencies:

    ```bash
    pip install langchain_community tavily-python
    ```

3. Obtain a [Tavily](https://tavily.com/) API KEY and export it as an environment variable.

    ```bash
    export TAVILY_API_KEY=<REPLACE_WITH_API_KEY>
    ```

4. **Import:** Import the `LangchainTool` wrapper from ADK and the specific `LangChain` tool you wish to use (e.g, `TavilySearchResults`).

    ```py
    from google.adk.tools.langchain_tool import LangchainTool
    from langchain_community.tools import TavilySearchResults
    ```

5. **Instantiate & Wrap:** Create an instance of your LangChain tool and pass it to the `LangchainTool` constructor.

    ```py
    # Instantiate the LangChain tool
    tavily_tool_instance = TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        include_images=True,
    )

    # Wrap it with LangchainTool for ADK
    adk_tavily_tool = LangchainTool(tool=tavily_tool_instance)
    ```

6. **Add to Agent:** Include the wrapped `LangchainTool` instance in your agent's `tools` list during definition.

    ```py
    from google.adk import Agent

    # Define the ADK agent, including the wrapped tool
    my_agent = Agent(
        name="langchain_tool_agent",
        model="gemini-2.0-flash",
        description="Agent to answer questions using TavilySearch.",
        instruction="I can answer your questions by searching the internet. Just ask me anything!",
        tools=[adk_tavily_tool] # Add the wrapped tool here
    )
    ```

### Full Example: Tavily Search

Here's the full code combining the steps above to create and run an agent using the LangChain Tavily search tool.

```py
--8<-- "examples/python/snippets/tools/third-party/langchain_tavily_search.py"
```

## Using CrewAI tools

ADK provides the `CrewaiTool` wrapper to integrate tools from the CrewAI library.

### Example: Web Search using CrewAI's Serper API

[Serper API](https://serper.dev/) provides access to Google Search results programmatically. It allows applications, like AI agents, to perform real-time Google searches (including news, images, etc.) and get structured data back without needing to scrape web pages directly.

1. Follow [ADK installation and setup](/adk-docs/get-started/installation.md) guide.

2. **Install Dependencies:** Install the necessary CrewAI tools package. For example, to use the SerperDevTool:

    ```bash
    pip install crewai-tools
    ```

3. Obtain a [Serper API KEY](https://serper.dev/) and export it as an environment variable.

    ```bash
    export SERPER_API_KEY=<REPLACE_WITH_API_KEY>
    ```

4. **Import:** Import `CrewaiTool` from ADK and the desired CrewAI tool (e.g, `SerperDevTool`).

    ```py
    from google.adk.tools.crewai_tool import CrewaiTool
    from crewai_tools import SerperDevTool
    ```

5. **Instantiate & Wrap:** Create an instance of the CrewAI tool. Pass it to the `CrewaiTool` constructor. **Crucially, you must provide a name and description** to the ADK wrapper, as these are used by ADK's underlying model to understand when to use the tool.

    ```py
    # Instantiate the CrewAI tool
    serper_tool_instance = SerperDevTool(
        n_results=10,
        save_file=False,
        search_type="news",
    )

    # Wrap it with CrewaiTool for ADK, providing name and description
    adk_serper_tool = CrewaiTool(
        name="InternetNewsSearch",
        description="Searches the internet specifically for recent news articles using Serper.",
        tool=serper_tool_instance
    )
    ```

6. **Add to Agent:** Include the wrapped `CrewaiTool` instance in your agent's `tools` list.

    ```py
    from google.adk import Agent

    # Define the ADK agent
    my_agent = Agent(
        name="crewai_search_agent",
        model="gemini-2.0-flash",
        description="Agent to find recent news using the Serper search tool.",
        instruction="I can find the latest news for you. What topic are you interested in?",
        tools=[adk_serper_tool] # Add the wrapped tool here
    )
    ```

### Full Example: Serper API

Here's the full code combining the steps above to create and run an agent using the CrewAI Serper API search tool.

```py
--8<-- "examples/python/snippets/tools/third-party/crewai_serper_search.py"
```
