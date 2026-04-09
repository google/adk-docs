# Google Cloud Secret Manager Integration

The ADK provides a built-in client for Google Cloud Secret Manager to simplify
retrieving secrets, such as API keys or other credentials, in your production
deployments.

## SecretManagerClient

The `SecretManagerClient` (`google.adk.integrations.secret_manager.secret_client`)
provides a simplified interface for retrieving secrets from Secret Manager.

### Authentication

You can instantiate the `SecretManagerClient` in a few ways:

*   **Application Default Credentials (ADC):** If you are running on Google
    Cloud (e.g., Cloud Run, GKE, Compute Engine) and the environment is
    configured with a service account, the client will automatically use ADC.

    ```python
    from google.adk.integrations.secret_manager import secret_client

    secret_manager = secret_client.SecretManagerClient()
    ```

*   **Service Account JSON:** You can provide the contents of a service account
    JSON keyfile as a string.

    ```python
    from google.adk.integrations.secret_manager import secret_client
    import json

    # Assume service_account_dict contains the service account JSON data
    service_account_json = json.dumps(service_account_dict)

    secret_manager = secret_client.SecretManagerClient(
        service_account_json=service_account_json
    )
    ```

*   **Authentication Token:** You can use an existing Google Cloud
    authorization token.

    ```python
    from google.adk.integrations.secret_manager import secret_client

    auth_token = "YOUR_AUTH_TOKEN"  # Replace with your actual token
    secret_manager = secret_client.SecretManagerClient(auth_token=auth_token)
    ```

### Retrieving secrets

To retrieve a secret, use the `get_secret()` method, passing the full
resource name of the secret version.

```python
from google.adk.integrations.secret_manager import secret_client

# Instantiate the client (e.g., using ADC)
secret_manager = secret_client.SecretManagerClient()

# Get the latest version of a secret
resource_name = "projects/my-project/secrets/my-secret/versions/latest"
secret_value = secret_manager.get_secret(resource_name)

# Now you can use the secret_value with other ADK tools
print(f"Retrieved secret: {secret_value}")
```

Replace `my-project` and `my-secret` with your Google Cloud project ID and
the name of your secret.
