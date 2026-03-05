Using the Gemini API (Google AI Studio) is the **simplest** and **fastest** method to use Gemini models and is recommended for getting started quickly by using API Keys for authentication.

1.  **Get an API key:** Obtain your key from [Google AI Studio](https://aistudio.google.com/apikey).
2.  **Set environment variables:** Create a `.env` file (Python) or `.properties` (Java) in your project's root directory and add the following lines. ADK will automatically load this file.
        ```shell
        GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        ```