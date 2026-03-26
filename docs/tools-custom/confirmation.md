# Get action confirmation for ADK Tools

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.14.0</span><span class="lst-preview">Experimental</span>
</div>

Some agent workflows require confirmation for decision making, verification,
security, or general oversight. In these cases, you want to get a response from
a human or supervising system before proceeding with a workflow. The *Tool
Confirmation* feature in the Agent Development Kit (ADK) allows an ADK Tool to
pause its execution and interact with a user or other system for confirmation or
to gather structured data before proceeding. You can use Tool Confirmation with
an ADK Tool in the following ways:

-   **[Boolean Confirmation](#boolean-confirmation):** You can
    configure a FunctionTool with a `require_confirmation` parameter. This
    option pauses the tool for a yes or no confirmation response.
-   **[Advanced Confirmation](#advanced-confirmation):** For scenarios requiring
    structured data responses, you can configure a `FunctionTool` with a text
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

![Screenshot of default user interface for tool confirmation](/adk-docs/assets/confirmation-ui.png)

**Figure 1.** Example confirmation response request dialog box using an
advanced, tool response implementation.

The following sections describe how to use this feature for the confirmation
scenarios. For a complete code sample, see the
[human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py)
example. There are additional ways to incorporate human input into your agent
workflow, for more details, see the
[Human-in-the-loop](/adk-docs/agents/multi-agents/#human-in-the-loop-pattern)
agent pattern.

## Boolean confirmation {#boolean-confirmation}

When your tool only requires a simple `yes` or `no` from the user, you can
append a confirmation step using the `FunctionTool` class as a wrapper. For
example, if you have a tool called `reimburse`, you can enable a confirmation
step by wrapping it with the `FunctionTool` class and setting the
`require_confirmation` parameter to `True`, as shown in the following example:

=== "Python"

    ```python
    root_agent = Agent(
        # ...
        tools = [
            # Set require_confirmation to True to require user confirmation
            # for the tool call.
            FunctionTool(reimburse, require_confirmation=True),
        ],
        # ...
    )

    # This implementation method requires minimal code, but is limited to simple
    # approvals from the user or confirming system. For a complete example of this
    # approach, see the following code sample for a more detailed example:
    # https://github.com/google/adk-python/blob/main/contributing/samples/human_tool_confirmation/agent.py
    ```

=== "Java"

    ```java
    LlmAgent rootAgent = LlmAgent.builder()
        // ...
        .tools(
            // Set requireConfirmation to true to require user confirmation
            // for the tool call.
            FunctionTool.create(myClassInstance, "reimburse", true)
        )
        // ...
        .build();
    ```

### Require confirmation function

You can modify the behavior `require_confirmation` response by replacing its
input value with a function that returns a boolean response. The following
example shows a function for determining if a confirmation is required:

=== "Python"

    ```python
    async def confirmation_threshold(
        amount: int, tool_context: ToolContext
    ) -> bool:
      """Returns true if the amount is greater than 1000."""
      return amount > 1000

    root_agent = Agent(
        # ...
        tools = [
            # Pass the threshold function to dynamically require confirmation
            FunctionTool(reimburse, require_confirmation=confirmation_threshold),
        ],
        # ...
    )
    ```

=== "Java"

    ```java
    // In ADK Java, dynamic threshold confirmation logic is evaluated directly 
    // inside the tool logic using the ToolContext rather than via a lambda parameter.
    public Map<String, Object> reimburse(
        @Schema(name="amount") int amount, ToolContext toolContext) {
      
      // 1. Dynamic threshold check
      if (amount > 1000) { 
        Optional<ToolConfirmation> toolConfirmation = toolContext.toolConfirmation();
        if (toolConfirmation.isEmpty()) {
           toolContext.requestConfirmation("Amount > 1000 requires approval.");
           return Map.of("status", "Pending manager approval.");
        } else if (!toolConfirmation.get().confirmed()) {
           return Map.of("status", "Reimbursement rejected.");
        }
      }
      
      // 2. Proceed with actual tool logic
      return Map.of("status", "ok", "reimbursedAmount", amount);
    }

    LlmAgent rootAgent = LlmAgent.builder()
        // ...
        .tools(
            // No requireConfirmation flag is set because the custom threshold
            // logic is already handled inside the method!
            FunctionTool.create(this, "reimburse")
        )
        // ...
        .build();    
    ```

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

When creating a Tool with an advanced confirmation, create a function that
includes a ToolContext object. Then define the confirmation using a
tool_confirmation object, the `tool_context.request_confirmation()` method with
`hint` and `payload` parameters. These properties are used as follows:

-   `hint`: Descriptive message that explains what is needed from the user.
-   `payload`: The structure of the data you expect in return. This data
    type is Any and must be serializable into a JSON-formatted string, such as
    a dictionary or pydantic model.

The following code shows an example implementation for a tool that processes
time off requests for an employee:

=== "Python"

    ```python
    def request_time_off(days: int, tool_context: ToolContext):
        """Request day off for the employee."""
        # ...
        tool_confirmation = tool_context.tool_confirmation
        if not tool_confirmation:
            tool_context.request_confirmation(
                hint=(
                    'Please approve or reject the tool call request_time_off() by'
                    ' responding with a FunctionResponse with an expected'
                    ' ToolConfirmation payload.'
                ),
                payload={
                    'approved_days': 0,
                },
            )
            # Return intermediate status indicating that the tool is waiting for
            # a confirmation response:
            return {'status': 'Manager approval is required.'}

        approved_days = tool_confirmation.payload['approved_days']
        approved_days = min(approved_days, days)
        if approved_days == 0:
            return {'status': 'The time off request is rejected.', 'approved_days': 0}
        return {
            'status': 'ok',
            'approved_days': approved_days,
        }
    ```

=== "Java"

    ```java
    public Map<String, Object> requestTimeOff(
        @Schema(name="days") int days, 
        ToolContext toolContext) {
        // Request day off for the employee.
        // ...
        Optional<ToolConfirmation> toolConfirmation = toolContext.toolConfirmation();
        if (toolConfirmation.isEmpty()) {
            toolContext.requestConfirmation(
                "Please approve or reject the tool call requestTimeOff() by " +
                "responding with a FunctionResponse with an expected " +
                "ToolConfirmation payload.",
                Map.of("approved_days", 0)
            );
            // Return intermediate status indicating that the tool is waiting for
            // a confirmation response:
            return Map.of("status", "Manager approval is required.");
        }

        Map<String, Object> payload = (Map<String, Object>) toolConfirmation.get().payload();
        int approvedDays = (int) payload.get("approved_days");
        approvedDays = Math.min(approvedDays, days);
        
        if (approvedDays == 0) {
            return Map.of("status", "The time off request is rejected.", "approved_days", 0);
        }
        
        return Map.of(
            "status", "ok",
            "approved_days", approvedDays
        );
    }
    ```

For a complete example of this approach, see the
[human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py)
code sample. Keep in mind that the agent workflow tool execution pauses while a
confirmation is obtained. After confirmation is received, you can access the
confirmation response in the `tool_confirmation.payload` object and then proceed
with the execution of the workflow.

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
                        "confirmed": true
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
    from the `RequestConfirmation` `FunctionCall` event.
-   The `name` should be `adk_request_confirmation`.
-   The `response` object contains the confirmation status and any
    additional payload data required by the tool.

!!! note "Note: Confirmation with Resume feature"

    If your ADK agent workflow is configured with the 
    [Resume](/adk-docs/runtime/resume/) feature, you also must include
    the Invocation ID (`invocation_id`) parameter with the confirmation
    response. The Invocation ID you provide must be the same invocation
    that generated the confirmation request, otherwise the system
    starts a new invocation with the confirmation response. If your
    agent uses the Resume feature, consider including the Invocation ID
    as a parameter with your confirmation request, so it can be
    included with the response. For more details on using the Resume
    feature, see
    [Resume stopped agents](/adk-docs/runtime/resume/).

## Known limitations {#known-limitations}

The tool confirmation feature has the following limitations:

-   [DatabaseSessionService](/adk-docs/api-reference/python/google-adk.html#google.adk.sessions.DatabaseSessionService)
    is not supported by this feature.
-   [VertexAiSessionService](/adk-docs/api-reference/python/google-adk.html#google.adk.sessions.VertexAiSessionService)
    is not supported by this feature.

## Next steps

For more information on building ADK tools for agent workflows, see [Function
tools](/adk-docs/tools-custom/function-tools/).
