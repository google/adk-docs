# Get action confirmation for ADK Tools

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.14.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.3.0</span><span class="lst-kotlin">Kotlin v0.1.0</span><span class="lst-preview">Experimental</span>
</div>

Some agent workflows require confirmation for decision making, verification,
security, or general oversight. In these cases, you want to get a response from
a human or supervising system before proceeding with a workflow. The *Tool
Confirmation* feature in the Agent Development Kit (ADK) allows an ADK Tool to
pause its execution and interact with a user or other system for confirmation or
to gather structured data before proceeding. You can use Tool Confirmation with
an ADK Tool in the following ways:

-   **[Boolean Confirmation](#boolean-confirmation):** You can
    configure a tool with a confirmation flag or provider. This
    option pauses the tool for a yes or no confirmation response.
-   **[Advanced Confirmation](#advanced-confirmation):** For scenarios requiring
    structured data responses, you can configure a tool with a text
    prompt to explain the confirmation and an expected response.

!!! example "Experimental"
    The Tool Confirmation feature is experimental and has some
    [known limitations](#known-limitations).
    We welcome your
    [feedback](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=tool%20confirmation)!

You can configure how a request is communicated to a user, and the system can
also use [remote responses](#remote-response) sent via the ADK
server's REST API. When using the confirmation feature with the ADK web user
interface, the agent workflow displays a dialog box to the user to request
input, as shown in Figure 1:

![Screenshot of default user interface for tool confirmation](/assets/confirmation-ui.png)

**Figure 1.** Example confirmation response request dialog box using an
advanced, tool response implementation.

The following sections describe how to use this feature for the confirmation
scenarios. For a complete code sample, see the
[human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py)
example. There are additional ways to incorporate human input into your agent
workflow, for more details, see the
[Human-in-the-loop](/workflows/patterns/#human-in-the-loop)
agent pattern.

## Boolean confirmation {#boolean-confirmation}

When your tool only requires a simple `yes` or `no` from the user, you can
append a confirmation step. In Python, Go, and Java, you can enable this by
wrapping the tool with the `FunctionTool` class and setting the
`require_confirmation` parameter (or equivalent) to `True`. In Kotlin, you set
`requireConfirmation = true` on the tool function's `@Tool` annotation. In
TypeScript, you implement this logic manually within the `execute` function
using the `ToolContext`.

The following examples show how to enable boolean confirmation:

=== "Python"

    ```python
    --8<-- "examples/inline/python/tools-custom/confirmation/001-boolean-confirmation-boolean-confirmatio.py"
    ```

=== "TypeScript"

    !!! note
        ADK for TypeScript currently requires manual implementation of
        confirmation logic within the tool's `execute` function.

    ```typescript
    --8<-- "examples/typescript/snippets/tools/confirmation/boolean_confirmation.ts:boolean_confirmation"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/tools-custom/confirmation/002-boolean-confirmation-boolean-confirmatio.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/tools-custom/confirmation/003-boolean-confirmation-boolean-confirmatio.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/tools/confirmation/ToolConfirmationExample.kt:boolean_confirmation"
    ```

### Require confirmation function

You can modify the behavior of the confirmation requirement by using a function that returns a boolean response based on the tool's input. In TypeScript, this is handled by adding conditional logic to your `execute` function. In Kotlin, the `@Tool` annotation's flag is a compile-time constant, so the conditional logic goes inside the tool function.

=== "Python"

    ```python
    --8<-- "examples/inline/python/tools-custom/confirmation/004-require-confirmation-function.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/tools/confirmation/boolean_confirmation.ts:dynamic_confirmation"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/tools-custom/confirmation/005-require-confirmation-function.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/tools-custom/confirmation/006-require-confirmation-function.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/tools/confirmation/dynamic/ReimbursementTools.kt:dynamic_confirmation"
    ```

    !!! note
        The `@Tool` annotation's `requireConfirmation` flag is a compile-time
        constant, so a threshold is evaluated inside the tool using the
        `ToolContext`, as in ADK Java.

## Advanced confirmation {#advanced-confirmation}

When a tool confirmation requires more details for the user or a more complex
response, use a tool_confirmation implementation. This approach extends the
`ToolContext` object to add a text description of the request for the user and
allows for more complex response data. When implementing tool confirmation this
way, you can pause a tool's execution, request specific information, and then
resume the tool with the provided data.

This confirmation flow has a request stage where the system assembles and sends
an input request human response, and a response stage where the system receives
and processes the returned data.

### Confirmation definition

When creating a Tool with advanced confirmation, use the `Tool Context Request Confirmation` method with `hint` and `payload` parameters:

-   `hint`: Descriptive message that explains what is needed from the user.
-   `payload`: The structure of the data you expect in return. This must be serializable into a JSON-formatted string.

For a complete example of this approach, see the
[human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py)
code sample. Keep in mind that the agent workflow tool execution pauses while a
confirmation is obtained. After confirmation is received, you can access the
confirmation response in the `tool_confirmation.payload` object and then proceed
with the execution of the workflow.

The following code shows an example implementation for a tool that processes
time off requests for an employee:

=== "Python"

    ```python
    --8<-- "examples/inline/python/tools-custom/confirmation/007-confirmation-definition.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/tools/confirmation/confirmation_example.ts:advanced_confirmation"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/tools-custom/confirmation/008-confirmation-definition.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/tools-custom/confirmation/009-confirmation-definition.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/tools/confirmation/ToolConfirmationExample.kt:advanced_confirmation"
    ```

## Remote confirmation with REST API {#remote-response}

If there is no active user interface for a human confirmation of an agent
workflow, you can handle the confirmation through a command-line interface or by
routing it through another channel like email or a chat application. To confirm
the tool call, the user or calling application needs to send a
`FunctionResponse` event with the tool confirmation data.

You can send the request to the ADK API server's `/run` or `/run_sse` endpoint,
or directly to the ADK runner. The following example uses a  `curl` command to
send the confirmation to the  `/run_sse` endpoint:


```bash
 curl -X POST http://localhost:8000/run_sse \
 -H "Content-Type: application/json" \
 -d '{
    "app_name": "human_tool_confirmation",
    "user_id": "user",
    "session_id": "7828f575-2402-489f-8079-74ea95b6a300",
    "new_message": {
        "parts": [
            {
                "function_response": {
                    "id": "adk-13b84a8c-c95c-4d66-b006-d72b30447e35",
                    "name": "adk_request_confirmation",
                    "response": {
                        "confirmed": true,
                        "payload": {
                            "approved_days": 5
                        }
                    }
                }
            }
        ],
        "role": "user"
    }
}'
```

A REST-based response for a confirmation must meet the following
requirements:

-   The `id` in the `function_response` should match the `function_call_id`
    from the `adk_request_confirmation` `FunctionCall` event.
-   The `name` should be `adk_request_confirmation`.
-   The `response` object contains the `confirmed` status and any
    additional `payload` data.

    !!! note "Note: Confirmation with Resume feature"

    If your ADK agent workflow is configured with the
    [Resume](/runtime/resume/) feature, you also must include
    the Invocation ID (`invocation_id`) parameter with the confirmation
    response. The Invocation ID you provide must be the same invocation
    that generated the confirmation request, otherwise the system
    starts a new invocation with the confirmation response. If your
    agent uses the Resume feature, consider including the Invocation ID
    as a parameter with your confirmation request, so it can be
    included with the response. For more details on using the Resume
    feature, see
    [Resume stopped agents](/runtime/resume/).

## Known limitations {#known-limitations}

The tool confirmation feature has the following limitations:

-   [DatabaseSessionService](/api-reference/python/google-adk.html#google.adk.sessions.DatabaseSessionService)
    is not supported by this feature.
-   [VertexAiSessionService](/api-reference/python/google-adk.html#google.adk.sessions.VertexAiSessionService)
    is not supported by this feature.

## Next steps

For more information on building ADK tools for agent workflows, see [Function
tools](/tools-custom/function-tools/).
