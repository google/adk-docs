# Google Cloud Platform (GCP) and Agent Platform Mentions in ADK Documentation

This file lists all pages in the ADK documentation that mention connecting with Google Cloud Platform (GCP) services, connecting models through Google Cloud / GCP, or using Agent Platform services.

---

## Build your agents

### [Build a multi-tool agent](file:///usr/local/google/home/joefernandez/dev/adk-docs/docs/tutorials/multi-tool-agent)
* **3. Set up the model** [/tutorials/multi-tool-agent/#set-up-the-model](/tutorials/multi-tool-agent/#set-up-the-model) - tabbed interface with "Gemini - Google Cloud Agent Platform" and "Gemini - Google Cloud Agent Platform with Express Mode" connection tabs


## Model Connections & Authentication

### [docs/agents/models/agent-platform.md](file:///usr/local/google/home/joefernandez/dev/adk-docs/docs/agents/models/agent-platform.md)
* **Agent Platform Setup**  
  [/agents/models/agent-platform/#agent-platform-setup](/agents/models/agent-platform/#agent-platform-setup)  
  *Walks through authenticating using Application Default Credentials (ADC) and configuring environment variables to target the Agent Platform backend.*

### [docs/agents/models/google-gemini.md](file:///usr/local/google/home/joefernandez/dev/adk-docs/docs/agents/models/google-gemini.md)
* **Gemini model authentication**  
  [/agents/models/google-gemini/#gemini-model-authentication](/agents/models/google-gemini/#gemini-model-authentication)  
  *Covers model authentication methods, comparing rapid development via Google AI Studio with enterprise-grade Google Cloud Agent Platform integration.*
* **Google Cloud Agent Platform**  
  [/agents/models/google-gemini/#google-cloud-agent-platform](/agents/models/google-gemini/#google-cloud-agent-platform)  
  *Details authenticating with Gemini on Agent Platform using User Credentials, Express Mode, or Service Accounts for production.*

---

## Integrations

### [docs/integrations/bigquery.md](file:///usr/local/google/home/joefernandez/dev/adk-docs/docs/integrations/bigquery.md)
* **Authentication**  
  [/integrations/bigquery/#authentication](/integrations/bigquery/#authentication)  
  *Explains different authentication modes (ADC, service account, access token, OAuth) to authenticate `BigQueryToolset` to a Google Cloud project.*



### [docs/integrations/agent-identity.md](file:///usr/local/google/home/joefernandez/dev/adk-docs/docs/integrations/agent-identity.md)
* **Agent Identity Auth Manager for ADK**  
  [/integrations/agent-identity/#agent-identity-auth-manager-for-adk](/integrations/agent-identity/#agent-identity-auth-manager-for-adk)  
  *Covers utilizing the Google Cloud Agent Identity service as a streamlined, Google-managed solution for managing OAuth tokens and API key lifecycles for ADK agents.*
