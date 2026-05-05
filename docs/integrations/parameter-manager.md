---
catalog_title: Parameter Manager
catalog_description: Retrieve configuration values from Google Cloud Parameter Manager
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["config", "google-cloud"]
---

# Parameter Manager

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.31.0</span><span class="lst-preview">Experimental</span>
</div>

The Parameter Manager integration provides a small client for retrieving
rendered parameter values from Google Cloud Parameter Manager. Use it when your
agent needs configuration values that should be managed outside the agent
process.

## Initialize the client

If you do not pass credentials explicitly, `ParameterManagerClient` uses default
Google Cloud credentials.

```python
from google.adk.integrations.parameter_manager.parameter_client import (
    ParameterManagerClient,
)

client = ParameterManagerClient()
```

You can also initialize the client with a service account JSON string:

```python
client = ParameterManagerClient(
    service_account_json='{"type": "service_account", "...": "..."}',
)
```

Or with an existing authorization token:

```python
client = ParameterManagerClient(auth_token="ya29...")
```

To use a regional Parameter Manager endpoint, pass `location`:

```python
client = ParameterManagerClient(location="us-central1")
```

## Retrieve a parameter

Call `get_parameter` with the full parameter version resource name. Use
`versions/latest` when you want the latest version.

```python
value = client.get_parameter(
    "projects/my-project/locations/global/parameters/my-param/versions/latest"
)
```

The method returns the rendered parameter payload as a string.

## Authentication notes

Provide only one of `service_account_json` or `auth_token`. If neither is
provided, the client attempts to use Application Default Credentials with the
`https://www.googleapis.com/auth/cloud-platform` scope.

For broader guidance on credential handling in ADK agents, see
[Authenticating with Tools](/tools-custom/authentication/).
