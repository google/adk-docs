
# Catalog Frontmatter

|element|content|
|-----|-----|
| catalog_title| Google Cloud Parameter Manager|
| catalog_description      | A client for interacting with Google Cloud Parameter Manager   |
---

# Google Cloud Secrets Manager
## Google Cloud Parameter Manager
The Parameter Manager integration is an extension of the Secret Manager class, offering a lightweight client designed to fetch processed parameter data from Google Cloud. This tool is ideal for agents that require configuration settings to be handled independently of the agent’s internal process.  If you want to know more about all options, features or capabilities that this integration facilitates, click here.
The following code snippets represent the usage of different credential types as shown below.

# Integration Name

**ParameterManagerClient**

This integration provides a small client for fetching Google Cloud parameter values, which is perfect for agents that need to store their configuration settings externally.

# Use cases 

## With different authentication credentials

### Using default credentials
```client = ParameterManagerClient()```

### Or with a service account json string
```client = ParameterManagerClient(service_account_json="...")```

### Or with an auth token
```client = ParameterManagerClient(auth_token="...")```

### To use a regional Parameter Manager endpoint, pass location:

```client = ParameterManagerClient(location="us-central1")```

# Prerequisites

### Only the class ParameterManagerClient
``` from google.adk.integrations.parameter_manager.parameter_client import ParameterManagerClient```

# Explaining how to retrieve a parameter 
```value =client.get_parameter("projects/my-project/locations/global/parameters/my-param/versions/latest")```
## Resources

- [Deploy Preview](https://deploy-preview-1729--adk-docs-preview.netlify.app/integrations/parameter-manager/#initialize-the-client)
- [GitHub Repository]([src/google/adk/integrations/parameter_manager/parameter_client.py](https://github.com/google/adk-python/blob/main/src/google/adk/integrations/parameter_manager/parameter_client.py))
- [Google Cloud](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/overview)
- [Google AI Studio](https://aistudio-preprod.corp.google.com/prompts/1C4ldgvJkKT6qHtFUeiZKcTiDGOmlP1ze?resourceKey=0-IldDiiPSogAPqBzVfz5jSw)

## Complete usage of ParameterManagerClient
Here is a complete example of how to initialize the client and use it to fetch a parameter within an ADK application.

==python==

```python
import os
from google.adk.integrations.parameter_manager.parameter_client import ParameterManagerClient

def fetch_external_api_key():
  -- 1. Initialize the Client
  client = ParameterManagerClient()

  -- 2. Define the resource name
  # Format: projects/{project_id}/locations/{location}/parameters/{parameter_id}
   project_id = "your-gcp-project"
   param_name = f"projects/{project_id}/locations/global/parameters/my-api-key"

  try:
        -- 3. Fetch the parameter payload
        -- This automatically resolves linked secrets if configured
        parameter_payload = client.get_parameter(param_name)
        
  print(f"Successfully fetched parameter: {parameter_payload}")
        return parameter_payload
        
  except Exception as e:
        print(f"Error retrieving parameter: {e}")
        return None

-- Example usage in an agent tool
  result = fetch_external_api_key()
```
