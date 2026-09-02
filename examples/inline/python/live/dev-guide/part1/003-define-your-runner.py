from google.adk.runners import Runner

APP_NAME = "bidi-demo"

# Define your runner
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service
)