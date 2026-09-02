from google.adk.agents import LlmAgent
from google.adk.models.apigee_llm import ApigeeLlm

# Instantiate the ApigeeLlm wrapper
model = ApigeeLlm(
    # Specify the Apigee route to your model. For more info, check out the ApigeeLlm documentation (https://github.com/google/adk-python/tree/main/contributing/samples/models/hello_world_apigeellm).
    model="apigee/gemini-flash-latest",
    # The proxy URL of your deployed Apigee proxy including the base path
    proxy_url=f"https://{APIGEE_PROXY_URL}",
    # Pass necessary authentication/authorization headers (like an API key)
    custom_headers={"foo": "bar"}
)

# Pass the configured model wrapper to your LlmAgent
agent = LlmAgent(
    model=model,
    name="my_governed_agent",
    instruction="You are a helpful assistant powered by Gemini and governed by Apigee.",
    # ... other agent parameters
)