# Use the Command Line

Supported in ADKPython v0.1.0TypeScript v0.2.0Go v0.1.0Java v0.1.0

ADK provides an interactive terminal interface for testing your agents. This is useful for quick testing, scripted interactions, and CI/CD pipelines.

## Run an agent

Use the following command to run your agent in the ADK command line interface:

```shell
adk run my_agent
```

```shell
npx @google/adk-devtools run agent.ts
```

In Go, the command-line interface is not a standalone `adk` tool. Instead, you embed the launcher directly in your agent's `main.go`. The `full.NewLauncher()` helper bundles the console, web server, and other modes into a single binary, with **console as the default** when no subcommand keyword is given:

main.go

```go
import (
    "google.golang.org/adk/v2/cmd/launcher"
    "google.golang.org/adk/v2/cmd/launcher/full"
)

func main() {
    // ... build your agent and config ...
    l := full.NewLauncher()
    if err := l.Execute(ctx, config, os.Args[1:]); err != nil {
        log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
    }
}
```

Run the agent in console mode with either of the following commands:

```shell
go run agent.go           # console is the default sublauncher
go run agent.go console   # or explicitly name the console subcommand
```

Create an `AgentCliRunner` class (see [Java Quickstart](https://adk.dev/get-started/java/index.md)) and run:

```shell
mvn compile exec:java -Dexec.mainClass="com.example.agent.AgentCliRunner"
```

This starts an interactive session where you can type queries and see agent responses directly in your terminal.

```shell
Running agent my_agent, type exit to exit.
[user]: What's the weather in New York?
[my_agent]: The weather in New York is sunny with a temperature of 25°C.
[user]: exit
```

```shell
Running agent my_agent, type exit to exit.
[user]: What's the weather in New York?
[my_agent]: The weather in New York is sunny with a temperature of 25°C.
[user]: exit
```

```shell
User -> What's the weather in New York?

Agent -> The weather in New York is sunny with a temperature of 25°C.

User ->
```

To exit, press **Ctrl+C** or send EOF (**Ctrl+D**).

```shell
Running agent my_agent, type exit to exit.
[user]: What's the weather in New York?
[my_agent]: The weather in New York is sunny with a temperature of 25°C.
[user]: exit
```

## Session options

Python only

The `--save_session`, `--resume`, `--replay`, and `--session_id` options are available in the Python ADK CLI only. The Go console launcher does not support session save/resume/replay via command-line flags. In Go, session persistence is configured in code by providing a persistent `session.Service` implementation (such as `session/database`) to `launcher.Config`.

The `adk run` command includes options for saving, resuming, and replaying sessions.

### Save sessions

To save the session when you exit:

```shell
adk run --save_session path/to/my_agent
```

You'll be prompted to enter a session ID, and the session will be saved to `path/to/my_agent/<session_id>.session.json`.

You can also specify the session ID upfront:

```shell
adk run --save_session --session_id my_session path/to/my_agent
```

### Resume sessions

To continue a previously saved session:

```shell
adk run --resume path/to/my_agent/my_session.session.json path/to/my_agent
```

This loads the previous session state and event history, displays it, and allows you to continue the conversation.

### Replay sessions

To replay a session file without interactive input:

```shell
adk run --replay path/to/input.json path/to/my_agent
```

The input file should contain initial state and queries:

```json
{
  "state": {"key": "value"},
  "queries": ["What is 2 + 2?", "What is the capital of France?"]
}
```

## Storage options

Python only

The `--session_service_uri` and `--artifact_service_uri` command-line flags are available in the Python ADK CLI only. In Go, session and artifact services are configured in code when constructing `launcher.Config` — for example, using `session/database` for a persistent database-backed session store, or `artifact/gcsartifact` for Cloud Storage-backed artifacts.

| Option                   | Description                 | Default                                                      |
| ------------------------ | --------------------------- | ------------------------------------------------------------ |
| `--session_service_uri`  | Custom session storage URI  | Per-agent SQLite at `<agents_dir>/<agent>/.adk/session.db`   |
| `--artifact_service_uri` | Custom artifact storage URI | Per-agent directory at `<agents_dir>/<agent>/.adk/artifacts` |
| `--memory_service_uri`   | Custom memory service URI   | In-memory                                                    |

### Example with storage options

```shell
adk run --session_service_uri "sqlite:///my_sessions.db" path/to/my_agent
```

## All options

To send a single message and exit instead of starting an interactive session, pass the query as an argument:

```shell
adk run path/to/my_agent "hello"
```

| Option                                       | Description                                               |
| -------------------------------------------- | --------------------------------------------------------- |
| `--save_session`                             | Save the session to a JSON file on exit                   |
| `--session_id`                               | Session ID to use when saving                             |
| `--resume`                                   | Path to a saved session file to resume                    |
| `--replay`                                   | Path to an input file for non-interactive replay          |
| `--session_service_uri`                      | Custom session storage URI                                |
| `--artifact_service_uri`                     | Custom artifact storage URI                               |
| `--memory_service_uri`                       | Custom memory service URI                                 |
| `--use_local_storage/--no_use_local_storage` | Use the local `.adk` folder when no service URI is set    |
| `--state`                                    | Initial state for the run as a JSON string                |
| `--timeout`                                  | Timeout for a single turn or query, such as `30s` or `5m` |
| `--in_memory`                                | Do not persist session data                               |
| `--jsonl`                                    | Output structured JSONL instead of human-readable text    |
| `--default_llm_model`                        | Default model when the agent does not set one             |

Go flags differ from Python

The Go console launcher does not support `--save_session`, `--resume`, `--replay`, `--session_id`, `--session_service_uri`, or `--artifact_service_uri`. These are Python CLI features. Session and artifact services are configured in Go code via `launcher.Config`.

Flags are passed after the `console` keyword (or directly if `console` is the default):

| Flag                | Description                                | Default |
| ------------------- | ------------------------------------------ | ------- |
| `-streaming_mode`   | Streaming mode for agent responses (`none` | `sse`)  |
| `-shutdown-timeout` | Graceful shutdown wait time                | `2s`    |
| `-otel_to_cloud`    | Export OpenTelemetry data to GCP           | `false` |

For example, to force non-streaming output:

```shell
go run agent.go console -streaming_mode none
```

Or to force SSE streaming (token-by-token output):

```shell
go run agent.go -streaming_mode sse
```

## Usage telemetry

The ADK CLI collects anonymous usage telemetry to understand feature adoption, guide development priorities, and improve tool performance. Data collection is OFF by default until you explicitly choose to enable it.

Your telemetry preference is stored locally on your machine in `~/.adk/config.json`. You can manage telemetry data collection at any time through the terminal:

- **Enable**: `adk telemetry enable`
- **Disable**: `adk telemetry disable`
- **Check status**: `adk telemetry status`

You can also manually deactivate telemetry data collection at any time by opening `~/.adk/config.json` and setting the `telemetry` attribute to `false`:

```json
{
  "telemetry": false
}
```

**What data is collected**

- **Environment Properties**: Operating system information, runtime language and version, and installed ADK CLI version.
- **Command Execution Events**: Generic command and subcommand names, flags passed, execution duration, exit codes, and exception types if an error occurs. We also log a sequence number and an ephemeral session ID that is discarded after command execution.

**What data is not collected**

The CLI does not collect sensitive, private, or personal data, specifically:

- Arguments or parameter values passed to commands or flags, such as agent names, prompt strings, file paths.
- User credentials, usernames, API keys, OAuth tokens, or secrets.
- Google Cloud Project IDs or Cloud Account details.
- Source code files, file contents, or directory paths.
- Personally Identifiable Information (PII).
