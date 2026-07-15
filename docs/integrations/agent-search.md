---
catalog_title: Agent Search
catalog_description: Search across your private, configured data stores in Agent Search
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["search","google"]
---

# Agent Search tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

The `vertex_ai_search_tool` uses Google Cloud Agent Search, enabling the
agent to search across your private, configured data stores (e.g., internal
documents, company policies, knowledge bases). This built-in tool requires you
to provide the specific data store ID during configuration. For further details
of the tool, see
[Understanding Grounding with Search](/grounding/grounding_with_search/).

!!! warning "Warning: Single tool per agent limitation"

    This tool can only be used ***by itself*** within an agent instance.
    For more information about this limitation and workarounds, see
    [Limitations for ADK tools](/tools/limitations/#one-tool-one-agent).

```py
--8<-- "examples/python/snippets/tools/built-in-tools/agent_search.py"
```

## Dynamic configuration

You can create a subclass of `VertexAiSearchTool` and override the 
`_build_vertex_ai_search_config` method to dynamically configure the search 
settings based on the conversation context. It's useful for implementing 
features such as per-user data filtering.

The `_build_vertex_ai_search_config` method receives the conversation 
`readonly_context` as an argument. Use this context to access state 
information and modify the search configuration at runtime.

```python
from google.genai import types
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import VertexAiSearchTool

class MyVertexAISearchTool(VertexAiSearchTool):
    def _build_vertex_ai_search_config(
        self, context: ReadonlyContext
    ) -> types.VertexAISearch:
        """Builds the VertexAISearch configuration, adding a user-specific filter."""
        config = super()._build_vertex_ai_search_config(context)
        if "user_id" in context.state:
            user_id = context.state["user_id"]
            config.filter = f'user_id: ANY("{user_id}")'
        return config
