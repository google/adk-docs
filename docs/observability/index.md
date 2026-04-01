# Observability for agents

Observability for agents enables measurement of a system's internal
state, including reasoning traces, tool calls, and latent model outputs, by
analyzing its external telemetry and structured logs. When building
agents, you may need these features to help debug and diagnose their
in-process behavior. Basic input and output monitoring is typically
insufficient for agents with any significant level of complexity.

Agent Development Kit (ADK) provides comprehensive observability features:

- **[Logging](/adk-docs/observability/logging/)** - Configure structured logging for agent activity and debugging
- **[OpenTelemetry Tracing for Agent Engine](/adk-docs/observability/tracing-agent-engine/)** - Implement distributed tracing for production deployments

For additional observability capabilities, consider
[observability ADK Integrations](/adk-docs/integrations/?topic=observability)
for monitoring and analysis.

!!! tip "ADK Integrations for observability"
    For a list of pre-built observability libraries for ADK, see
    [Tools and Integrations](/adk-docs/integrations/?topic=observability).
