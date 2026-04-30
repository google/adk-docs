# Use the Web Interface

Supported in ADKPython v0.1.0TypeScript v0.2.0Go v0.1.0Java v0.1.0

The ADK web interface lets you test your agents directly in the browser. This tool provides a simple way to interactively develop and debug your agents.

Caution: ADK Web for development only

ADK Web is ***not meant for use in production deployments***. You should use ADK Web for development and debugging purposes only.

## Start the web interface

Use the following command to run your agent in the ADK web interface:

```shell
adk web
```

```shell
npx adk web
```

```shell
go run agent.go web api webui
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

In Java, the Web Interface and the API server are bundled together.

The server starts on `http://localhost:8000` by default:

```shell
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://localhost:8000.                         |
+-----------------------------------------------------------------------------+
```

## Features

Key features of the ADK web interface include:

- **Chat interface**: Send messages to your agents and view responses in real-time
- **Session management**: Create and switch between sessions
- **State inspection**: View and modify session state during development
- **Event history**: Inspect all events generated during agent execution

## Common options

| Option                   | Description                        | Default                |
| ------------------------ | ---------------------------------- | ---------------------- |
| `--port`                 | Port to run the server on          | `8000`                 |
| `--host`                 | Host binding address               | `127.0.0.1`            |
| `--session_service_uri`  | Custom session storage URI         | In-memory              |
| `--artifact_service_uri` | Custom artifact storage URI        | Local `.adk/artifacts` |
| `--reload/--no-reload`   | Enable auto-reload on code changes | `true`                 |

### Example with options

```shell
adk web --port 3000 --session_service_uri "sqlite:///sessions.db"
```
