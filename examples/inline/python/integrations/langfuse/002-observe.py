from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

def say_hello():
    return {"greeting": "Hello Langfuse 👋"}

agent = Agent(
    name="hello_agent",
    model="gemini-3.5-flash",
    instruction="Always greet using the say_hello tool.",
    tools=[say_hello],
)

APP_NAME = "hello_app"
USER_ID = "demo-user"
SESSION_ID = "demo-session"

session_service = InMemorySessionService()
# create_session is async → await it in notebooks
await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

user_msg = types.Content(role="user", parts=[types.Part(text="hi")])
for event in runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=user_msg):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(event.content.parts[0].text)
        elif event.error_message:
            print(f"Agent error: {event.error_message}")