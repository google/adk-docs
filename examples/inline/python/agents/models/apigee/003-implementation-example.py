import asyncio
from google.adk.models.apigee_llm import CompletionsHTTPClient
from google.adk.models.llm_request import LlmRequest
from google.genai import types

async def test_client():
    # 1. Initialize the client
    client = CompletionsHTTPClient(
        base_url="https://your-apigee-proxy-url.com/v1",
        headers={"Authorization": "Bearer YOUR_API_KEY"}
    )

    # 2. Construct a minimal request
    request = LlmRequest(
        model="gpt-4o",  # Replace with your target model ID
        contents=[types.Content(role="user", parts=[types.Part.from_text(text="Hello!")])]
    )

    # 3. Execute a non-streaming generation
    async for response in client.generate_content_async(request, stream=False):
        if response.content and response.content.parts:
            print(f"Response: {response.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(test_client())