# AI Models for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">Typescript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

The Agent Development Kit (ADK) is designed for flexibility, allowing you to
integrate various Large Language Models (LLMs) into your agents. While the setup
for Google Gemini models is covered in the
[Setup Foundation Models](../../get-started/installation.md) guide, this section
details how to leverage Gemini effectively and integrate other popular models,
including those hosted externally or running locally.

ADK primarily uses two mechanisms for model integration:

1. **Direct String / Registry:** For models tightly integrated with Google Cloud
   (like Gemini models accessed via Google AI Studio or Vertex AI) or models
   hosted on Vertex AI endpoints. You typically provide the model name or
   endpoint resource string directly to the `LlmAgent`. ADK's internal registry
   resolves this string to the appropriate backend client, often utilizing the
   `google-genai` library.
2. **Wrapper Classes:** For broader compatibility, especially with models
   outside the Google ecosystem or those requiring specific client
   configurations (like models accessed via Apigee or LiteLLM). You instantiate a specific
   wrapper class (e.g., `ApigeeLlm` or `LiteLlm`) and pass this object as the `model` parameter
   to your `LlmAgent`.

The following pages guide you through using these methods based on your needs.
