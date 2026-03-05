The standard way to authenticate to Vertex AI is using [Application Default Credentials (ADC)](https://docs.cloud.google.com/docs/authentication/set-up-adc-local-dev-environment). Ensure you have completed the project [prerequisites](/adk-docs/agents/models/google-gemini/#setup-cloud-project) and follow the steps below to set it up in your local development environment.

1.  **Install the gcloud CLI:** Follow the official [installation instructions](https://cloud.google.com/sdk/docs/install).
2.  **Create local authentication credentials:** This gcloud command opens a browser to authenticate your user account for local development.
    ```bash
    gcloud auth application-default login
    ```
    
3.  **Set environment variables:** Create a `.env` file (Python) or `.properties` (Java) in your project's root directory and add the following lines. ADK will automatically load this file.
    ```shell
    GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    GOOGLE_GENAI_USE_VERTEXAI=TRUE # Explicitly tell the library to use Vertex AI
    ```

See [ADC documentation](https://docs.cloud.google.com/docs/authentication/application-default-credentials) to get more details and understand how ADC works.