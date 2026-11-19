---
catalog_title: Code Execution
catalog_description: Execute code and debug using Gemini models
catalog_icon: /integrations/assets/gemini-spark.svg
catalog_tags: ["code", "google"]
---

# Gemini API Code Execution tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

The Code execution functionality in the Gemini API allows the model to perform
tasks like calculations, data manipulation, or running small scripts. This
function is available using Gemini 2 and higher models. 

!!! warning "Warning: Single tool per agent limitation"

    This tool can only be used ***by itself*** within an agent instance.
    For more information about this limitation and workarounds, see
    [Limitations for ADK tools](/tools/limitations/#one-tool-one-agent).

## Get started

The following code examples show the basic implementation of this functionality
in an ADK agent:

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CodeExecutionAgentApp.java:full_code"
    ```
