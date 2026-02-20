# REST API Reference

This page provides a reference for the REST API provided by the ADK web server. For details on using the ADK REST API in practice, see [Use the API Server](/adk-docs/runtime/api-server/).

Tip

You can view an updated API reference on a running ADK web server by browsing the `/docs` location, for example at: `http://localhost:8000/docs`

## Endpoints

### `/run`

This endpoint executes an agent run. It takes a JSON payload with the details of the run and returns a list of events generated during the run.

**Request Body**

The request body should be a JSON object with the following fields:

- `app_name` (string, required): The name of the agent to run.
- `user_id` (string, required): The ID of the user.
- `session_id` (string, required): The ID of the session.
- `new_message` (Content, required): The new message to send to the agent. See the [Content](#content-object) section for more details.
- `streaming` (boolean, optional): Whether to use streaming. Defaults to `false`.
- `state_delta` (object, optional): A delta of the state to apply before the run.

**Response Body**

The response body is a JSON array of [Event](#event-object) objects.

### `/run_sse`

This endpoint executes an agent run using Server-Sent Events (SSE) for streaming responses. It takes the same JSON payload as the `/run` endpoint.

**Request Body**

The request body is the same as for the `/run` endpoint.

**Response Body**

The response is a stream of Server-Sent Events. Each event is a JSON object representing an [Event](#event-object).

## Objects

### `Content` object

The `Content` object represents the content of a message. It has the following structure:

```json
{
  "parts": [
    {
      "text": "..."
    }
  ],
  "role": "..."
}
```

- `parts`: A list of parts. Each part can be either text or a function call.
- `role`: The role of the author of the message (e.g., "user", "model").

### `Event` object

The `Event` object represents an event that occurred during an agent run. It has a complex structure with many optional fields. The most important fields are:

- `id`: The ID of the event.
- `timestamp`: The timestamp of the event.
- `author`: The author of the event.
- `content`: The content of the event.
