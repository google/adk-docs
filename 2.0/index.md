# Welcome to ADK 2.0

Supported in ADKPython v2.0.0Go v2.0.0

ADK 2.0 introduces powerful tools for building sophisticated AI agents, and helps you structure agents to execute challenging tasks with more control, predictability, and reliability. ADK 2.0 is available for Python and Go and includes the following key features:

- [**Graph-based workflows**](/graphs/): Build deterministic agent workflows with more control over how tasks are routed and executed.
- [**Dynamic workflows**](/graphs/dynamic/): Use code-based logic for building more complex workflows including iterative loops and complex decision-based branching.
- [**Collaborative workflows**](/workflows/collaboration/): Build complex agent architectures with coordinator agents and multiple subagents working together.

Check out the linked topics above for more information, and try out the new way to build agents with ADK 2.0!

ADK Python v2.0.0 GA release

ADK Python 2.0 is released for general availability as of May 19, 2026.

ADK Go v2.0.0 GA release

ADK Go 2.0 is released for general availability as of June 30, 2026.

## ADK Python 1.x compatibility

ADK 2.0 is designed to be compatible with agents developed with ADK 1.x releases. However, there are a few breaking changes you should be aware of before upgrading an ADK 1.x project to ADK 2.0.

Breaking changes: ADK Python 1.x to 2.0 incompatibilities

There are several known incompatibilities and breaking changes introduced with ADK Python v2.0.0. Before upgrading, review these changes and take mitigation steps, if necessary.

The ADK 2.0 release introduces the Workflow Runtime, transitioning ADK from a hierarchical agent executor to a graph-based execution engine. In this new architecture, your Agents, Tools, and Functions are evaluated as individual *nodes* within a workflow graph. If you are upgrading from ADK 1.x, review the following breaking changes and migration steps to ensure a smooth transition for your production applications.

### Event Schema & Custom Session Storage

ADK 2.0 introduces new fields `node_info` and `output` to the core ***Event*** schema to track graph state and workflow outputs.

- **Custom Session storage:** If you have implemented a custom `BaseSessionService`, such as storing sessions in your own SQL or NoSQL databases using rigid columns, your underlying database schema must be updated to accommodate these new fields. Inserting a 2.0 ***Event*** into a rigid 1.x database table causes insertion or ORM deserialization failures. *However, if your custom session service stores events as serialized JSON blobs rather than mapping them to explicit columns, you do not need to update your schema.*
- **Strict JSON validation:** If your deployment includes downstream API gateways, mobile clients, or web frontends that perform strict JSON schema validation, including setting `additionalProperties: false`, then validation will reject 2.0 events until their expected schemas are updated.

**Migration action:** Update your database schemas and downstream client validators to expect and store the `node_info` and `output` fields on all Event payloads. Ensure all reader applications are updated to handle the 2.0 format before writing 2.0 sessions to a shared database.

### Agent Execution: BaseAgent to BaseNode

In ADK 1.x, Agents were standalone executors. In ADK 2.0, the ***BaseAgent*** class now subclasses ***BaseNode***. Agents are now evaluated as individual *nodes* within the new Workflow Graph engine.

- **Execution driver custom overrides:** The ABC contract has changed. Custom overrides of 1.x abstract methods, such as `_run_async_impl()` or `generate_content()`, are no longer the correct way to drive execution. The Workflow Graph engine completely bypasses these legacy overrides. If you inject custom telemetry or state management by overriding these methods, those calls are silently ignored.

**Migration action:** Move custom execution logic out of `run()` overrides. Instead, utilize the standardized `BeforeAgentCallback` and `AfterAgentCallback` interfaces to safely inject custom logic into the execution lifecycle.

### Context & Callbacks: In-Place Mutation

Bypassing the framework to manually append events is no longer safe.

- **Direct appending of events:** In ADK 1.x, some developers forcefully appended events to the session via `context.session.events.append(custom_event)`. In ADK 2.0, the Workflow runner needs strict control over event emission to manage state, graph routing, and streaming. Manually appending to the session list circumvents the graph engine and breaks determinism.

**Migration action:** Do not append events directly to the session, and do not use `enqueue_event` directly. You must now explicitly yield the event from within your node or agent so that the framework can manage its persistence, routing, and streaming natively.

### Error Handling & Automatic Retries

The ADK 2.0 framework now automatically catches exceptions to enable automatic retries, telemetry, and Human-in-the-Loop (HITL) pauses.

- **`Try...except` and `BaseException`:** In ADK 1.x, the framework did not have native automatic retries, so developers often wrote manual `try...except` loops inside their tools to prevent crashes. In ADK 2.0, if you migrate a tool and leave a broad `except Exception:` block inside it, this code masks the failure from the framework, permanently disabling the new 2.0 automatic retry mechanisms for that step. Furthermore, catching `BaseException` inadvertently traps `NodeInterruptedError`, which breaks the framework's ability to pause the workflow for Human-in-the-Loop (HITL) input.

**Migration Action:** Allow standard exceptions to propagate out of your tools so the framework can evaluate them against your configured ***RetryConfig***, such as `RetryConfig(max_attempts=3)`. Never catch ***BaseException*** unless you are explicitly re-raising the exception.

If you encounter additional ADK Python 1.0 to ADK 2.0 incompatibilities, report them through the [issue tracker](https://github.com/google/adk-python/issues/new?template=bug_report.md&labels=v2).

### Installing ADK Python 1.x

If you want to update ADK, but are not yet ready to update to ADK 2.0, make sure to specify an ADK version during installation or use the compatible release `~=` operator as shown below. ADK 1.0 has the following system requirements:

- **Python 3.10** or later
- `pip` for installing packages

To install the latest version of ADK 1.x, follow these steps:

1. Enable a Python virtual environment. See below for instructions.

1. Install the package using pip using compatible release `~=` operator for ADK 1.x:

   ```bash
   pip install "google-adk~=1.0"
   ```

Recommended: Create and activate a Python virtual environment

Create a Python virtual environment:

```shell
python3 -m venv .venv
```

Activate the Python virtual environment:

```console
.venv\Scripts\activate.bat
```

```console
.venv\Scripts\Activate.ps1
```

```bash
source .venv/bin/activate
```

## ADK Go 1.x compatibility

ADK Go 2.0 is designed to be compatible with agents developed with ADK Go 1.x releases. However, there are a few breaking changes you should be aware of before upgrading an ADK Go 1.x project to ADK Go 2.0.

Breaking changes: ADK Go 1.x to 2.0 incompatibilities

There are several known incompatibilities and breaking changes introduced with ADK Go v2.0.0. Before upgrading, review these changes and take mitigation steps, if necessary.

The ADK Go 2.0 release introduces the Workflow Runtime, transitioning ADK Go from a hierarchical agent executor to a graph-based execution engine. In this new architecture, your Agents, Tools, and Functions are evaluated as individual *nodes* within a workflow graph. If you are upgrading from ADK Go 1.x, review the following breaking changes and migration steps.

### Module import path

ADK Go 2.0 uses a new major version module path. You must update all import paths in your Go source files and your `go.mod` file.

- **1.x import path:** `google.golang.org/adk`
- **2.0 import path:** `google.golang.org/adk/v2`

**Migration action:** Run `go get google.golang.org/adk/v2` and update all import statements in your source files from `google.golang.org/adk/...` to `google.golang.org/adk/v2/...`.

### Agent Execution: Agent interface changes

In ADK Go 1.x, agents implemented the `agent.Agent` interface by providing a `Run` method. In ADK Go 2.0, agents are evaluated as individual *nodes* within the new Workflow Graph engine.

- **Execution driver custom overrides:** Custom agent types that override internal execution behavior may no longer work as expected. The Workflow Graph engine manages execution scheduling and event emission, and custom implementations that bypass these mechanisms are silently ignored.

**Migration action:** Move custom execution logic into standardized `BeforeAgentCallback` and `AfterAgentCallback` hooks to safely inject custom logic into the execution lifecycle.

### Event Construction: `session.NewEvent` signature change

`session.NewEvent` now requires a `context.Context` as its first argument:

```go
// Before (ADK Go 1.x)
ev := session.NewEvent(ctx.InvocationID())
// or
ev := session.NewEventWithContext(ctx, ctx.InvocationID())

// After (ADK Go 2.0)
ev := session.NewEvent(ctx, ctx.InvocationID())
```

The event ID and timestamp are now obtained through the `platform` package, so a time or UUID provider installed on `ctx` controls them. This lets workflow engines produce deterministic, replay-safe events. The previous parameterless-context form and the temporary `NewEventWithContext` helper are removed.

**Migration action:** Pass the context already in scope as the first argument to `session.NewEvent`. Any `context.Context` works — the `ctx` of an agent, tool, or callback (which embed `context.Context`), a request context, or in tests, `t.Context()`. If a helper that calls `NewEvent` does not yet receive a context, add a `ctx context.Context` parameter and thread it down from the caller. Avoid creating a new `context.Background()` mid-call-chain; reserve that for `main`, `init`, and top-level test setup.

### Event Schema & Custom Session Storage

ADK Go 2.0 adds five new fields to the core ***Event*** struct to support graph routing, workflow state, and human-in-the-loop pausing:

| Go field                       | Serialized name                                      | Purpose                                                              |
| ------------------------------ | ---------------------------------------------------- | -------------------------------------------------------------------- |
| `IsolationScope string`        | `isolationScope` (`json:"isolationScope,omitempty"`) | Restricts which agent contexts see this event in LLM prompt history. |
| `Routes []string`              | `Routes` (no JSON tag)                               | Routing keys emitted by a node to drive conditional edge dispatch.   |
| `RequestedInput *RequestInput` | `RequestedInput` (no JSON tag)                       | Signals that a workflow node is pausing for human input.             |
| `Output any`                   | `Output` (no JSON tag)                               | Generic data output from a workflow node.                            |
| `NodeInfo *NodeInfo`           | `nodeInfo` (`json:"nodeInfo,omitempty"`)             | Workflow-node metadata identifying which node emitted the event.     |

- **Custom session storage:** If you have implemented a custom `session.Service`, such as storing sessions in your own SQL or NoSQL databases with rigid schemas, your underlying database schema must be updated to accommodate all five new fields. Inserting a 2.0 ***Event*** into a rigid 1.x database table causes insertion or deserialization failures. *However, if your custom session service stores events as serialized JSON blobs, you do not need to update your schema.*

**Migration action:** Update your database schemas and downstream client validators to expect and store the five new fields on all Event payloads. Pay particular attention to `Routes`, `RequestedInput`, and `Output`, which have no JSON struct tags and therefore serialize under their Go field names exactly as shown above.

If you encounter additional ADK Go 1.0 to ADK 2.0 incompatibilities, report them through the [issue tracker](https://github.com/google/adk-go/issues/new?template=bug_report.md&labels=v2).

### Installing ADK Go 1.x

If you want to continue using ADK Go 1.x and are not yet ready to upgrade to ADK Go 2.0, pin your dependency to the 1.x release line:

```shell
go get google.golang.org/adk@v1
```

## Next steps

Read the developer guides for building agents with ADK 2.0 features:

- [**Graph-based workflows**](/graphs/)
- [**Collaborative agents**](/workflows/collaboration/)
- [**Dynamic workflows**](/graphs/dynamic/)

Check out these ADK 2.0 code samples for testing and inspiration:

- [**Workflow samples**](https://github.com/google/adk-python/tree/main/contributing/samples/workflows)

- [**Collaborative task samples**](https://github.com/google/adk-python/tree/main/contributing/samples/multi_agent)

- [**All workflow agents samples**](https://github.com/google/adk-go/tree/main/examples/workflow)

- [**Collaborative task sample**](https://github.com/google/adk-go/tree/main/examples/multiagent/collaboration)

Thanks for checking out ADK 2.0! We look forward to your feedback — let us know on [ADK Go](https://github.com/google/adk-go/issues/new) or [ADK Python](https://github.com/google/adk-python/issues/new).
