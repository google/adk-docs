---
catalog_title: Secret Manager
catalog_description: Securely store and manage sensitive data like API keys and passwords for ADK agents.
catalog_icon: /integrations/assets/secret-manager.png
---
# Secret Manager

Google Cloud Secret Manager allows you to store, manage, and access secrets as binary blobs or text strings.

## Use cases
- **Secure Key Storage**: Store API keys safely away from your agent code.
- **Credential Rotation**: Update passwords without changing your application setup.

## Prerequisites
- A Google Cloud account with Secret Manager enabled.
- An active API key or service account credential.

## Installation
```bash
pip install google-cloud-secret-manager
from google.adk.agents import Agent
# Your example code goes here
