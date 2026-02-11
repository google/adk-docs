# Observability for agents

Observability for agents enables measurement of a system's internal
state, including reasoning traces, tool calls, and latent model outputs, by
analyzing its external telemetry and structured logs. When building
agents, you may need these features to help debug and diagnose their
in-process behavior. Basic input and output monitoring is typically
insufficient for agents with any significant level of complexity.

Agent Development Kit (ADK) provides configurable
[logging](/adk-docs/observability/logging/)
functionality for monitoring and debugging agents. However, you may
need to consider more advanced
[observability ADK Integrations](/adk-docs/integrations/?topic=observability)
for monitoring and analysis.

!!! tip "ADK Integrations for observability"
    For a list of pre-built observability libraries for ADK, see
    [Tools and Integrations](/adk-docs/integrations/?topic=observability).
