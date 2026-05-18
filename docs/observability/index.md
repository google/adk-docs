# Observability for agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-kotlin">Kotlin v0.1</span>
</div>

Observability for agents enables measurement of a system's internal
state, including reasoning traces, tool calls, and latent model outputs, by
analyzing its external telemetry and structured logs. When building
agents, you may need these features to help debug and diagnose their
in-process behavior. Basic input and output monitoring is typically
insufficient for agents with any significant level of complexity.

Agent Development Kit (ADK) provides built-in observability through
[logging](/observability/logging/), [metrics](/observability/metrics/), and
[traces](/observability/traces/) to help you monitor and debug your agents. However, you may need to consider more
advanced [observability ADK Integrations](/integrations/?topic=observability)
for monitoring and analysis.

## Quick Start: Enabling Observability in Kotlin

In Kotlin, you can enable comprehensive observability by configuring OpenTelemetry for traces and using the `LoggingPlugin` for detailed console output.

```kotlin
--8<-- "examples/kotlin/snippets/observability/SetupExample.kt:full_example"
```

!!! tip "ADK Integrations for observability"
    For a list of pre-built observability libraries for ADK, see
    [Tools and Integrations](/integrations/?topic=observability).
