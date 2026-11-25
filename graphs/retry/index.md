# Handle node failures with retries and timeouts

Supported in ADKPython v2.0.0TypeScript v2.0.0Go v2.0.0Java v1.14.0Kotlin v1.2.0

Nodes in a graph-based workflow often call services that fail intermittently or respond slowly, such as model APIs, remote tools, and databases. Agent Development Kit (ADK) lets you attach a retry policy and a timeout to each node, so a node can recover from a transient failure without failing the whole workflow, and a stalled node fails after a set time instead of blocking the workflow. Use retries and timeouts functionality to:

- Retry a tool call that fails with a connection error, waiting longer between each attempt so the remote service has time to recover.
- Stop a model call that has not responded within 30 seconds, and try it again.
- Retry only the errors that are likely to succeed on a second attempt, and fail immediately on all other errors.

A node that has a retry policy runs again when it fails, until an attempt succeeds or the node reaches its maximum attempts. Only then does the failure reach the rest of the workflow. Nodes without a retry policy are not retried.

Experimental in TypeScript, Java, and Kotlin

In ADK TypeScript, ADK Java, and ADK Kotlin, the workflow APIs that node retries and timeouts depend on are experimental releases. These APIs may have limitations and are not recommended for production use in those languages.

## Get started

The following example builds a two-node workflow. The first node calls an unreliable forecast service, and its configuration allows three attempts in total, waits one second before the first retry, retries only service errors and timeouts, and limits each attempt to 10 seconds. The second node reports the result.

```python
import random

from google.adk import Context
from google.adk import Event
from google.adk import Workflow
from google.adk.workflow import NodeTimeoutError
from google.adk.workflow import RetryConfig
from google.adk.workflow import node


class ServiceUnavailableError(Exception):
  """Stands in for a transient failure from a remote service."""


@node(
    retry_config=RetryConfig(
        max_attempts=3,  # 1 original attempt + 2 retries
        initial_delay=1.0,  # seconds before the first retry
        exceptions=[ServiceUnavailableError, NodeTimeoutError],
    ),
    timeout=10.0,  # seconds allowed for each attempt
)
async def fetch_forecast(ctx: Context):
  """Simulates an unreliable call to a forecast service."""
  yield Event(message=f"Fetching forecast, attempt {ctx.attempt_count}")
  if random.random() < 0.5:
    raise ServiceUnavailableError("Forecast service unavailable")
  yield "sunny"


def report_forecast(node_input: str):
  return Event(message=f"The forecast is {node_input}.")


root_agent = Workflow(
    name="forecast_workflow",
    edges=[("START", fetch_forecast, report_forecast)],
)
```

Pass `retryConfig` and `timeout` as options to `node()`. Delays and timeouts are in seconds.

```typescript
import {
  createEvent,
  node,
  NodeContext,
  NodeTimeoutError,
  Workflow,
} from '@google/adk';

/** Stands in for a transient failure from a remote service. */
class ServiceUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ServiceUnavailableError';
  }
}

/** Simulates an unreliable call to a forecast service. */
async function* fetchForecast(ctx: NodeContext) {
  yield createEvent({
    content: {
      role: 'model',
      parts: [{ text: `Fetching forecast, attempt ${ctx.attemptCount}` }],
    },
  });
  if (Math.random() < 0.5) {
    throw new ServiceUnavailableError('Forecast service unavailable');
  }
  yield 'sunny';
}

function reportForecast(_ctx: NodeContext, forecast: string) {
  return `The forecast is ${forecast}.`;
}

export const rootAgent = new Workflow({
  name: 'forecast_workflow',
  edges: [
    [
      'START',
      node(fetchForecast, {
        name: 'fetch_forecast',
        retryConfig: {
          maxAttempts: 3, // 1 original attempt + 2 retries
          initialDelay: 1, // seconds before the first retry
          exceptions: [ServiceUnavailableError, NodeTimeoutError],
        },
        timeout: 10, // seconds allowed for each attempt
      }),
      node(reportForecast, { name: 'report_forecast' }),
    ],
  ],
});
```

Set `RetryConfig` and `Timeout` in the `workflow.NodeConfig` that you pass to the node constructor. Start from `workflow.DefaultRetryConfig()` and change only the fields you need.

```go
// errServiceUnavailable stands in for a transient failure from a remote service.
var errServiceUnavailable = errors.New("forecast service unavailable")

func newForecastWorkflow() (agent.Agent, error) {
    // fetchForecast simulates a slow, unreliable service call. It watches
    // ctx.Done() so that the node's timeout can stop it.
    fetchForecast := func(ctx agent.Context, _ any) (string, error) {
        select {
        case <-time.After(200 * time.Millisecond):
        case <-ctx.Done():
            return "", ctx.Err()
        }
        if rand.Float64() < 0.5 {
            return "", errServiceUnavailable
        }
        return "sunny", nil
    }

    // Start from the default policy and override only what you need.
    retry := workflow.DefaultRetryConfig()
    retry.MaxAttempts = 3 // 1 original attempt + 2 retries
    retry.InitialDelay = time.Second
    // Retry only transient failures: the service error and the node's own
    // timeout, which surfaces as context.DeadlineExceeded.
    retry.ShouldRetry = func(err error) bool {
        return errors.Is(err, errServiceUnavailable) ||
            errors.Is(err, context.DeadlineExceeded)
    }

    fetchNode := workflow.NewFunctionNode("fetch_forecast", fetchForecast,
        workflow.NodeConfig{
            RetryConfig: retry,
            Timeout:     10 * time.Second, // limit for each attempt
        },
    )

    reportNode := workflow.NewFunctionNode("report_forecast",
        func(_ agent.Context, forecast string) (string, error) {
            return "The forecast is " + forecast + ".", nil
        },
        workflow.NodeConfig{},
    )

    return workflowagent.New(workflowagent.Config{
        Name:  "forecast_workflow",
        Edges: workflow.Chain(workflow.Start, fetchNode, reportNode),
    })
}
```

Return a `NodeConfig` from the `config()` method of your `Node` implementation.

```java
import com.google.adk.agents.Context;
import com.google.adk.workflow.Edge;
import com.google.adk.workflow.Node;
import com.google.adk.workflow.NodeConfig;
import com.google.adk.workflow.NodeTimeoutException;
import com.google.adk.workflow.RetryConfig;
import com.google.adk.workflow.Start;
import com.google.adk.workflow.Workflow;
import io.reactivex.rxjava3.core.Flowable;
import java.time.Duration;
import java.util.concurrent.ThreadLocalRandom;

public final class ForecastWorkflow {

  /** Stands in for a transient failure from a remote service. */
  static final class ServiceUnavailableException extends RuntimeException {
    ServiceUnavailableException(String message) {
      super(message);
    }
  }

  /** Simulates an unreliable call to a forecast service. */
  static final class FetchForecastNode implements Node {
    private static final NodeConfig CONFIG =
        NodeConfig.builder()
            .retryConfig(
                RetryConfig.builder()
                    .maxAttempts(3) // 1 original attempt + 2 retries
                    .initialDelay(Duration.ofSeconds(1))
                    .exceptionClasses(
                        ServiceUnavailableException.class, NodeTimeoutException.class)
                    .build())
            .timeout(Duration.ofSeconds(10)) // limit for each attempt
            .build();

    @Override
    public String name() {
      return "fetch_forecast";
    }

    @Override
    public NodeConfig config() {
      return CONFIG;
    }

    @Override
    public Flowable<?> runNode(Context context, Object nodeInput) {
      if (ThreadLocalRandom.current().nextDouble() < 0.5) {
        return Flowable.error(
            new ServiceUnavailableException(
                "Forecast service unavailable, attempt " + context.attemptCount()));
      }
      return Flowable.just("sunny");
    }
  }

  public static Workflow create() {
    return Workflow.builder()
        .name("forecast_workflow")
        .edges(new Edge(Start.INSTANCE, new FetchForecastNode()))
        .build();
  }
}
```

Pass a `NodeConfig` to `node()`. The workflow APIs require an opt-in to `ExperimentalWorkflowApi`.

```kotlin
import com.google.adk.kt.annotations.ExperimentalWorkflowApi
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Role
import com.google.adk.kt.workflow.NodeConfig
import com.google.adk.kt.workflow.RetryConfig
import com.google.adk.kt.workflow.Start
import com.google.adk.kt.workflow.Workflow
import com.google.adk.kt.workflow.emit
import com.google.adk.kt.workflow.node
import com.google.adk.kt.workflow.workflow
import kotlin.random.Random
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.Duration.Companion.seconds
import kotlinx.coroutines.delay

/** Stands in for a transient failure from a remote service. */
class ServiceUnavailableException(message: String) : Exception(message)

/** Simulates an unreliable call to a forecast service. */
val fetchForecast =
  node<Any?, String>(
    "fetch_forecast",
    config =
      NodeConfig(
        retryConfig =
          RetryConfig(
            maxAttempts = 3, // 1 original attempt + 2 retries
            initialDelay = 1.seconds,
            // A timed-out attempt is reported as "NodeTimeoutError".
            exceptions = listOf("ServiceUnavailableException", "NodeTimeoutError"),
          ),
        timeout = 10.seconds, // limit for each attempt
      ),
  ) { context, _ ->
    emit(Content.fromText(Role.MODEL, "Fetching forecast, attempt ${context.attemptCount}"))
    delay(200.milliseconds)
    if (Random.nextDouble() < 0.5) throw ServiceUnavailableException("Forecast service unavailable")
    "sunny"
  }

val reportForecast = node<String, String>("report_forecast") { _, forecast -> "The forecast is $forecast." }

fun createForecastWorkflow(): Workflow =
  workflow("forecast_workflow") { chain(Start, fetchForecast, reportForecast) }
```

When `fetch_forecast` fails with a service error or exceeds its timeout, the ADK agent waits, then runs the node again with the same input. The next node, `report_forecast`, runs only after an attempt succeeds. If all three attempts fail, the node fails with the error from the last attempt, and the workflow fails with it. In all languages except Go, the node context provides an attempt count, which starts at 1, so your code can tell which attempt is running.

## Configure retries

A retry policy controls three things: how many times a node runs, how long ADK waits between attempts, and which errors start a retry.

- **Attempts:** The maximum attempts value counts the original attempt, so a value of 3 allows 2 retries. A value of 0 or 1 disables retries.
- **Delay:** The wait before the first retry is the initial delay. ADK multiplies each later wait by the backoff factor, so the defaults of 1 second and 2.0 give base waits of 1, 2, 4, and 8 seconds before jitter. The maximum delay caps each wait.
- **Jitter:** The system adds or subtracts a random amount, up to the jitter factor times the delay, from each wait, so that many nodes that fail at the same time do not all retry at the same moment. Set jitter to 0 for fixed delays, for example in tests.

The following decisions have the most effect on how well retries work for your workflow:

- **Retry only transient errors.** By default, a retry policy retries almost every error. An error caused by bad input or a bug fails the same way on every attempt, so retrying it only delays the failure. List the error types that can succeed on a later attempt, such as connection errors, rate limit errors, and timeouts. For details on how each language matches errors, see [Configuration options](#configuration-options).
- **Set the policy on the node that can fail.** In Python, Java, and Kotlin, you can also attach a retry policy to a nested workflow, and a failure of any node inside it then retries the nested workflow. Setting the policy on the individual node that calls the unreliable service retries less work and gives you more control.
- **Make retried work safe to repeat.** A retry runs the whole node again. If the node writes to an external system before it fails, the write can happen more than once. Design those operations so that repeating them has no extra effect, or move the side effect into a separate node that runs after the unreliable call succeeds.

## Set node timeouts

A timeout limits how long a single attempt of a node can run. The limit applies to each attempt separately, not to the total time across retries, and the wait between attempts does not count toward it. When an attempt runs past its timeout, ADK stops the attempt and treats it as a failure:

- In Python, TypeScript, Java, and Kotlin, the attempt fails with a node timeout error, as listed in the following table.
- In Go, the node's context reaches its deadline, and the attempt fails with `context.DeadlineExceeded`.

ADK retries a timed-out attempt like any other failure when the node has a retry policy that covers the timeout error. If you list specific error types in the policy, include the timeout error, as the [Get started](#get-started) example does. A timeout without a retry policy fails the node the first time it fires.

| Language   | Timeout setting                           | Timeout error              | Name to list in a retry policy             |
| ---------- | ----------------------------------------- | -------------------------- | ------------------------------------------ |
| Python     | `timeout` in seconds                      | `NodeTimeoutError`         | `NodeTimeoutError`                         |
| TypeScript | `timeout` in seconds                      | `NodeTimeoutError`         | `NodeTimeoutError`                         |
| Go         | `NodeConfig.Timeout` as a `time.Duration` | `context.DeadlineExceeded` | Match it in `ShouldRetry` with `errors.Is` |
| Java       | `NodeConfig.timeout` as a `Duration`      | `NodeTimeoutException`     | `NodeTimeoutException`                     |
| Kotlin     | `NodeConfig.timeout` as a `Duration`      | `NodeTimeoutError`         | `NodeTimeoutError`                         |

Stopping an attempt relies on cancellation, and how cancellation reaches your code depends on the language:

- **Go:** The node's `agent.Context` carries the deadline. Pass it to the calls your node makes, or check `ctx.Done()`, so the node returns when the deadline passes.
- **TypeScript:** ADK stops reading events from the node when the timeout fires. To also cancel work the node has started, such as an HTTP request, pass `ctx.abortSignal` to that work.
- **Kotlin:** ADK runs the attempt in a coroutine and cancels the coroutine when the timeout fires. Code that does not reach a suspension point keeps running until it does.

## Configuration options

The retry policy has the same options in every language. Durations are in seconds in Python and TypeScript, and use the language's duration type in Go, Java, and Kotlin.

| Option           | Default    | Description                                                                           |
| ---------------- | ---------- | ------------------------------------------------------------------------------------- |
| Maximum attempts | `5`        | Attempts including the original one. A value of 0 or 1 disables retries.              |
| Initial delay    | 1 second   | Wait before the first retry.                                                          |
| Maximum delay    | 60 seconds | Upper limit on the wait between attempts.                                             |
| Backoff factor   | `2.0`      | Multiplier applied to the wait after each attempt.                                    |
| Jitter           | `1.0`      | Random spread applied to each wait, as a fraction of the wait. `0` gives fixed waits. |
| Errors to retry  | All errors | Errors that start a retry. See the following list.                                    |

Each language selects the errors to retry in its own way:

- **Python:** The `exceptions` setting takes exception classes or class names. A listed class also matches its subclasses.
- **TypeScript:** The `exceptions` setting takes error classes or class names. An error matches when its class name or its `name` property is in the list. ADK does not check the class hierarchy.
- **Go:** The `ShouldRetry` setting is a function that receives the error and returns `true` to retry it. The default retries every error except `workflow.ErrInputValidation`.
- **Java:** The `exceptions` setting takes simple class names, which match exactly. The `exceptionClasses` setting takes classes, which also match their subclasses. ADK never retries a `WorkflowConfigurationException`.
- **Kotlin:** The `exceptions` setting takes simple class names, which match exactly. ADK never retries a `WorkflowConfigurationException`.

Go: unset fields are zero, not defaults

In Go, a `RetryConfig` built as a struct literal uses the zero value for every field that you do not set, not the default value. For example, `&workflow.RetryConfig{MaxAttempts: 3}` retries with no delay between attempts. Start from `workflow.DefaultRetryConfig()` and override fields instead. Also, Go applies jitter after it applies `MaxDelay`, so a single wait can be longer than `MaxDelay` by up to the jitter fraction.

## Limitations

- **Attempt count is not saved.** ADK keeps the attempt count in memory for the current run of the node. If the workflow pauses, for example for [human input](/graphs/human-input/), or the application restarts, a node that runs again after the workflow resumes starts from attempt 1 with all of its attempts available.

## Next steps

- [Build graph routes for agent workflows](/graphs/routes/): connect nodes with sequences, branches, and parallel paths.
- [Data handling for agent workflows](/graphs/data-handling/): pass data between nodes.
- [Human input for agent workflows](/graphs/human-input/): pause a workflow to ask a person for input.
