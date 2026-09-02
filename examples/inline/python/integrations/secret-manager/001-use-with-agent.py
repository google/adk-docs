import os

from google.adk import Agent
from google.adk.integrations.secret_manager.secret_client import SecretManagerClient

# Fetch secret from global Secret Manager
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
secret_id = os.environ.get("ADK_TEST_SECRET_ID")
secret_version = os.environ.get("ADK_TEST_SECRET_VERSION", "latest")

if not project_id or not secret_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT and ADK_TEST_SECRET_ID environment variables must be set.")

resource_name = f"projects/{project_id}/secrets/{secret_id}/versions/{secret_version}"

print("Fetching secret from global Secret Manager...")
# Initialize Secret Manager Client (Global)
client = SecretManagerClient()

# Fetch secret
try:
    secret_payload = client.get_secret(resource_name)
    print("Successfully fetched secret.")
    # The secret_payload can now be used by the agent or its tools as required.
except Exception as e:
    print(f"Error fetching secret: {e}")
    raise e

# Initialize Agent
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)

print("Agent initialized successfully.")