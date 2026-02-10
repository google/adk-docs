---
catalog_title: Google Search
catalog_description: Perform web searches using Google Search with Gemini
catalog_icon: /adk-docs/integrations/assets/google-search.png
catalog_tags: ["search","google"]
---

# Gemini API Google Search tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

The `google_search` tool allows the agent to perform web searches using Google Search. The `google_search` tool is only compatible with Gemini 2 models. For further details of the tool, see [Understanding Google Search grounding](/adk-docs/grounding/google_search_grounding/).

!!! warning "Additional requirements when using the `google_search` tool"
    When you use grounding with Google Search, and you receive Search suggestions in your response, you must display the Search suggestions in production and in your applications.
    For more information on grounding with Google Search, see Grounding with Google Search documentation for [Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) or [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions). The UI code (HTML) is returned in the Gemini response as `renderedContent`, and you will need to show the HTML in your app, in accordance with the policy.

!!! warning "Warning: Single tool per agent limitation"

    This tool can only be used ***by itself*** within an agent instance.
    For more information about this limitation and workarounds, see
    [Limitations for ADK tools](/adk-docs/tools/limitations/#one-tool-one-agent).

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/google_search.py"
    ```

=== "TypeScript"

    ```typescript
    import {GOOGLE_SEARCH, LlmAgent} from '@google/adk';

    export const rootAgent = new LlmAgent({
      model: 'gemini-2.5-flash',
      name: 'root_agent',
      description:
          'an agent whose job it is to perform Google search queries and answer questions about the results.',
      instruction:
          'You are an agent whose job is to perform Google search queries and answer questions about the results.',
      tools: [GOOGLE_SEARCH],
    });
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools/built-in-tools/google_search.go"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/GoogleSearchAgentApp.java:full_code"
    ```
