---
catalog_title: Code Execution
catalog_description: Execute code and debug using Gemini models
catalog_icon: /adk-docs/integrations/assets/gemini-spark.svg
catalog_tags: ["code", "google"]
---

# Gemini API Code Execution tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

The `built_in_code_execution` tool enables the agent to execute code,
specifically when using Gemini 2 and higher models. This allows the model to
perform tasks like calculations, data manipulation, or running small scripts.

!!! warning "Warning: Single tool per agent limitation"

    This tool can only be used ***by itself*** within an agent instance.
    For more information about this limitation and workarounds, see
    [Limitations for ADK tools](/adk-docs/tools/limitations/#one-tool-one-agent).

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CodeExecutionAgentApp.java:full_code"
    ```
