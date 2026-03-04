# Google Gemini models for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

There are two primary APIs for accessing the Gemini model family: [Vertex AI API](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/overview) (available via Google Cloud Console) and the [Gemini API](https://ai.google.dev/gemini-api/docs) (available via Google AI Studio). While both provide access to the same state-of-the-art models, the choice between them depends on your specific security requirements, development phase, and deployment environment.

## ADK Integration
The ADK does not utilize a proprietary API; instead, it acts as a robust abstraction layer that supports accessing Gemini models through both Vertex AI and the Gemini API. By providing a unified interface, the ADK enables you to easily integrate advanced Gemini features, including:

[Code Execution](/adk-docs/tools/gemini-api/code-execution/): Run generated code in a secure environment.

[Google Search](/adk-docs/tools/gemini-api/google-search/): Ground model responses with real-time web results.

[Context Caching](/adk-docs/context/caching/): Optimize performance and cost for long-context prompts.

[Computer use](/adk-docs/tools/gemini-api/computer-use/): Enable models to interact with digital interfaces.

[Interactions API](/adk-docs/tools/gemini-api/interactions-api/): Manage complex conversational flows.


## Choosing Vertex API or Gemini API for you agent {#choosing-api}
### Vertex AI

Vertex AI is a Google Cloud-managed machine learning platform that provides a unified environment for the entire AI lifecycle. It allows developers, data scientists, and ML engineers to access the latest Gemini models while seamlessly integrating with other Vertex AI services and the broader Google Cloud ecosystem.

#### When to use Vertex AI:

* **Existing Google Cloud Infrastructure:** Ideal for teams already leveraging Google Cloud services. Vertex AI uses the same IAM authentication as other GCP services, providing a seamless experience if you are already using the Google Cloud Console.

* **Enterprise Security:** For teams that require implementing industry-leading best practices, including VPC Service Controls, Customer-Managed Encryption Keys (CMEK), and Workload Identity Federation to eliminate long-lived secrets.

* **Production Reliability:** For applications that require financially-backed SLAs (99.9%+), 24/7 technical support, and Provisioned Throughput (PT) to eliminate 429 rate-limit errors.

* **GCP Ecosystem Integration:** Best for use cases requiring deep, native interaction with services like Agent Engine, BigQuery, Cloud Storage, and GKE.

* **Compliance & Governance:** For workloads that must adhere to regulatory standards such as HIPAA, SOC 2, ISO, or FedRAMP, or those requiring strict data residency in specific regions.

* **Advanced MLOps:** Optimized for teams needing managed tools for model monitoring, evaluation, and fine-tuning, or those deploying third-party and open-source models alongside Gemini.

### Gemini API

The Gemini API, accessible through Google AI Studio, is an interface dedicated to generative AI models, designed for rapid development and application building. It allows developers to quickly prototype and deploy applications using Gemini models with minimal setup.

It is the ideal choice for developers, startups, and businesses that prioritize speed and agility, offering a straightforward path to production without the initial need for complex cloud infrastructure or enterprise-level governance.

#### When to use Gemini API

* **Speed of Implementation:** Start building in minutes using a simple API key, avoiding the overhead of complex project configurations.

* **Agile Prototyping:** Optimized for a "build, share, and deploy" workflow, perfect for iterative testing of prompts and model capabilities.

* **Low-Friction Scaling:** Features a generous free tier for experimentation and a clear Pay-As-You-Go model for production.

* **Standalone Applications:** Best for projects that do not require deep integration with the broader Google Cloud enterprise security stack.


## Gemini model authentication

A primary difference between Vertex AI and the Gemini API is the authentication mechanism. Vertex AI leverages standard Google Cloud authentication methods—including Application Default Credentials (ADC) for local development—while the Gemini API uses API Keys directly. See 
[Choosing API](/adk-docs/agents/models/google-gemini/#choosing-api) for more guidance to select Vertex AI or Gemini API.

This section explains how to authenticate for local development using both platforms.

### Vertex AI

To use Gemini models via Vertex AI for local development, use Application Default Credentials (ADC). This is the standard and recommended method for authenticating with Google Cloud services, as it avoids the security risks associated with long-lived API keys.

#### Google Cloud Prerequisites {#setup-cloud-project}

1. **Sign into Google Cloud**:
    * If you're an **existing user** of Google Cloud:
        * Sign in via
          [https://console.cloud.google.com](https://console.cloud.google.com)
        * If you previously used a Free Trial that has expired, you may need to
          upgrade to a
          [Paid billing account](https://docs.cloud.google.com/free/docs/free-cloud-features#how-to-upgrade).
    * If you are a **new user** of Google Cloud:
        * You can sign up for the
          [Free Trial program](https://docs.cloud.google.com/free/docs/free-cloud-features).
          The Free Trial gets you a $300 Welcome credit to spend over 90 days on various
          [Google Cloud products](https://docs.cloud.google.com/free/docs/free-cloud-features#during-free-trial)
          and you won't be billed. During the Free Trial, you also get access to the
          [Google Cloud Free Tier](https://docs.cloud.google.com/free/docs/free-cloud-features#free-tier),
          which gives you free usage of select products up to specified monthly
          limits, and to product-specific free trials.

2. **Create a Google Cloud project**
    * You can use existing project or create a new one on the [Create Project](https://console.cloud.google.com/projectcreate) page. Find more details in [GCP documentation](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects).

3. **Get your Google Cloud Project ID**
    * Make sure to note the Project ID (inmutable alphanumeric with hyphens),
      _not_ the project number (numeric) or project name (mutable human-readable).

    <img src="/adk-docs/assets/project-id.png" alt="Google Cloud Project ID">

4. **Enable Vertex AI in your project**
    * You need to [enable the Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com). Click on the "Enable" button to enable the API. Once enabled, it
    should say "API Enabled".

5. **Grant IAM permissions**
    * If you don't have Owner role or other wider permissions, make sure to grant the following IAM permissions to your Google account so it has permissions to call Gemini models:
        * `aiplatform.googleapis.com/user`
    * You can grant these permissions in the console following these steps:
        1. Go to the [IAM & Admin](https://console.cloud.google.com/iam-admin/iam) page.
        2. Click on the "Add" button.
        3. In the "New principals" field, enter your email address.
        4. In the "Select a role" field, select "Vertex AI User".
    * Or by running the following command (See gcloud [installation instructions](https://cloud.google.com/sdk/docs/install)):
        ```bash
        gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member="user:YOUR_EMAIL_ADDRESS" --role="roles/aiplatform.user"
        ```
        Find more details and best practices in [GCP IAM documentation](https://docs.cloud.google.com/iam/docs/using-iam-securely)


#### Authentication with Vertex AI {#adc-authentication}

1.  **Install the gcloud CLI:** Follow the official [installation instructions](https://cloud.google.com/sdk/docs/install).
2.  **Log in using ADC:** This command opens a browser to authenticate your user account for local development.
    ```bash
    gcloud auth application-default login
    ```
    
3.  **Set environment variables:**
    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    ```

    Explicitly tell the library to use Vertex AI:
    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

4. **Models:** Find available model IDs in the
  [Vertex AI documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models).

#### Authentication with Vertex AI in **Express Mode**

Vertex AI also offers [Vertex AI Express Mode](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview), a simplified, API-key-based setup designed for rapid prototyping. This allows new users to quickly access Gemini models for a 90-day period without the immediate need for full Google Cloud project configuration.


1.  **Sign up for Express Mode** to get your API key.
2.  **Set environment variables:**
    ```shell
    export GOOGLE_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### Google AI Studio

This is the simplest method and is recommended for getting started quickly.

*   **Authentication Method:** API Key
*   **Setup:**
    1.  **Get an API key:** Obtain your key from [Google AI Studio](https://aistudio.google.com/apikey).
    2.  **Set environment variables:** Create a `.env` file (Python) or `.properties` (Java) in your project's root directory and add the following lines. ADK will automatically load this file.

        ```shell
        export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        ```

        (or)

        Pass these variables during the model initialization via the `Client` (see example below).

* **Models:** Find all available models on the
  [Google AI for Developers site](https://ai.google.dev/gemini-api/docs/models).


!!! warning "Secure Your Credentials"

    Service account credentials or API keys are powerful credentials. Never
    expose them publicly. Use a secret manager such as [Google Cloud Secret
    Manager](https://cloud.google.com/security/products/secret-manager) to store
    and access them securely in production.

!!! note "Gemini model versions"

    Always check the official Gemini documentation for the latest model names,
    including specific preview versions if needed. Preview models might have
    different availability or quota limitations.
    

## Using Gemini in your agents

Once you have authenticated and set the required environment variables (GOOGLE_GENAI_USE_VERTEXAI and your credentials), using Gemini models is seamless. The ADK uses these variables to automatically route requests to either Vertex AI or Google AI Studio. The following code examples show a basic implementation for using Gemini models in your agents:

=== "Python"

    ```python
    from google.adk.agents import LlmAgent

    # --- Example using a stable Gemini Flash model ---
    agent_gemini_flash = LlmAgent(
        # Use the latest stable Flash model identifier
        model="gemini-2.5-flash",
        name="gemini_flash_agent",
        instruction="You are a fast and helpful Gemini assistant.",
        # ... other agent parameters
    )
    ```

=== "TypeScript"

    ```typescript
    import {LlmAgent} from '@google/adk';

    // --- Example #2: using a powerful Gemini Pro model with API Key in model ---
    export const rootAgent = new LlmAgent({
      name: 'hello_time_agent',
      model: 'gemini-2.5-flash',
      description: 'Gemini flash agent',
      instruction: `You are a fast and helpful Gemini assistant.`,
    });
    ```

=== "Go"

    ```go
    import (
    	"google.golang.org/adk/agent/llmagent"
    	"google.golang.org/adk/model/gemini"
    	"google.golang.org/genai"
    )

    --8<-- "examples/go/snippets/agents/models/models.go:gemini-example"
    ```

=== "Java"

    ```java
    // --- Example #1: using a stable Gemini Flash model with ENV variables---
    LlmAgent agentGeminiFlash =
        LlmAgent.builder()
            // Use the latest stable Flash model identifier
            .model("gemini-2.5-flash") // Set ENV variables to use this model
            .name("gemini_flash_agent")
            .instruction("You are a fast and helpful Gemini assistant.")
            // ... other agent parameters
            .build();
    ```

