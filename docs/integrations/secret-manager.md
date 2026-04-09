---
sidebar_label: Google Cloud Secret Manager
title: Google Cloud Secret Manager Integration
---

The ADK includes a built-in client for Google Cloud Secret Manager that simplifies retrieving secrets. This allows you to securely store and access sensitive information like API keys or other credentials required by your ADK tools.

The primary class for this integration is `SecretManagerClient`, which can be imported from `google.adk.integrations.secret_manager.secret_client`.

## Instantiating the Client

You can instantiate the `SecretManagerClient` in a few different ways, depending on your authentication needs.

### Using Application Default Credentials (ADC)

If your application is running in a Google Cloud environment (like Cloud Run or GKE) or you have configured the gcloud CLI locally with `gcloud auth application-default login`, you can instantiate the client without any arguments. It will automatically find the necessary credentials.

```python
from google.adk.integrations.secret_manager import secret_client

client = secret_client.SecretManagerClient()
```

### Using a Service Account

You can authenticate by passing the contents of a service account JSON key file as a string.

```python
from google.adk.integrations.secret_manager import secret_client
import json

# Assume 'service_account_dict' is a dictionary containing your service account key
service_account_json_string = json.dumps(service_account_dict)

client = secret_client.SecretManagerClient(
    service_account_json=service_account_json_string
)
```

### Using an OAuth 2.0 Access Token

If you have a pre-existing OAuth 2.0 access token, you can use it to instantiate the client.

```python
from google.adk.integrations.secret_manager import secret_client

auth_token = "your-oauth2-access-token"

client = secret_client.SecretManagerClient(auth_token=auth_token)
```

## Retrieving a Secret

Once the client is instantiated, you can retrieve a secret by calling the `get_secret()` method. This method requires the full resource name of the secret version you wish to access.

The resource name has the following format:
`projects/your-gcp-project-id/secrets/your-secret-name/versions/your-secret-version`

Typically, you will want to retrieve the latest version of a secret, which can be specified using `latest`.

```python
# Assuming 'client' is an instantiated SecretManagerClient
resource_name = "projects/my-gcp-project/secrets/api-key/versions/latest"

try:
    secret_value = client.get_secret(resource_name)
    print(f"Successfully retrieved secret: {secret_value}")
except Exception as e:
    print(f"Error retrieving secret: {e}")

# You can now use the secret_value with other ADK tools
# For example, passing it to a model's API key parameter
#
# from google.adk.models import some_model
#
# model = some_model.SomeModel(api_key=secret_value)

```
