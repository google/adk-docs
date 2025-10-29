# Integrate with LangChain Tools

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python. Java support is planned/ coming soon."}

ADK is designed to be **highly extensible, allowing you to seamlessly integrate tools from other AI Agent frameworks** such as LangChain. This interoperability is crucial because it allows for faster development time and allows you to reuse existing tools.

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
