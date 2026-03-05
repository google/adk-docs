Vertex AI also offers [Vertex AI Express Mode](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview), a simplified, API-key-based setup designed for rapid prototyping. This allows new users to quickly access Gemini models for a 90-day period without the immediate need for full Google Cloud project configuration.

1.  **Sign up for Express Mode** to get your API key.
2.  **Set environment variables:** Create a `.env` file (Python) or `.properties` (Java) in your project's root directory and add the following lines. ADK will automatically load this file.
    ```shell
    GOOGLE_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```