# How the framework provides context
from google.adk import Runner

# 1. You initialize a Runner with your agent and services
runner = Runner(
    app_name="my_app",
    agent=my_root_agent,
    session_service=my_session_service,
    artifact_service=my_artifact_service,
)

# 2. You call run_async with the user input
# Note: run_async is an asynchronous generator yielding Events.
# The framework internally creates an InvocationContext and passes it
# implicitly to your agent code, callbacks, and tools.
async for event in runner.run_async(
    user_id="user123",
    session_id="session456",
    new_message=user_message
):
    print(event.stringify_content())

# As a developer, you work with the context objects provided in method arguments.