# Data Agent tools for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.1.0</span>
</div>

These are a set of tools aimed to provide integration with Data Agents powered by [Conversational Analytics API](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/overview), namely:

* **`list_accessible_data_agents`**: Lists Data Agents you have permission to access in the configured GCP project.
* **`get_data_agent_info`**: Retrieves details about a specific Data Agent given its full resource name.
* **`ask_data_agent`**: Chats with a specific Data Agent using natural language.

They are packaged in the toolset `DataAgentToolset`.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/data_agent.py"
```
