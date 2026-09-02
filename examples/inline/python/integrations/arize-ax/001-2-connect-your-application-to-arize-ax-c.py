from arize.otel import register

# Register with Arize AX
tracer_provider = register(
    space_id="your-space-id",      # Found in app space settings page
    api_key="your-api-key",        # Found in app space settings page
    project_name="your-project-name"  # Name this whatever you prefer
)

# Import and configure the automatic instrumentor from OpenInference
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

# Finish automatic instrumentation
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)