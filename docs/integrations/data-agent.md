---
catalog_title: Data Agents
catalog_description: Analyze data with AI-powered agents
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["data", "google"]
---

# Google Cloud Data Agents tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.23.0</span>
</div>

These are a set of tools aimed to provide integration with Data Agents powered by [Conversational Analytics API](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/overview).

Data Agents are AI-powered agents that help you analyze your data using natural language. When configuring a Data Agent, you can choose from supported data sources, including **BigQuery**, **Looker**, and **Looker Studio**.

**Prerequisites**

Before using these tools, you must build and configure your Data Agents in Google Cloud:

* [Build a data agent using HTTP and Python](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-http)
* [Build a data agent using the Python SDK](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-sdk)
* [Create a data agent in BigQuery Studio](https://docs.cloud.google.com/bigquery/docs/create-data-agents#create_a_data_agent)

The `DataAgentToolset` includes the following tools:

* **`list_accessible_data_agents`**: Lists Data Agents you have permission to access in the configured GCP project.
* **`get_data_agent_info`**: Retrieves details about a specific Data Agent given its full resource name.
* **`ask_data_agent`**: Chats with a specific Data Agent using natural language.

They are packaged in the toolset `DataAgentToolset`.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/data_agent.py"
```
