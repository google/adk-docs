import os
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models.google_llm import Gemini
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin

os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-gcp-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_ENTERPRISE'] = 'True'

plugin = BigQueryAgentAnalyticsPlugin(
    project_id="your-gcp-project-id",
    dataset_id="your-big-query-dataset-id",
)

root_agent = Agent(
    model=Gemini(model="gemini-flash-latest"),
    name='my_agent',
    instruction="You are a helpful assistant.",
)

app = App(
    name="my_agent",
    root_agent=root_agent,
    plugins=[plugin],
)