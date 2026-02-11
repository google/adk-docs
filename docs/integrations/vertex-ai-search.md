---
catalog_title: Vertex AI Search
catalog_description: Search across your private, configured data stores in Vertex AI Search
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["search","google"]
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
