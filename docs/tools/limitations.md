# Limitations for ADK tools

Some ADK tools have limitations that can impact how you implement them within an
agent workflow. This page lists these tool limitations and workarounds, if available.

## One tool per agent limitation {#one-tool-one-agent}

!!! note "ONLY for Search in ADK Python v1.15.0 and lower"

    This limitation only applies to the use of Google Search and Agent Search
    tools in ADK Python v1.15.0 and lower. ADK Python release v1.16.0 and higher
    provides a built-in workaround to remove this limitation.

In general, you can use more than one tool in an agent, but use of specific
tools within an agent excludes the use of any other tools in that agent. The
following ADK Tools can only be used by themselves, without any other tools, in
a single agent object:

* [Code Execution](/integrations/code-execution/) with Gemini API (Note: in
  TypeScript, this requires Gemini 2.0+ and does not have this limitation)
* [Google Search](/integrations/google-search/) with Gemini API (Note:
  limitation only applies to Gemini 1.x models in TypeScript)
* [Agent Search](/integrations/agent-search/) (Note: currently unavailable in
  TypeScript)

For example, the following approach that uses one of these tools along with
other tools, within a single agent, is ***not supported***:

=== "Python"

    ```py
    --8<-- "examples/inline/python/tools/limitations/001-one-tool-per-agent-limitation-one-tool-o.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/tools/limitations/002-one-tool-per-agent-limitation-one-tool-o.ts"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/tools/limitations/003-one-tool-per-agent-limitation-one-tool-o.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/inline/kotlin/tools/limitations/004-one-tool-per-agent-limitation-one-tool-o.kt"
    ```

### Workaround #1: AgentTool.create() method

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript (v0.6.1+)</span><span class="lst-java">Java</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

The following code sample demonstrates how to use multiple built-in tools or how
to use built-in tools with other tools by using multiple agents:

=== "Python"

    ```py
    --8<-- "examples/inline/python/tools/limitations/005-workaround-1-agenttool-create-method.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/tools/limitations/006-workaround-1-agenttool-create-method.ts"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/tools/limitations/007-workaround-1-agenttool-create-method.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/tools/LimitationsWorkaround.kt:workaround_1"
    ```

### Workaround #2: bypass_multi_tools_limit

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-java">Java</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

ADK Python has a built-in workaround which bypasses this limitation for
`GoogleSearchTool` and `VertexAiSearchTool` (use `bypass_multi_tools_limit=True` to enable it),
as shown in the
[built_in_multi_tools](https://github.com/google/adk-python/tree/main/contributing/samples/tools/built_in_multi_tools).
sample agent.

!!! warning

    Built-in tools cannot be used within a sub-agent, with the exception of
    `GoogleSearchTool` and `VertexAiSearchTool` in ADK Python because of the
    workaround mentioned above.

For example, the following approach that uses built-in tools within sub-agents
is **not supported**:

=== "Python"

    ```py
    --8<-- "examples/inline/python/tools/limitations/008-workaround-2-bypassmultitoolslimit.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/tools/limitations/009-workaround-2-bypassmultitoolslimit.ts"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/tools/limitations/010-workaround-2-bypassmultitoolslimit.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/inline/kotlin/tools/limitations/011-workaround-2-bypassmultitoolslimit.kt"
    ```
