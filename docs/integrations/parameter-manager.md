---
catalog_title: Parameter Manager
catalog_description: A client for interacting with Google Cloud Parameter Manager.
---

# Parameter Manager

The Parameter Manager integration provides a client for interacting with Google Cloud Parameter Manager.

## Initialize the ParameterManagerClient

You can initialize the `ParameterManagerClient` in a few ways:

**Using default credentials**

```python
from google.adk.integrations.parameter_manager.parameter_client import ParameterManagerClient

client = ParameterManagerClient()
```

**With a service account JSON string**

```python
client = ParameterManagerClient(service_account_json="...")
```

**With an auth token**

```python
client = ParameterManagerClient(auth_token="...")
```

## Retrieve a parameter

To retrieve a parameter, use the `get_parameter` method with the full resource name of the parameter version:

```python
value = client.get_parameter("projects/my-project/locations/global/parameters/my-param/versions/latest")
```
