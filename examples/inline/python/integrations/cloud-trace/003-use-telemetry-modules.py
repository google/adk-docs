from google.adk.telemetry import google_cloud
from google.adk.telemetry.setup import maybe_set_otel_providers

# Get GCP exporters configuration
hooks = google_cloud.get_gcp_exporters(enable_cloud_tracing=True)

# Initialize and set global OTel providers
maybe_set_otel_providers(otel_hooks_to_setup=[hooks])