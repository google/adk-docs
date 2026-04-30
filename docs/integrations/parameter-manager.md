---
catalog_title: Parameter Manager
catalog_description: A client for interacting with Google Cloud Parameter Manager.
---

# Parameter Manager

You can use the `ParameterManagerClient` to securely fetch configuration and parameters from the Google Cloud Parameter Manager.

## Initialize the client

You can initialize the `ParameterManagerClient` in a few ways:

### Using default credentials

If you are running on a Google Cloud environment with default credentials, you can initialize the client without any arguments:

```python
from google.adk.integrations.parameter_manager.parameter_client import ParameterManagerClient

# Using default credentials
client = ParameterManagerClient()
```

### Using a service account

You can provide a service account JSON string to authenticate:

```python
from google.adk.integrations.parameter_manager.parameter_client import ParameterManagerClient

client = ParameterManagerClient(service_account_json="...")
```

### Using an auth token

Alternatively, you can use an auth token:

```python
from google.adk.integrations.parameter_manager.parameter_client import ParameterManagerClient

client = ParameterManagerClient(auth_token="...")
```

## Retrieve a parameter

Once the client is initialized, you can retrieve a parameter by providing its full resource name:

```python
value = client.get_parameter("projects/my-project/locations/global/parameters/my-param/versions/latest")
```
