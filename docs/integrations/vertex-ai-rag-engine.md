---
catalog_title: Vertex AI RAG Engine
catalog_description: Perform private data retrieval using Vertex AI RAG Engine
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["data","google"]
---

# Vertex AI RAG Engine tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

The `vertex_ai_rag_retrieval` tool allows the agent to perform private data retrieval using Vertex
AI RAG Engine.

When you use grounding with Vertex AI RAG Engine, you need to prepare a RAG corpus beforehand.
Please refer to the [RAG ADK agent sample](https://github.com/google/adk-samples/blob/main/python/agents/RAG/rag/shared_libraries/prepare_corpus_and_data.py) or [Vertex AI RAG Engine page](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart) for setting it up.

!!! warning "Warning: Single tool per agent limitation"

    This tool can only be used ***by itself*** within an agent instance.
    For more information about this limitation and workarounds, see
    [Limitations for ADK tools](/adk-docs/tools/limitations/).

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/vertexai_rag_engine.py"
    ```
