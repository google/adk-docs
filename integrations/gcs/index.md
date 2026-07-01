# Google Cloud Storage (GCS)

Supported in ADKPython v2.3.0

The `GCSToolset` and `GCSAdminToolset` allow ADK agents to interact with [Google Cloud Storage (GCS)](https://cloud.google.com/storage) to manage buckets and read/write objects.

## Use cases

- **Object Management**: Read, download, create, upload, list, metadata check, and delete GCS objects.
- **Bucket Management**: List cloud storage buckets, create new buckets, change configurations, such as enabling versioning or uniform bucket-level access, and delete buckets.
- **Data Integration**: Use cloud storage objects dynamically as part of the agent's workflow, such as processing files and ingestion.

## Prerequisites

- **Enable the Google Cloud Storage API** in the target Google Cloud project.
- **IAM Permissions**: The authenticated principal (Application Default Credentials, service account, or user) must have the correct permissions, including `roles/storage.objectAdmin` and `roles/storage.admin`, to perform GCS bucket and object operations.
- A Google Cloud Project ID configured.

## Authentication

The `GCSToolset` and `GCSAdminToolset` support several authentication mechanisms via `GCSCredentialsConfig`:

### Application Default Credentials

Recommended for local development and deployment to Google Cloud, including Agent Runtime, Cloud Run, and GKE.

```python
import google.auth
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# Load Application Default Credentials
credentials, _ = google.auth.default()

# Configure the toolset
credentials_config = GCSCredentialsConfig(credentials=credentials)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### Service Account

Allows providing credentials from a service account file.

```python
import google.auth
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# Load Service Account credentials
credentials, _ = google.auth.load_credentials_from_file('path/to/key.json')

# Configure the toolset
credentials_config = GCSCredentialsConfig(credentials=credentials)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### External Access Token

For acting on behalf of an end-user, such as via an OAuth2 flow or an external identity provider.

```python
from google.oauth2.credentials import Credentials
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# Assume 'user_token' is obtained via an external OAuth flow
credentials = Credentials(token=user_token)

# Configure the toolset
credentials_config = GCSCredentialsConfig(credentials=credentials)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### External Auth Providers

For platforms like Gemini Enterprise where the token is managed externally by the environment or platform.

```python
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# The key used to look up the access token in the session state
credentials_config = GCSCredentialsConfig(
    external_access_token_key="YOUR_AUTH_ID"
)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### Interactive Auth (ADK Web)

For interactive sessions using `adk web` interface to trigger an OAuth 2.0 login flow.

```python
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# Provide OAuth 2.0 Client ID and Secret
credentials_config = GCSCredentialsConfig(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

## Use with agent

The following example shows how to configure credentials and instantiate the storage toolset with write access enabled.

```python
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
```

## Available tools

The GCS integration split the capabilities into two main toolsets:

### GCS Storage Tools (`GCSToolset`)

| Tool                      | Description                                                                               |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| `gcs_get_bucket`          | Get metadata information about a GCS bucket.                                              |
| `gcs_list_objects`        | List object names in a GCS bucket. Supports optional prefix filtering and pagination.     |
| `gcs_get_object_metadata` | Get metadata properties of a specific GCS object (blob).                                  |
| `gcs_create_object`       | Create a new object (blob) in a bucket from in-memory string data or a local file upload. |
| `gcs_get_object_data`     | Get content of a GCS object as a string, or download it directly to a local file.         |
| `gcs_delete_objects`      | Delete multiple GCS objects (blobs) from a bucket.                                        |

### GCS Admin Tools (`GCSAdminToolset`)

| Tool                | Description                                                                         |
| ------------------- | ----------------------------------------------------------------------------------- |
| `gcs_list_buckets`  | List GCS bucket names in a Google Cloud project.                                    |
| `gcs_create_bucket` | Create a new GCS bucket in a specific location.                                     |
| `gcs_update_bucket` | Update properties of a GCS bucket (e.g. versioning or uniform bucket-level access). |
| `gcs_delete_bucket` | Delete a GCS bucket (bucket must be empty first).                                   |

## Sample agents

For complete, ready-to-run examples of GCS-powered agents with detailed authentication configurations, see:

- [GCS Storage Sample Agent](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/gcs)
- [GCS Admin Sample Agent](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/gcs_admin)

## Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [GitHub Repository](https://github.com/google/adk-python)
