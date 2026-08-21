# Connect to Google Cloud and Agent Platform

This guide explains how to connect and authenticate your ADK agents with Google Cloud Platform (GCP) services, models running on Google Cloud Agent Platform, and Agent Platform services.

## Setup Google Cloud Agent Platform

Before attempting to connect an agent with Google Cloud or Agent Platform services, make sure you have completed the following prerequisites:

- Google Cloud Project with the **Agent Platform API** (`aiplatform.googleapis.com`) enabled.
- Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install) tool.

## Google Cloud authentication options

You have a few options for authentication when connecting your ADK agent to Google Cloud, as described in the table below.

| Method                                             | Best Used For                   | Authentication Mechanism                           | Environment                                                      |
| -------------------------------------------------- | ------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------- |
| [**User Credentials**](#user-credentials)          | Local development and testing   | Application Default Credentials via `gcloud`       | Local workstation                                                |
| [**Service Account**](#service-account)            | Production deployment and CI/CD | Google IAM Service Account Key / Workload Identity | Google Cloud (Agent Runtime, Cloud Run, GKE) or external servers |
| [**Express Mode**](#express-mode)                  | Rapid prototyping and testing   | API Key                                            | Local or cloud environments                                      |
| [**Agent Identity**](/integrations/agent-identity) | Production deployment and CI/CD | Google IAM Service Account Key / Workload Identity | Google Cloud (Agent Runtime, Cloud Run, GKE)                     |

Warning: Protect your credentials

User credentials, service account credentials, and API keys are highly sensitive. Never commit credential files or keys directly to your codebase. Whenever possible use secure secret managers such as [Google Cloud Agent Identity](/integrations/agent-identity/), [Google Cloud Secret Manager](https://cloud.google.com/security/products/secret-manager) or other similar products.

### User credentials for local development

Connect to Google Cloud with user credentials authentication method working with local development environments.

1. Authenticate your local workstation using Application Default Credentials (ADC) *before* running your ADK agent application:

   ```bash
   gcloud auth application-default login
   ```

1. Set your environment variables to enable Agent Platform and specify your project details:

   ```console
   # Add to ADK code project but NOT source control
   GOOGLE_GENAI_USE_ENTERPRISE=TRUE
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=cloud-location   # example: us-central1
   ```

   ```bash
   export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_CLOUD_LOCATION="cloud-location"   # example: us-central1
   ```

`GOOGLE_GENAI_USE_ENTERPRISE` was previously `GOOGLE_GENAI_USE_VERTEXAI`

These variable names are equivalent and do the same thing. If you set `GOOGLE_GENAI_USE_ENTERPRISE` and your agent does not connect to Agent Platform, you're on an older ADK version. Use `GOOGLE_GENAI_USE_VERTEXAI` instead, or update to a newer version of ADK.

### Service account for production

When deploying to secure hosted environments, use a service account for connection authentication:

1. Create a [Service Account](https://docs.cloud.google.com/iam/docs/service-account-overview) and grant it the `Agent Platform User` role.
1. Provide the credentials to your agent application according to your deployment strategy:
   - **Deployed on Google Cloud (Agent Runtime, Cloud Run, GKE):** The environment automatically provides the credentials. No key file configuration is necessary.

   - **Running externally:** Generate a [service account key file](https://cloud.google.com/iam/docs/keys-create-delete#console) (`.json`) and configure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:

     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
     ```

Workload Identity option

Instead of the key file, you can also authenticate the service account using [Workload Identity](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/workload-identity).

### Agent Platform express mode for testing

Express Mode offers a simplified, API-key-based setup for prototyping without full gcloud authentication.

1. Sign up for [express mode](https://console.cloud.google.com/expressmode) to get an API key.

1. Set the following environment variables:

   ```console
   # Add to ADK code project but NOT source control
   GOOGLE_GENAI_USE_ENTERPRISE=TRUE
   GOOGLE_GENAI_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
   ```

   ```bash
   export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
   export GOOGLE_GENAI_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
   ```

## Google Cloud hosted models

Google Cloud Agent Platform hosts a wide array of AI models you can connect to your ADK agents, including Gemini models, third-party AI models, open weight models, and models custom-tuned for your organization. Once you have connected your ADK agent to Google Cloud and Agent Platform, you have access to AI models to fit your application requirements. Check out these resources to explore and find the model that's right for your project:

- Get more information about using [Gemini models](/agents/models/google-gemini/) with ADK agents.
- Explore third party and custom model options in [Agent Platform hosted models](/agents/models/agent-platform/) for use with ADK agents.
- Find available models and model IDs from Google Cloud in the [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models) documentation.

## Additional Google Cloud services connections

Many Google Cloud services provide ADK integrations with authentication helpers for accessing GCP APIs or resources with an ADK agent. For more information, see the following pages:

- [Google Cloud Application Integration](/integrations/application-integration/)
- [BigQuery Toolset](/integrations/bigquery/)
- [BigQuery Agent Analytics](/integrations/bigquery-agent-analytics/)
- [Data Agent](/integrations/data-agent/)
