# my_bq_agent/agent.py
import os
import google.auth
from google.adk.apps import App
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin, BigQueryLoggerConfig
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig


# --- OpenTelemetry note (no setup required for BQAA) ---
# The BQAA plugin does NOT export OTel spans of its own. It tracks the
# parent-child hierarchy on an internal stack: the root invocation span
# reuses the ambient OTel span's id (as a 16-hex string) when one is
# active, and child BQAA spans are generated internally as 16-hex
# strings. The plugin's `trace_id`
# column inherits from whichever OpenTelemetry span is active in the
# surrounding runtime when the agent runs:
#   * Agent Engine wires its invocation span automatically, so
#     `trace_id` in BigQuery joins to Cloud Trace out of the box.
#   * Locally, framework-instrumented runners open an invocation span
#     for you.
#   * If neither is available, the plugin falls back to a per-invocation
#     trace_id and the parent-child hierarchy is still preserved in
#     BigQuery — no OTel setup needed.
# Setting a bare `TracerProvider` with no ambient span will NOT cause
# `trace_id` to be populated with a "real" OTel id; only an *active*
# span does. See the "Tracing and observability" section for details.

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BIG_QUERY_DATASET_ID", "your-big-query-dataset-id")
# GOOGLE_CLOUD_LOCATION must be a valid Agent Platform region (e.g., "us-central1").
# BQ_LOCATION is the BigQuery dataset location, which can be a multi-region
# like "US" or "EU", or a single region like "us-central1".
VERTEX_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
BQ_LOCATION = os.environ.get("BQ_LOCATION", "US")
GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME", "your-gcs-bucket-name") # Optional

if PROJECT_ID == "your-gcp-project-id":
    raise ValueError("Please set GOOGLE_CLOUD_PROJECT or update the code.")

# --- CRITICAL: Set environment variables BEFORE Gemini instantiation ---
os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = VERTEX_LOCATION
os.environ['GOOGLE_GENAI_USE_ENTERPRISE'] = 'True'

# --- Initialize the Plugin with Config ---
bq_config = BigQueryLoggerConfig(
    enabled=True,
    gcs_bucket_name=GCS_BUCKET, # Enable GCS offloading for multimodal content
    log_multi_modal_content=True,
    max_content_length=500 * 1024, # 500 KB limit for inline text
    batch_size=1, # Default is 1 for low latency, increase for high throughput
    shutdown_timeout=10.0
)

bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id=DATASET_ID,
    table_id="agent_events", # default table name is agent_events
    config=bq_config,
    location=BQ_LOCATION
)

# --- Initialize Tools and Model ---
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials)
)

llm = Gemini(model="gemini-flash-latest")

root_agent = Agent(
    model=llm,
    name='my_bq_agent',
    instruction="You are a helpful assistant with access to BigQuery tools.",
    tools=[bigquery_toolset]
)

# --- Create the App ---
app = App(
    name="my_bq_agent",
    root_agent=root_agent,
    plugins=[bq_logging_plugin],
)