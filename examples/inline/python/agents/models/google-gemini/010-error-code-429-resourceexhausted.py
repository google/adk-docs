from google.genai import types

# ...

agent = Agent(
    model=Gemini(
    retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
    )
)