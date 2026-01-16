# Use the API Server

Supported in ADKPython v0.1.0TypeScript v0.2.0Go v0.1.0Java v0.1.0

Before you deploy your agent, you should test it to ensure that it is working as intended. Use the API server in ADK to expose your agents through a REST API for programmatic testing and integration.

## Start the API server

Use the following command to run your agent in an ADK API server:

```shell
adk api_server
```

```shell
npx adk api_server
```

```shell
go run agent.go web api
```

Make sure to update the port number.

With Maven, compile and run the ADK web server:

```console
mvn compile exec:java \
 -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
```

With Gradle, the `build.gradle` or `build.gradle.kts` build file should have the following Java plugin in its plugins section:

```groovy
plugins {
    id('java')
    // other plugins
}
```

Then, elsewhere in the build file, at the top-level, create a new task:

```groovy
tasks.register('runADKWebServer', JavaExec) {
    dependsOn classes
    classpath = sourceSets.main.runtimeClasspath
    mainClass = 'com.google.adk.web.AdkWebServer'
    args '--adk.agents.source-dir=src/main/java/agents', '--server.port=8080'
}
```

Finally, on the command-line, run the following command:

```console
gradle runADKWebServer
```

In Java, both the Dev UI and the API server are bundled together.

This command will launch a local web server, where you can run cURL commands or send API requests to test your agent. By default, the server runs on `http://localhost:8000`.

Advanced Usage and Debugging

For a complete reference on all available endpoints, request/response formats, and tips for debugging (including how to use the interactive API documentation), see the **ADK API Server Guide** below.

## Test locally

Testing locally involves launching a local web server, creating a session, and sending queries to your agent. First, ensure you are in the correct working directory.

For TypeScript, you should be inside the agent project directory itself.

```console
parent_folder/
└── my_sample_agent/  <-- For TypeScript, run commands from here
    └── agent.py (or Agent.java or agent.ts)
```

**Launch the Local Server**

Next, launch the local server using the commands listed above.

The output should appear similar to:

```shell
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

```shell
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://localhost:8000.                         |
+-----------------------------------------------------------------------------+
```

```shell
2025-05-13T23:32:08.972-06:00  INFO 37864 --- [ebServer.main()] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
2025-05-13T23:32:08.980-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : Started AdkWebServer in 1.15 seconds (process running for 2.877)
2025-05-13T23:32:08.981-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : AdkWebServer application started successfully.
```

Your server is now running locally. Ensure you use the correct ***port number*** in all the subsequent commands.

**Create a new session**

With the API server still running, open a new terminal window or tab and create a new session with the agent using:

```shell
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"key1": "value1", "key2": 42}'
```

Let's break down what's happening:

- `http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123`: This creates a new session for your agent `my_sample_agent`, which is the name of the agent folder, for a user ID (`u_123`) and for a session ID (`s_123`). You can replace `my_sample_agent` with the name of your agent folder. You can replace `u_123` with a specific user ID, and `s_123` with a specific session ID.
- `{"key1": "value1", "key2": 42}`: This is optional. You can use this to customize the agent's pre-existing state (dict) when creating the session.

This should return the session information if it was created successfully. The output should appear similar to:

```json
{"id":"s_123","appName":"my_sample_agent","userId":"u_123","state":{"key1":"value1","key2":42},"events":[],"lastUpdateTime":1743711430.022186}
```

Info

You cannot create multiple sessions with exactly the same user ID and session ID. If you try to, you may see a response, like: `{"detail":"Session already exists: s_123"}`. To fix this, you can either delete that session (e.g., `s_123`), or choose a different session ID.

**Send a query**

There are two ways to send queries via POST to your agent, via the `/run` or `/run_sse` routes.

- `POST http://localhost:8000/run`: collects all events as a list and returns the list all at once. Suitable for most users (if you are unsure, we recommend using this one).
- `POST http://localhost:8000/run_sse`: returns as Server-Sent-Events, which is a stream of event objects. Suitable for those who want to be notified as soon as the event is available. With `/run_sse`, you can also set `streaming` to `true` to enable token-level streaming.

**Using `/run`**

```shell
curl -X POST http://localhost:8000/run \
-H "Content-Type: application/json" \
-d '{
"appName": "my_sample_agent",
"userId": "u_123",
"sessionId": "s_123",
"newMessage": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
}
}'
```

In TypeScript, currently only `camelCase` field names are supported (e.g. `appName`, `userId`, `sessionId`, etc.).

If using `/run`, you will see the full output of events at the same time, as a list, which should appear similar to:

```json
[{"content":{"parts":[{"functionCall":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"2Btee6zW","timestamp":1743712220.385936},{"content":{"parts":[{"functionResponse":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"PmWibL2m","timestamp":1743712221.895042},{"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"sYT42eVC","timestamp":1743712221.899018}]
```

**Using `/run_sse`**

```shell
curl -X POST http://localhost:8000/run_sse \
-H "Content-Type: application/json" \
-d '{
"appName": "my_sample_agent",
"userId": "u_123",
"sessionId": "s_123",
"newMessage": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
},
"streaming": false
}'
```

You can set `streaming` to `true` to enable token-level streaming, which means the response will be returned to you in multiple chunks and the output should appear similar to:

```shell
data: {"content":{"parts":[{"functionCall":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"ptcjaZBa","timestamp":1743712255.313043}

data: {"content":{"parts":[{"functionResponse":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"5aocxjaq","timestamp":1743712257.387306}

data: {"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"rAnWGSiV","timestamp":1743712257.391317}
```

**Send a query with a base64 encoded file using `/run` or `/run_sse`**

```shell
curl -X POST http://localhost:8000/run \
-H 'Content-Type: application/json' \
-d '{
   "appName":"my_sample_agent",
   "userId":"u_123",
   "sessionId":"s_123",
   "newMessage":{
      "role":"user",
      "parts":[
         {
            "text":"Describe this image"
         },
         {
            "inlineData":{
               "displayName":"my_image.png",
               "data":"iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAACXBIWXMAAAsTAAALEwEAmpw...",
               "mimeType":"image/png"
            }
         }
      ]
   },
   "streaming":false
}'
```

Info

If you are using `/run_sse`, you should see each event as soon as it becomes available.

## Integrations

ADK uses [Callbacks](https://google.github.io/adk-docs/callbacks/index.md) to integrate with third-party observability tools. These integrations capture detailed traces of agent calls and interactions, which are crucial for understanding behavior, debugging issues, and evaluating performance.

- [Comet Opik](https://github.com/comet-ml/opik) is an open-source LLM observability and evaluation platform that [natively supports ADK](https://www.comet.com/docs/opik/tracing/integrations/adk).

## Deploy your agent

Now that you've verified the local operation of your agent, you're ready to move on to deploying your agent! Here are some ways you can deploy your agent:

- Deploy to [Agent Engine](https://google.github.io/adk-docs/deploy/agent-engine/index.md), a simple way to deploy your ADK agents to a managed service in Vertex AI on Google Cloud.
- Deploy to [Cloud Run](https://google.github.io/adk-docs/deploy/cloud-run/index.md) and have full control over how you scale and manage your agents using serverless architecture on Google Cloud.

## Interactive API docs

The API server automatically generates interactive API documentation using Swagger UI. This is an invaluable tool for exploring endpoints, understanding request formats, and testing your agent directly from your browser.

To access the interactive docs, start the API server and navigate to <http://localhost:8000/docs> in your web browser.

You will see a complete, interactive list of all available API endpoints, which you can expand to see detailed information about parameters, request bodies, and response schemas. You can even click "Try it out" to send live requests to your running agents.

## API endpoints

The following sections detail the primary endpoints for interacting with your agents.

JSON Naming Convention

- **Both Request and Response bodies** will use `camelCase` for field names (e.g., `"appName"`).

### Utility endpoints

#### List available agents

Returns a list of all agent applications discovered by the server.

- **Method:** `GET`
- **Path:** `/list-apps`

**Example Request**

```shell
curl -X GET http://localhost:8000/list-apps
```

**Example Response**

```json
["my_sample_agent", "another_agent"]
```

______________________________________________________________________

### Session management

Sessions store the state and event history for a specific user's interaction with an agent.

#### Update a session

Updates an existing session.

- **Method:** `PATCH`
- **Path:** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**Request Body**

```json
{
  "stateDelta": {
    "key1": "value1",
    "key2": 42
  }
}
```

**Example Request**

```shell
curl -X PATCH http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc \
  -H "Content-Type: application/json" \
  -d '{"stateDelta":{"visit_count": 5}}'
```

**Example Response**

```json
{"id":"s_abc","appName":"my_sample_agent","userId":"u_123","state":{"visit_count":5},"events":[],"lastUpdateTime":1743711430.022186}
```

#### Get a session

Retrieves the details of a specific session, including its current state and all associated events.

- **Method:** `GET`
- **Path:** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**Example Request**

```shell
curl -X GET http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**Example Response**

```json
{"id":"s_abc","appName":"my_sample_agent","userId":"u_123","state":{"visit_count":5},"events":[...],"lastUpdateTime":1743711430.022186}
```

#### Delete a session

Deletes a session and all of its associated data.

- **Method:** `DELETE`
- **Path:** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**Example Request**

```shell
curl -X DELETE http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**Example Response** A successful deletion returns an empty response with a `204 No Content` status code.

______________________________________________________________________

### Agent execution

These endpoints are used to send a new message to an agent and get a response.

#### Run agent (single response)

Executes the agent and returns all generated events in a single JSON array after the run is complete.

- **Method:** `POST`
- **Path:** `/run`

**Request Body**

```json
{
  "appName": "my_sample_agent",
  "userId": "u_123",
  "sessionId": "s_abc",
  "newMessage": {
    "role": "user",
    "parts": [
      { "text": "What is the capital of France?" }
    ]
  }
}
```

In TypeScript, currently only `camelCase` field names are supported (e.g. `appName`, `userId`, `sessionId`, etc.).

**Example Request**

```shell
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "my_sample_agent",
    "userId": "u_123",
    "sessionId": "s_abc",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the capital of France?"}]
    }
  }'
```

#### Run agent (streaming)

Executes the agent and streams events back to the client as they are generated using [Server-Sent Events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events).

- **Method:** `POST`
- **Path:** `/run_sse`

**Request Body** The request body is the same as for `/run`, with an additional optional `streaming` flag.

```json
{
  "appName": "my_sample_agent",
  "userId": "u_123",
  "sessionId": "s_abc",
  "newMessage": {
    "role": "user",
    "parts": [
      { "text": "What is the weather in New York?" }
    ]
  },
  "streaming": true
}
```

- `streaming`: (Optional) Set to `true` to enable token-level streaming for model responses. Defaults to `false`.

**Example Request**

```shell
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "my_sample_agent",
    "userId": "u_123",
    "sessionId": "s_abc",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the weather in New York?"}]
    },
    "streaming": false
  }'
```
