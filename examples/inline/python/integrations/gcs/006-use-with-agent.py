import google.auth
from google.adk.agents.llm_agent import LlmAgent
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.settings import GCSToolSettings, Capabilities
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# 1. Load Application Default Credentials (ADC)
application_default_credentials, _ = google.auth.default()

# 2. Configure credentials config
credentials_config = GCSCredentialsConfig(
    credentials=application_default_credentials
)

# 3. Configure settings (allow read and write operations)
tool_settings = GCSToolSettings(capabilities=[Capabilities.READ_WRITE])

# 4. Instantiate the GCS Toolset
gcs_toolset = GCSToolset(
    credentials_config=credentials_config,
    gcs_tool_settings=tool_settings
)

# 5. Define an LLM Agent with the toolset
agent = LlmAgent(
    model="gemini-2.5-flash",
    name="gcs_agent",
    description="Agent for interacting with GCS buckets and objects.",
    instruction="""
        You are a storage assistant agent. Use the GCS tools to answer questions,
        list objects, upload files, or perform admin tasks as requested.
    """,
    tools=[gcs_toolset]
)