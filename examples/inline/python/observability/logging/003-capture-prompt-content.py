from google.adk.agents.run_config import RunConfig
from google.adk.telemetry import ContentCapturingMode, TelemetryConfig

run_config = RunConfig(
    telemetry=TelemetryConfig(
        capture_message_content=ContentCapturingMode.SPAN_AND_EVENT,
    ),
)