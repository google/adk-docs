# Supported methods

## Summary
<table>
    <thead>
        <tr>
            <th rowspan="2">
                Method
            </th>
            <th rowspan="2">
                Description
            </th>
            <th rowspan="2">
                Reference
            </th>
            <th colspan="4" style="text-align:center">
                Support
            </th>
        </tr>
        <tr>
            <th>
            Python
            </th>
            <th>
            Go
            </th>
            <th>
            Java
            </th>
        </tr>
    </thead>
    <body>
        <tr>
            <th colspan="6">Session management</td>
        </tr>
        <tr>
            <td>create_session</td>
            <td>Deprecated, use async_create_session instead</td>
            <td></td>
            <td>&#9989;</td>
            <td>&#10060;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>async_create_session</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>async_get_session</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>async_list_sessions</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>async_delete_session</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>get_session</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>list_sessions</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>delete_session</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>async_get_session</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>async_list_sessions</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>async_create_session</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>async_delete_session</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <th colspan="6">Memory</td>
        </tr>
        <tr>
            <td>async_add_session_to_memory</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>async_search_memory</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <th colspan="6">Query</td>
        </tr>
        <tr>
            <td>stream_query</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>async_stream_query</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <td>streaming_agent_run_with_events</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
        <tr>
            <th colspan="6">Others</td>
        </tr>
        <tr>
            <td>register_feedback</td>
            <td></td>
            <td></td>
            <td>&#9989;</td>
            <td>&#9989;</td>
            <td>&#10060;</td>
        </tr>
    </body>
</table>

# AIPlatform API for Agent Engine
## Calling the Agent Engine methods
### AIPlatform AgentEngine Input
Input is JSON formatted according to the following schema.
```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://google.com/agentengine/aiplatform.json",
    "title": "AgentEngine wrapper for AIPlatform",
    "description": "",
    "type": "object",
    "properties": {
        "class_method": {
            "description": "Name of the underlying method",
            "type": "string"
        },
        "input": {
            "description": "Method-specific input",
            "type": "object"
        },
    },
    "required": [
        "class_method",
        "input"
    ]
}
```
### Response for streaming
For early failures, before the streaming starts, the response is just like the one for [non-streaming version](#response-for-non-streaming)

After the streaming starts, it provides a stream of JSON-formatted data one per line. JSON object is specific for the called method.
In case of an error, the HTTP status is already 200 and cannot be changed, so the error is formatted as an streaming data as well, according to the schema:
```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://google.com/agentengine/streaming_error.json",
    "title": "Defines how streaming errors are formatted",
    "description": "",
    "type": "object",
    "properties": {
        "error": {
            "description": "Object describing the error",
            "type": "object"
        },
    },
    "required": [
        "error"
    ]
}
```

### Response for non-streaming
On success, the response is JSON-formatted response specific for the called method (class_method).

On failure, the response is JSON-formatted error similar to the following one:
```json
{
  "error": {
    "code": 400,
    "message": "Reasoning Engine Execution failed.\nPlease refer to our documentation (https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/troubleshooting/use) for checking logs and other troubleshooting tips.\nError Details: {\"detail\":\"Agent Engine Error: An error occurred during invocation. Exception: 404 NOT_FOUND. {'error': {'code': 404, 'message': 'Session projects/kdroste-adk-2025-12/locations/us-central1/reasoningEngines/3765669545214214144/sessions/7177615616973471745 not found.', 'status': 'NOT_FOUND'}}\\nRequest Data: {'session_id': '7177615616973471745', 'user_id': 'u_12345_non_existing'}\"}",
    "status": "FAILED_PRECONDITION",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.DebugInfo",
        "detail": "[ORIGINAL ERROR] generic::failed_precondition: Reasoning Engine Execution failed.\nPlease refer to our documentation (https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/troubleshooting/use) for checking logs and other troubleshooting tips.\nError Details: {\"detail\":\"Agent Engine Error: An error occurred during invocation. Exception: 404 NOT_FOUND. {'error': {'code': 404, 'message': 'Session projects/kdroste-adk-2025-12/locations/us-central1/reasoningEngines/3765669545214214144/sessions/7177615616973471745 not found.', 'status': 'NOT_FOUND'}}\\nRequest Data: {'session_id': '7177615616973471745', 'user_id': 'u_12345_non_existing'}\"} [google.rpc.error_details_ext] { message: \"Reasoning Engine Execution failed.\\nPlease refer to our documentation (https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/troubleshooting/use) for checking logs and other troubleshooting tips.\\nError Details: {\\\"detail\\\":\\\"Agent Engine Error: An error occurred during invocation. Exception: 404 NOT_FOUND. {\\'error\\': {\\'code\\': 404, \\'message\\': \\'Session projects/kdroste-adk-2025-12/locations/us-central1/reasoningEngines/3765669545214214144/sessions/7177615616973471745 not found.\\', \\'status\\': \\'NOT_FOUND\\'}}\\\\nRequest Data: {\\'session_id\\': \\'7177615616973471745\\', \\'user_id\\': \\'u_12345_non_existing\\'}\\\"}\" }"
      }
    ]
  }
}
```




# Create session
You should use `async_create_session`. `create_session` is deprecated. 

## `async_create_session`
### Input
Input adheres to the general [schema](#aiplatform-agentengine-input) :
```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://google.com/agentengine/async_create_session.schema.json",
    "title": "Request for async_create_session",
    "description": "",
    "type": "object",
    "properties": {
        "user_id": {
            "description": "UserID",
            "type": "string"
        },
        "state": {
            "description": "Dictionary mapping string to objects",
            "type": "object"
        },
    },
    "required": [
        "user_id"
    ]
}
```

### Semantics
Creates a new session 

### Output
Session data is returned 

#TODO(kdroste): create a schema for that
```go
type SessionData struct {
	UserID         string          `json:"user_id"`
	LastUpdateTime float64         `json:"last_update_time"`
	AppName        string          `json:"app_name"`
	ID             string          `json:"id"`
	State          map[string]any  `json:"state"`
	Events         []session.Event `json:"events"`
}
```

### Error handling
In case of a failure and error is returned using the non-streaming version of [response](#response-for-non-streaming)

### Invocation examples

```bash
curl -v \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
https://${LOCATION_ID}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION_ID}/reasoningEngines/${RESOURCE_ID}:query -d '{
    "class_method": "async_create_session",
    "input": {
        "user_id": "u_12345",
    }
}'
```