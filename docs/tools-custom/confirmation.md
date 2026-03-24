# Get action confirmation for ADK Tools

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.14.0</span><span class="lst-go">Go</span><span class="lst-preview">Experimental</span>
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
append a confirmation step using the built-in configuration. For example, if you have a tool called `reimburse`, you can enable a confirmation
step by setting the `require_confirmation` parameter to `True` (Python) or `RequireConfirmation` to `true` (Go).

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

=== "Go"

    ```go
    reimburseTool, _ := functiontool.New(functiontool.Config{
        Name:                "reimburse",
        Description:         "Reimburse an amount",
        // Set RequireConfirmation to true to require user confirmation
        // for the tool call.
        RequireConfirmation: true,
    }, reimburse)

    rootAgent, _ := llmagent.New(llmagent.Config{
        // ...
        Tools: []tool.Tool{reimburseTool},
    })
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

You can modify the behavior of the confirmation requirement by using a function that returns a boolean response based on the tool's input.

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

=== "Go"

    ```go
    reimburseTool, _ := functiontool.New(functiontool.Config{
        Name:        "reimburse",
        Description: "Reimburse an amount",
        // RequireConfirmationProvider allows for dynamic determination 
        // of whether user confirmation is needed.
        RequireConfirmationProvider: func(args ReimburseArgs) bool {
            return args.Amount > 1000
        },
    }, reimburse)
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
response, use the manual confirmation request implementation in your tool's logic. This approach uses the `ToolContext` object to provide a text description of the request and allows for complex response data via a payload.

### Confirmation definition

When creating a Tool with advanced confirmation, use the `tool_context.request_confirmation()` method (Python/Go) or `toolContext.requestConfirmation()` (Java) with `hint` and `payload` parameters:

-   `hint`: Descriptive message that explains what is needed from the user.
-   `payload`: The structure of the data you expect in return. This must be serializable into a JSON-formatted string.

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

=== "Go"

    ```go
    func requestTimeOff(ctx tool.Context, args RequestTimeOffArgs) (map[string]any, error) {
        confirmation := ctx.ToolConfirmation()
        if confirmation == nil {
            ctx.RequestConfirmation(
                "Please approve or reject the tool call requestTimeOff() by "+
                "responding with a FunctionResponse with an expected "+
                "ToolConfirmation payload.",
                map[string]any{"approved_days": 0},
            )
            return map[string]any{"status": "Manager approval is required."}, nil
        }

        payload := confirmation.Payload.(map[string]any)
        approvedDays := int(payload["approved_days"].(float64))
        approvedDays = min(approvedDays, args.Days)
        
        if approvedDays == 0 {
            return map[string]any{"status": "The time off request is rejected.", "approved_days": 0}, nil
        }
        
        return map[string]any{
            "status": "ok",
            "approved_days": approvedDays,
        }, nil
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

## Remote confirmation with REST API {#remote-response}

If there is no active user interface for human confirmation, you can handle it via the ADK API server's `/run` or `/run_sse` endpoint by sending a `FunctionResponse` event with the tool confirmation data.

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

## Known limitations {#known-limitations}

The tool confirmation feature has the following limitations:

-   [DatabaseSessionService](/adk-docs/api-reference/python/google-adk.html#google.adk.sessions.DatabaseSessionService)
    is not supported by this feature.
-   [VertexAiSessionService](/adk-docs/api-reference/python/google-adk.html#google.adk.sessions.VertexAiSessionService)
    is not supported by this feature.

## Next steps

For more information on building ADK tools for agent workflows, see [Function
tools](/adk-docs/tools-custom/function-tools/).
