# Observability for agents

Supported in ADKPython v0.1.0Go v0.1.0Kotlin v0.1.0

Observability for agents enables measurement of a system's internal state, including reasoning traces, tool calls, and latent model outputs, by analyzing its external telemetry and structured logs. When building agents, you may need these features to help debug and diagnose their in-process behavior. Basic input and output monitoring is typically insufficient for agents with any significant level of complexity.

Agent Development Kit (ADK) provides built-in observability through [logging](/observability/logging/), [metrics](/observability/metrics/), and [traces](/observability/traces/) to help you monitor and debug your agents. However, you may need to consider more advanced [observability ADK Integrations](/integrations/?topic=observability) for monitoring and analysis.

## Quick Start: Enabling Observability in Kotlin

In Kotlin, you can enable comprehensive observability by configuring OpenTelemetry for traces and using the `LoggingPlugin` for detailed console output.

```kotlin
// 1. Configure OpenTelemetry (Traces)
// ADK Kotlin uses GlobalOpenTelemetry to resolve its tracer on the JVM.
val spanExporter = OtlpGrpcSpanExporter.builder().setEndpoint("http://localhost:4317").build()

val resource =
    Resource.getDefault()
        .merge(
            Resource.create(
                Attributes.of(AttributeKey.stringKey("service.name"), "my-kotlin-agent"),
            ),
        )

val tracerProvider =
    SdkTracerProvider.builder()
        .addSpanProcessor(BatchSpanProcessor.builder(spanExporter).build())
        .setResource(resource)
        .build()

OpenTelemetrySdk.builder().setTracerProvider(tracerProvider).buildAndRegisterGlobal()

// 2. Optional: Configure ADK Telemetry behavior
// Enable capturing full message content in traces (use with caution in production)
TelemetryConfig.captureMessageContent = true

// 3. Initialize Agent and Runner with LoggingPlugin for console output
val agent = LlmAgent(name = "my_agent", model = Gemini(name = "gemini-flash-latest"))

val runner =
    InMemoryRunner(
        App(appName = "my_agent", rootAgent = agent, plugins = listOf(LoggingPlugin())),
    )

// The runner will now automatically emit traces via GlobalOpenTelemetry
// and log activity to the console via the LoggingPlugin.
runner.run(
    userId = "user123",
    sessionId = "session456",
    newMessage = Content.fromText(Role.USER, "Hello!"),
)
```

ADK Integrations for observability

For a list of pre-built observability libraries for ADK, see [Tools and Integrations](/integrations/?topic=observability).
