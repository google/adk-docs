# my_agent/agent.py

from dotenv import load_dotenv

load_dotenv()

# OpenTelemetry imports
from opentelemetry.sdk import trace as trace_sdk

# Galileo span processor (auto-configures OTLP headers & endpoint from env vars)
from galileo import otel

# OpenInference instrumentation for ADK
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

# Create tracer provider and register Galileo span processor
tracer_provider = trace_sdk.TracerProvider()
galileo_span_processor = otel.GalileoSpanProcessor()
tracer_provider.add_span_processor(galileo_span_processor)

# Instrument Google ADK with OpenInference (this captures inputs/outputs)
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)