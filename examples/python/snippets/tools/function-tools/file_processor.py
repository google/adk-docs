import time
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.tools import LongRunningFunctionTool
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 1. Define the generator function
def process_large_file(file_path: str) -> dict:
    """
    Simulates processing a large file, yielding progress updates.

    Args:
      file_path: Path to the file being processed.

    Returns: 
      A final status dictionary.
    """
    total_steps = 5

    # This dict will be sent in the first FunctionResponse
    yield {"status": "pending", "message": f"Starting processing for {file_path}..."}

    for i in range(total_steps):
        time.sleep(1)  # Simulate work for one step
        progress = (i + 1) / total_steps
        # Each yielded dict is sent in a subsequent FunctionResponse
        yield {
            "status": "pending",
            "progress": f"{int(progress * 100)}%",
            "estimated_completion_time": f"~{total_steps - (i + 1)} seconds remaining"
        }

    # This returned dict will be sent in the final FunctionResponse
    return {"status": "completed", "result": f"Successfully processed file: {file_path}"}

# 2. Wrap the function with LongRunningFunctionTool
long_running_tool = LongRunningFunctionTool(func=process_large_file)

# 3. Use the tool in an Agent
file_processor_agent = Agent(
    # Use a model compatible with function calling
    model="gemini-2.0-flash",
    name='file_processor_agent',
    instruction="""You are an agent that processes large files. When the user provides a file path, use the 'process_large_file' tool. Keep the user informed about the progress based on the tool's updates (which arrive as function responses). Only provide the final result when the tool indicates completion in its final function response.""",
    tools=[long_running_tool]
)


APP_NAME = "file_processor"
USER_ID = "1234"
SESSION_ID = "session1234"

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=file_processor_agent, app_name=APP_NAME, session_service=session_service)


# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

call_agent("Replace with a path to your file...")
