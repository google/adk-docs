---
catalog_title: Knowledge Engine
catalog_description: Perform private data retrieval using Knowledge Engine
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["data","google"]
---

# Knowledge Engine tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

The `vertex_ai_rag_retrieval` tool allows the agent to perform private data
retrieval using Knowledge Engine.

When you use grounding with Knowledge Engine, you need to prepare a RAG corpus
beforehand. Please refer to the [RAG ADK agent
sample](https://github.com/google/adk-samples/blob/main/python/agents/RAG/rag/shared_libraries/prepare_corpus_and_data.py)
or [Knowledge Engine
page](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart)
for setting it up.

!!! warning "Warning: Single tool per agent limitation"

    This tool can only be used ***by itself*** within an agent instance.
    For more information about this limitation and workarounds, see
    [Limitations for ADK tools](/tools/limitations/).

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/rag_engine.py"
    ```
