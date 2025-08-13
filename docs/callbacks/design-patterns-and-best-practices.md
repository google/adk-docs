# Design Patterns and Best Practices for Callbacks

Callbacks offer powerful hooks into the agent lifecycle. Here are common design patterns illustrating how to leverage them effectively in ADK, followed by best practices for implementation.

## Design Patterns

These patterns demonstrate typical ways to enhance or control agent behavior using callbacks:

### 1. Guardrails & Policy Enforcement { #guardrails-policy-enforcement }

**Pattern Overview:**
Intercept requests before they reach the LLM or tools to enforce rules.

**Implementation:**
- Use `before_model_callback` to inspect the `LlmRequest` prompt
- Use `before_tool_callback` to inspect tool arguments
- If a policy violation is detected (e.g., forbidden topics, profanity):
  - Return a predefined response (`LlmResponse` or `dict`/`Map`) to block the operation
  - Optionally update `context.state` to log the violation

**Example Use Case:**
A `before_model_callback` checks `llm_request.contents` for sensitive keywords and returns a standard "Cannot process this request" `LlmResponse` if found, preventing the LLM call.

### 2. Dynamic State Management { #dynamic-state-management }

**Pattern Overview:**
Read from and write to session state within callbacks to make agent behavior context-aware and pass data between steps.

**Implementation:**
- Access `callback_context.state` or `tool_context.state`
- Modifications (`state['key'] = value`) are automatically tracked in the subsequent `Event.actions.state_delta`
- Changes are persisted by the `SessionService`

**Example Use Case:**
An `after_tool_callback` saves a `transaction_id` from the tool's result to `tool_context.state['last_transaction_id']`. A later `before_agent_callback` might read `state['user_tier']` to customize the agent's greeting.

### 3. Logging and Monitoring { #logging-and-monitoring }

**Pattern Overview:**
Add detailed logging at specific lifecycle points for observability and debugging.

**Implementation:**
- Implement callbacks (e.g., `before_agent_callback`, `after_tool_callback`, `after_model_callback`)
- Print or send structured logs containing:
  - Agent name
  - Tool name
  - Invocation ID
  - Relevant data from the context or arguments

**Example Use Case:**
Log messages like `INFO: [Invocation: e-123] Before Tool: search_api - Args: {'query': 'ADK'}`.

### 4. Caching { #caching }

**Pattern Overview:**
Avoid redundant LLM calls or tool executions by caching results.

**Implementation Steps:**
1. **Before Operation:** In `before_model_callback` or `before_tool_callback`:
   - Generate a cache key based on the request/arguments
   - Check `context.state` (or an external cache) for this key
   - If found, return the cached `LlmResponse` or result directly

2. **After Operation:** If cache miss occurred:
   - Use the corresponding `after_` callback to store the new result in the cache using the key

**Example Use Case:**
`before_tool_callback` for `get_stock_price(symbol)` checks `state[f"cache:stock:{symbol}"]`. If present, returns the cached price; otherwise, allows the API call and `after_tool_callback` saves the result to the state key.

### 5. Request/Response Modification { #request-response-modification }

**Pattern Overview:**
Alter data just before it's sent to the LLM/tool or just after it's received.

**Implementation Options:**
- **`before_model_callback`:** Modify `llm_request` (e.g., add system instructions based on `state`)
- **`after_model_callback`:** Modify the returned `LlmResponse` (e.g., format text, filter content)
- **`before_tool_callback`:** Modify the tool `args` dictionary (or Map in Java)
- **`after_tool_callback`:** Modify the `tool_response` dictionary (or Map in Java)

**Example Use Case:**
`before_model_callback` appends "User language preference: Spanish" to `llm_request.config.system_instruction` if `context.state['lang'] == 'es'`.

### 6. Conditional Skipping of Steps { #conditional-skipping-of-steps }

**Pattern Overview:**
Prevent standard operations (agent run, LLM call, tool execution) based on certain conditions.

**Implementation:**
- Return a value from a `before_` callback to skip the normal execution:
  - `Content` from `before_agent_callback`
  - `LlmResponse` from `before_model_callback`
  - `dict` from `before_tool_callback`
- The framework interprets this returned value as the result for that step

**Example Use Case:**
`before_tool_callback` checks `tool_context.state['api_quota_exceeded']`. If `True`, it returns `{'error': 'API quota exceeded'}`, preventing the actual tool function from running.

### 7. Tool-Specific Actions (Authentication & Summarization Control) { #tool-specific-actions-authentication-summarization-control }

**Pattern Overview:**
Handle actions specific to the tool lifecycle, primarily authentication and controlling LLM summarization of tool results.

**Implementation:**
Use `ToolContext` within tool callbacks (`before_tool_callback`, `after_tool_callback`):

- **Authentication:** Call `tool_context.request_credential(auth_config)` in `before_tool_callback` if credentials are required but not found (e.g., via `tool_context.get_auth_response` or state check). This initiates the auth flow.
- **Summarization:** Set `tool_context.actions.skip_summarization = True` if the raw dictionary output of the tool should be passed back to the LLM or potentially displayed directly, bypassing the default LLM summarization step.

**Example Use Case:**
A `before_tool_callback` for a secure API checks for an auth token in state; if missing, it calls `request_credential`. An `after_tool_callback` for a tool returning structured JSON might set `skip_summarization = True`.

### 8. Artifact Handling { #artifact-handling }

**Pattern Overview:**
Save or load session-related files or large data blobs during the agent lifecycle.

**Implementation:**
- **Saving:** Use `callback_context.save_artifact` / `await tool_context.save_artifact` to store data:
  - Generated reports
  - Logs
  - Intermediate data
- **Loading:** Use `load_artifact` to retrieve previously stored artifacts
- **Tracking:** Changes are tracked via `Event.actions.artifact_delta`

**Example Use Case:**
An `after_tool_callback` for a "generate_report" tool saves the output file using `await tool_context.save_artifact("report.pdf", report_part)`. A `before_agent_callback` might load a configuration artifact using `callback_context.load_artifact("agent_config.json")`.

## Best Practices for Callbacks

### Design Principles

**Keep Focused:**
Design each callback for a single, well-defined purpose (e.g., just logging, just validation). Avoid monolithic callbacks.

**Mind Performance:**
Callbacks execute synchronously within the agent's processing loop. Avoid long-running or blocking operations (network calls, heavy computation). Offload if necessary, but be aware this adds complexity.

### Error Handling

**Handle Errors Gracefully:**
- Use `try...except/catch` blocks within your callback functions
- Log errors appropriately
- Decide if the agent invocation should halt or attempt recovery
- Don't let callback errors crash the entire process

### State Management

**Manage State Carefully:**
- Be deliberate about reading from and writing to `context.state`
- Changes are immediately visible within the _current_ invocation and persisted at the end of the event processing
- Use specific state keys rather than modifying broad structures to avoid unintended side effects
- Consider using state prefixes (`State.APP_PREFIX`, `State.USER_PREFIX`, `State.TEMP_PREFIX`) for clarity, especially with persistent `SessionService` implementations

### Reliability

**Consider Idempotency:**
If a callback performs actions with external side effects (e.g., incrementing an external counter), design it to be idempotent (safe to run multiple times with the same input) if possible, to handle potential retries in the framework or your application.

### Testing & Documentation

**Test Thoroughly:**
- Unit test your callback functions using mock context objects
- Perform integration tests to ensure callbacks function correctly within the full agent flow

**Ensure Clarity:**
- Use descriptive names for your callback functions
- Add clear docstrings explaining their purpose, when they run, and any side effects (especially state modifications)

**Use Correct Context Type:**
Always use the specific context type provided (`CallbackContext` for agent/model, `ToolContext` for tools) to ensure access to the appropriate methods and properties.

By applying these patterns and best practices, you can effectively use callbacks to create more robust, observable, and customized agent behaviors in ADK.