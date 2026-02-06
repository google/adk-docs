---
catalog_title: Vertex AI Search
catalog_description: Search across your private, configured data stores in Vertex AI Search
catalog_icon: /adk-docs/assets/tools-vertex-ai.png
---

# Vertex AI Search tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

The `vertex_ai_search_tool` uses Google Cloud Vertex AI Search, enabling the
agent to search across your private, configured data stores (e.g., internal
documents, company policies, knowledge bases). This built-in tool requires you
to provide the specific data store ID during configuration. For further details
of the tool, see
[Understanding Vertex AI Search grounding](/adk-docs/grounding/vertex_ai_search_grounding/).

!!! warning "Warning: Single tool per agent limitation"

    This tool can only be used ***by itself*** within an agent instance.
    For more information about this limitation and workarounds, see
    [Limitations for ADK tools](/adk-docs/tools/limitations/#one-tool-one-agent).

```py
--8<-- "examples/python/snippets/tools/built-in-tools/vertexai_search.py"
```

## Dynamic Configuration (e.g., Per-User Filtering)

You can dynamically configure the Vertex AI Search tool at runtime by subclassing `VertexAiSearchTool` and overriding the `_build_vertex_ai_search_config(self, context)` method. This is useful for applying context-aware filters, such as filtering results based on the current user's ID.

The `context` object provides access to the agent's state, allowing you to create customized search configurations for each request.

### Example: Per-User Filtering

Here is an example of how to implement a dynamic filter based on a `user_id` stored in the agent's state:

```python
from google.genai import types
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import VertexAiSearchTool

class DynamicFilterSearchTool(VertexAiSearchTool):
  def _build_vertex_ai_search_config(
      self, ctx: ReadonlyContext
  ) -> types.VertexAISearch:
    user_id = ctx.state.get('user_id')
    return types.VertexAISearch(
        datastore=self.data_store_id,
        filter=f"user_id = '{user_id}'"
    )
```

In this example:

1.  `DynamicFilterSearchTool` inherits from `VertexAiSearchTool`.
2.  The `_build_vertex_ai_search_config` method is overridden to access the agent's context.
3.  The `user_id` is retrieved from `ctx.state`.
4.  A `VertexAISearch` object is returned with a dynamic filter that restricts the search to documents where the `user_id` field matches the user's ID.
