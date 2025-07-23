# A2A Under the Hood

This guide is for advanced users who want to understand the underlying
mechanisms of the A2A integration in the ADK.

## The A2A Server: `adk api_server --a2a`

When you run `adk api_server --a2a`, the ADK does the following:

1. **Starts a FastAPI Server:** The core of the A2A server is a standard
   FastAPI application.
2. **Generates an OpenAPI Specification:** The ADK inspects your agent's `tools`
   and generates a compliant OpenAPI 3.0 specification. This specification is
   available at the `/openapi.json` endpoint and is crucial for the
   `RemoteA2AAgent` to understand the remote agent's capabilities.
3. **Creates A2A-Compliant Endpoints:** The ADK creates the necessary endpoints
   to handle A2A requests, including `/a2a/{agent_name}`.
4. **Handles Data Conversion:** The server automatically converts incoming A2A
   requests into the ADK's internal event format, and converts the ADK's
   response events back into the A2A format. The ADK uses Pydantic models to
   ensure that the data is valid and conforms to the A2A specification.

## The A2A Client: `RemoteA2AAgent`

When you instantiate a `RemoteA2AAgent`, it does the following:

1. **Fetches the OpenAPI Specification:** The `RemoteA2AAgent` sends a GET
   request to the remote agent's `/openapi.json` endpoint to fetch its OpenAPI
   specification.
2. **Dynamically Creates Tools:** The `RemoteA2AAgent` parses the OpenAPI
   specification and dynamically creates a set of tools that correspond to the
   remote agent's capabilities. This is how the `root_agent` knows how to use
   the remote agent's `tools`.
3. **Handles HTTP Requests:** When you use one of the dynamically created tools,
   the `RemoteA2AAgent` sends a POST request to the remote agent's
   `/a2a/{agent_name}` endpoint with the tool call information.
4. **Handles Responses:** The `RemoteA2AAgent` receives the A2A response from
   the remote agent and converts it into an ADK event that the `root_agent` can
   understand.

## The `LongRunningFunctionTool` Protocol Flow

The Human-in-the-Loop (HITL) pattern relies on a specific, asynchronous
protocol flow orchestrated by the `LongRunningFunctionTool`. This is not a
single HTTP request-response, but a two-step process.

### Step 1: The Initial Tool Call (Request for Work)

1.  The `root_agent` decides to call the remote tool (e.g., `approval_request`).
2.  The `RemoteA2AAgent` sends a **POST** request to the remote agent's A2A
    endpoint (e.g., `/a2a/approval_agent`). The request body contains the
    arguments for the `start_func` of the `LongRunningFunctionTool` (e.g.,
    `amount` and `purpose`).
3.  The remote A2A server receives this request and executes **only** the
    `start_func`.
4.  The server immediately sends back a **`200 OK`** response. The body of this
    response contains a special **`tool_code`** with a `status` of **`pending`**
    and a unique `ticket_id`.

    ```json
    {
      "tool_code": "print(default_api.some_tool(ticket_id='abc-123', status='pending'))"
    }
    ```

### Step 2: The Final Tool Response (Callback with Result)

1.  The `root_agent` receives the `pending` status and the `ticket_id`. It can
    now inform the user that the task is awaiting external input.
2.  At a later time, a separate process (like the `manual_approval.py` script)
    gets the final result from the human.
3.  This process constructs a **new** message to the `root_agent`, this time
    providing a `tool_response` that includes the original `ticket_id` and the
    final output (e.g., `approved: True`).
4.  The `root_agent`'s conversation loop processes this `tool_response`. The
    `RemoteA2AAgent` recognizes this as the completion of a pending task and
    sends a **second POST** request to the same remote agent endpoint.
5.  This second request's body is different. It contains the arguments for the
    `end_func` of the `LongRunningFunctionTool` (e.g., `ticket_id`,
    `approved`, and `comment`).
6.  The remote A2A server receives this request, finds the matching tool, and
    executes the `end_func` with the provided arguments, completing the
    workflow.
7.  The final result from the `end_func` is returned in the response to the
    `root_agent`.

This two-step, callback-style mechanism allows the `root_agent` to remain
responsive while waiting for long-running, asynchronous tasks to complete.

## Overriding the Default Behavior

For advanced use cases, you can override the default A2A behavior by creating
your own `A2AClient` and `A2AExecutor`. This allows you to customize the HTTP
requests, error handling, and other aspects of the A2A communication.