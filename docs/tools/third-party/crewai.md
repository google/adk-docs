# Integrate with CrewAI Tools

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python. Java support is planned/ coming soon."}

ADK is designed to be **highly extensible, allowing you to seamlessly integrate tools from other AI Agent frameworks** such as CrewAI. This interoperability is crucial because it allows for faster development time and allows you to reuse existing tools.

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
