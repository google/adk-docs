import os

from google.adk import Agent
from google.adk.integrations.parameter_manager.parameter_client import ParameterManagerClient

# Fetch parameter from global Parameter Manager
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
parameter_id = os.environ.get("ADK_TEST_PARAMETER_ID")
parameter_version = os.environ.get("ADK_TEST_PARAMETER_VERSION", "latest")

if not project_id or not parameter_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT and ADK_TEST_PARAMETER_ID environment variables must be set.")

resource_name = f"projects/{project_id}/locations/global/parameters/{parameter_id}/versions/{parameter_version}"

print("Fetching parameter from global Parameter Manager...")
# Initialize Parameter Manager Client
client = ParameterManagerClient()

# Fetch parameter
try:
    parameter_payload = client.get_parameter(resource_name)
    print("Successfully fetched parameter.")
except Exception as e:
    print(f"Error fetching parameter: {e}")
    raise e

# Initialize Agent
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)

print("Agent initialized successfully.")