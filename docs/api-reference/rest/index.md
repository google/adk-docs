# REST API Reference

This page provides a complete reference for the REST API provided by the ADK web server.
For details on using the ADK REST API in practice, see
[Use the API Server](../../../runtime/api-server/).

!!! tip
    You can view an interactive API reference on a running ADK web server by browsing
    the `/docs` location, for example at: `http://localhost:8000/docs`

---

## Base URL

All endpoints are relative to the server base URL (e.g. `http://localhost:8000`).

---

## System

### `GET /health`

Returns the health status of the server.

**Response**

```json
{ "status": "ok" }
```

---

### `GET /version`

Returns the ADK version and runtime information.

**Response**

```json
{
  "version": "1.0.0",
  "language": "python",
  "language_version": "3.12.0"
}
```

---

### `GET /list-apps`

Lists all available agents (apps) registered with the server.

**Query Parameters**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `detailed` | boolean | No | If `true`, returns detailed app info. Defaults to `false`. |

**Response** (default)

```json
["my_agent", "another_agent"]
```

**Response** (`detailed=true`)

```json
{
  "apps": [
    {
      "name": "my_agent",
      "display_name": "My Agent",
      "description": "An example agent."
    }
  ]
}
```

---

## Agent Execution

### `POST /run`

Runs an agent synchronously and returns all events once the run completes.

**Request Body**

```json
{
  "app_name": "my_agent",
  "user_id": "user_123",
  "session_id": "session_abc",
  "new_message": {
    "role": "user",
    "parts": [{ "text": "Hello, agent!" }]
  },
  "streaming": false,
  "state_delta": {},
  "invocation_id": "optional-custom-id"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `app_name` | string | Yes | Name of the agent to run. |
| `user_id` | string | Yes | ID of the user. |
| `session_id` | string | Yes | ID of the session. Must exist unless `auto_create_session` is enabled. |
| `new_message` | Content | Yes | The user message to send to the agent. See [Content](#content). |
| `streaming` | boolean | No | Enable token streaming. Defaults to `false`. |
| `state_delta` | object | No | Key-value state changes to apply before running. |
| `invocation_id` | string | No | Optional custom invocation ID for tracing. |

**Response**

A JSON array of [Event](#event) objects.

```json
[
  {
    "id": "evt_001",
    "author": "my_agent",
    "timestamp": 1711234567.89,
    "content": {
      "role": "model",
      "parts": [{ "text": "Hello! How can I help?" }]
    }
  }
]
```

**Error Responses**

| Status | Description |
|--------|-------------|
| `404` | Session not found. |

---

### `POST /run_sse`

Runs an agent and streams events back using [Server-Sent Events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events).

**Request Body**

Same as [`POST /run`](#post-run).

**Response**

A stream of `text/event-stream` events. Each event data is a JSON-serialised [Event](#event) object.

```
data: {"id": "evt_001", "author": "my_agent", "content": {...}}

data: {"id": "evt_002", "author": "my_agent", "content": {...}}
```

**Error Responses**

| Status | Description |
|--------|-------------|
| `404` | Session not found. |

---

### `WebSocket /run_live`

Runs an agent over a persistent WebSocket connection for live bidirectional audio/text streaming.

**Query Parameters**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `app_name` | string | Yes | Name of the agent. |
| `user_id` | string | Yes | ID of the user. |
| `session_id` | string | Yes | ID of the session. Must exist. |
| `modalities` | string[] | No | Response modalities. Allowed: `"TEXT"`, `"AUDIO"`. Defaults to `["AUDIO"]`. |
| `proactive_audio` | boolean | No | Enable proactive audio responses. |
| `enable_affective_dialog` | boolean | No | Enable affective dialog features. |
| `enable_session_resumption` | boolean | No | Enable session resumption. |

**Connection Example**

```
ws://localhost:8000/run_live?app_name=my_agent&user_id=user_123&session_id=session_abc&modalities=TEXT
```

**Behaviour**

- Connect and send messages as JSON blobs to the agent.
- The server streams back events in real time.
- Closes with code `1002` if session is not found.
- Closes with code `1008` if the request origin is not allowed.

---

## Sessions

### `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}`

Retrieves a specific session.

**Path Parameters**

| Name | Description |
|------|-------------|
| `app_name` | Name of the agent. |
| `user_id` | ID of the user. |
| `session_id` | ID of the session. |

**Response**

A [Session](#session) object.

**Error Responses**

| Status | Description |
|--------|-------------|
| `404` | Session not found. |

---

### `GET /apps/{app_name}/users/{user_id}/sessions`

Lists all sessions for a user within an app. Eval-generated sessions are excluded.

**Path Parameters**

| Name | Description |
|------|-------------|
| `app_name` | Name of the agent. |
| `user_id` | ID of the user. |

**Response**

An array of [Session](#session) objects.

---

### `POST /apps/{app_name}/users/{user_id}/sessions`

Creates a new session.

**Path Parameters**

| Name | Description |
|------|-------------|
| `app_name` | Name of the agent. |
| `user_id` | ID of the user. |

**Request Body** *(optional)*

```json
{
  "session_id": "optional-custom-id",
  "state": { "key": "value" },
  "events": []
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | No | Custom session ID. Auto-generated if omitted. |
| `state` | object | No | Initial state key-value pairs. |
| `events` | Event[] | No | Initial events to seed the session with. |

**Response**

The created [Session](#session) object.

---

### `POST /apps/{app_name}/users/{user_id}/sessions/{session_id}` *(deprecated)*

Creates a session with a specific ID. Use [`POST /apps/{app_name}/users/{user_id}/sessions`](#post-appsapp_nameusersuser_idsessions) instead.

**Path Parameters**

| Name | Description |
|------|-------------|
| `app_name` | Name of the agent. |
| `user_id` | ID of the user. |
| `session_id` | Desired session ID. |

**Request Body** *(optional)*

```json
{ "state": { "key": "value" } }
```

**Response**

The created [Session](#session) object.

---

### `DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id}`

Deletes a session.

**Path Parameters**

| Name | Description |
|------|-------------|
| `app_name` | Name of the agent. |
| `user_id` | ID of the user. |
| `session_id` | ID of the session to delete. |

**Response**

`204 No Content`

---

### `PATCH /apps/{app_name}/users/{user_id}/sessions/{session_id}`

Updates the state of an existing session without running the agent.

**Path Parameters**

| Name | Description |
|------|-------------|
| `app_name` | Name of the agent. |
| `user_id` | ID of the user. |
| `session_id` | ID of the session to update. |

**Request Body**

```json
{ "state_delta": { "my_key": "new_value" } }
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `state_delta` | object | Yes | Key-value pairs to merge into the session state. |

**Response**

The updated [Session](#session) object.

**Error Responses**

| Status | Description |
|--------|-------------|
| `404` | Session not found. |

---

## Artifacts

Artifacts are named binary or structured files attached to a session (e.g. uploaded files, images, generated outputs).

### `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts`

Lists the names of all artifacts in a session.

**Response**

```json
["report.pdf", "image.png"]
```

---

### `POST /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts`

Uploads a new artifact (or a new version of an existing one).

**Request Body**

```json
{
  "filename": "report.pdf",
  "artifact": { "inline_data": { "mime_type": "application/pdf", "data": "<base64>" } },
  "custom_metadata": { "source": "agent_output" }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `filename` | string | Yes | Name of the artifact. |
| `artifact` | Part | Yes | The artifact content as a `google.genai.types.Part`. |
| `custom_metadata` | object | No | Optional metadata key-value pairs. |

**Response**

An [ArtifactVersion](#artifactversion) object with the new version number.

**Error Responses**

| Status | Description |
|--------|-------------|
| `400` | Invalid input. |
| `500` | Internal error saving artifact. |

---

### `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}`

Gets the latest (or a specific) version of an artifact.

**Path Parameters**

| Name | Description |
|------|-------------|
| `artifact_name` | Name of the artifact. |

**Query Parameters**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `version` | integer | No | Version number to retrieve. Defaults to latest. |

**Response**

A `google.genai.types.Part` object.

**Error Responses**

| Status | Description |
|--------|-------------|
| `404` | Artifact not found. |

---

### `DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}`

Deletes an artifact and all its versions.

**Response**

`204 No Content`

---

### `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions`

Lists all version numbers for an artifact.

**Response**

```json
[1, 2, 3]
```

---

### `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions/{version_id}`

Gets a specific version of an artifact.

**Path Parameters**

| Name | Description |
|------|-------------|
| `version_id` | Integer version number. |

**Response**

A `google.genai.types.Part` object.

**Error Responses**

| Status | Description |
|--------|-------------|
| `404` | Artifact version not found. |

---

### `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions/{version_id}/metadata`

Gets the metadata for a specific artifact version.

**Response**

An [ArtifactVersion](#artifactversion) object.

**Error Responses**

| Status | Description |
|--------|-------------|
| `404` | Artifact version not found. |

---

### `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions/metadata`

Lists metadata for all versions of an artifact.

**Response**

An array of [ArtifactVersion](#artifactversion) objects.

---

## Memory

### `PATCH /apps/{app_name}/users/{user_id}/memory`

Ingests events from a session into the user's long-term memory service.

**Path Parameters**

| Name | Description |
|------|-------------|
| `app_name` | Name of the agent. |
| `user_id` | ID of the user. |

**Request Body**

```json
{ "session_id": "session_abc" }
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | ID of the session whose events will be added to memory. |

**Response**

`204 No Content`

---

## Events

### `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/events/{event_id}/graph`

Returns a graph visualisation (Graphviz dot format) of the agent execution for a given event.

**Path Parameters**

| Name | Description |
|------|-------------|
| `event_id` | ID of the event. |

**Response**

A Graphviz dot string or structured graph object representing agent call hierarchy.

---

## Eval

### `GET /apps/{app_name}/eval-sets`

Lists all eval sets for an app.

**Response**

An array of eval set identifiers.

---

### `POST /apps/{app_name}/eval-sets`

Creates a new eval set.

**Request Body**

```json
{ "eval_set_id": "my_eval_set" }
```

**Response**

The created eval set object.

---

### `POST /apps/{app_name}/eval-sets/{eval_set_id}/add-session`

Adds an existing session to an eval set as a test case.

**Path Parameters**

| Name | Description |
|------|-------------|
| `eval_set_id` | ID of the eval set. |

**Request Body**

```json
{
  "session_id": "session_abc",
  "eval_case_id": "optional-case-id"
}
```

**Response**

The created eval case.

---

### `GET /apps/{app_name}/eval-sets/{eval_set_id}/eval-cases/{eval_case_id}`

Gets a specific eval case.

**Response**

An eval case object.

---

### `PUT /apps/{app_name}/eval-sets/{eval_set_id}/eval-cases/{eval_case_id}`

Updates an existing eval case.

**Response**

The updated eval case object.

---

### `DELETE /apps/{app_name}/eval-sets/{eval_set_id}/eval-cases/{eval_case_id}`

Deletes an eval case.

**Response**

`204 No Content`

---

### `POST /apps/{app_name}/eval-sets/{eval_set_id}/run`

Runs all eval cases in an eval set and returns results.

**Path Parameters**

| Name | Description |
|------|-------------|
| `eval_set_id` | ID of the eval set to run. |

**Response**

An array of eval result objects.

---

### `GET /apps/{app_name}/eval-results`

Lists all eval results for an app.

**Response**

An array of eval result summaries.

---

### `GET /apps/{app_name}/eval-results/{eval_result_id}`

Gets a specific eval result.

**Path Parameters**

| Name | Description |
|------|-------------|
| `eval_result_id` | ID of the eval result. |

**Response**

A detailed eval result object.

---

### `GET /apps/{app_name}/metrics-info`

Returns the available evaluation metrics for an app.

**Response**

An object describing supported metric names and their configurations.

---

## Debug *(dev only)*

These endpoints are intended for local development and debugging only.

### `GET /debug/trace/{event_id}`

Returns the OpenTelemetry trace data associated with a specific event.

**Path Parameters**

| Name | Description |
|------|-------------|
| `event_id` | ID of the event to look up. |

**Response**

A trace dictionary.

**Error Responses**

| Status | Description |
|--------|-------------|
| `404` | Trace not found. |

---

### `GET /debug/trace/session/{session_id}`

Returns all trace data for a session.

**Path Parameters**

| Name | Description |
|------|-------------|
| `session_id` | ID of the session. |

**Response**

An array of trace dictionaries.

---

### `GET /dev/build_graph/{app_name}`

Returns the agent graph structure for an app (used by the web UI).

**Path Parameters**

| Name | Description |
|------|-------------|
| `app_name` | Name of the agent. |

**Response**

A nested object representing the agent hierarchy and configuration.

**Error Responses**

| Status | Description |
|--------|-------------|
| `404` | App not found. |

---

## Builder *(web UI only)*

These endpoints power the agent editor UI. They are only registered when `web=True` and should not be used in production deployments.

### `POST /builder/save`

Saves agent YAML files. Supports saving to a temporary staging area (`tmp=true`) or directly to the agents directory.

**Query Parameters**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tmp` | boolean | No | Save to temporary staging area. Defaults to `false`. |

**Request Body**

`multipart/form-data` with one or more files. Each file's name must be in the format `{app_name}/{relative_path}`. Only `.yaml` and `.yml` files are accepted.

**Response**

`true` on success, `false` on failure.

---

### `POST /builder/app/{app_name}/cancel`

Discards all staged (temporary) changes for an app.

**Response**

`true` on success, `false` on failure.

---

### `GET /builder/app/{app_name}`

Retrieves the YAML source for an agent file.

**Path Parameters**

| Name | Description |
|------|-------------|
| `app_name` | Name of the agent. |

**Query Parameters**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file_path` | string | No | Relative path within the agent directory. Defaults to `root_agent.yaml`. |
| `tmp` | boolean | No | Read from the temporary staging area. Defaults to `false`. |

**Response**

The raw YAML file content (`application/x-yaml`).

---

## Data Models

### `Content`

Represents a message passed to or from an agent.

```json
{
  "role": "user",
  "parts": [
    { "text": "Hello!" }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | `"user"` or `"model"`. |
| `parts` | Part[] | List of content parts (text, inline data, function calls, etc.). |

---

### `Event`

Represents a single event emitted during an agent run.

```json
{
  "id": "evt_abc123",
  "invocation_id": "inv_xyz",
  "author": "my_agent",
  "timestamp": 1711234567.89,
  "content": { "role": "model", "parts": [{ "text": "Done!" }] },
  "actions": { "state_delta": {} },
  "error_code": null,
  "error_message": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique event ID. |
| `invocation_id` | string | ID of the agent invocation this event belongs to. |
| `author` | string | Name of the agent or `"user"` that authored the event. |
| `timestamp` | float | Unix timestamp. |
| `content` | Content | The event content. |
| `actions` | EventActions | Side-effects (state changes, artifact mutations, etc.). |
| `error_code` | string | Present if the event represents an error. |
| `error_message` | string | Human-readable error detail. |

---

### `Session`

```json
{
  "id": "session_abc",
  "app_name": "my_agent",
  "user_id": "user_123",
  "state": { "key": "value" },
  "events": [],
  "last_update_time": 1711234567.89
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Session ID. |
| `app_name` | string | Agent name. |
| `user_id` | string | User ID. |
| `state` | object | Current session state key-value map. |
| `events` | Event[] | All events in the session history. |
| `last_update_time` | float | Unix timestamp of last update. |

---

### `ArtifactVersion`

```json
{
  "filename": "report.pdf",
  "version": 2,
  "create_time": 1711234567.89,
  "custom_metadata": { "source": "agent_output" }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `filename` | string | Artifact name. |
| `version` | integer | Version number (1-indexed). |
| `create_time` | float | Unix timestamp when this version was created. |
| `custom_metadata` | objct | Optional metadata attached at upload time. |
