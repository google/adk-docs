from google.adk.auth import AuthConfig
from google.adk.events import Event
import asyncio

# --- Helper Functions ---
async def get_user_input(prompt: str) -> str:
  """
  Asynchronously prompts the user for input in the console.

  Uses asyncio's event loop and run_in_executor to avoid blocking the main
  asynchronous execution thread while waiting for synchronous `input()`.

  Args:
    prompt: The message to display to the user.

  Returns:
    The string entered by the user.
  """
  loop = asyncio.get_event_loop()
  # Run the blocking `input()` function in a separate thread managed by the executor.
  return await loop.run_in_executor(None, input, prompt)


def is_pending_auth_event(event: Event) -> bool:
  """
  Checks if an ADK Event represents a request for user authentication credentials.

  The ADK framework emits a specific function call ('adk_request_credential')
  when a tool requires authentication that hasn't been previously satisfied.

  Args:
    event: The ADK Event object to inspect.

  Returns:
    True if the event is an 'adk_request_credential' function call, False otherwise.
  """
  # Safely checks nested attributes to avoid errors if event structure is incomplete.
  return (
      event.content
      and event.content.parts
      and event.content.parts[0] # Assuming the function call is in the first part
      and event.content.parts[0].function_call
      # The specific function name indicating an auth request from the ADK framework.
      and event.content.parts[0].function_call.name == 'adk_request_credential'
  )


def get_function_call_id(event: Event) -> str:
  """
  Extracts the unique ID of the function call from an ADK Event.

  This ID is crucial for correlating a function *response* back to the specific
  function *call* that the agent initiated to request for auth credentials.

  Args:
    event: The ADK Event object containing the function call.

  Returns:
    The unique identifier string of the function call.

  Raises:
    ValueError: If the function call ID cannot be found in the event structure.
                (Corrected typo from `contents` to `content` below)
  """
  # Navigate through the event structure to find the function call ID.
  if (
      event
      and event.content
      and event.content.parts
      and event.content.parts[0] # Use content, not contents
      and event.content.parts[0].function_call
      and event.content.parts[0].function_call.id
  ):
    return event.content.parts[0].function_call.id
  # If the ID is missing, raise an error indicating an unexpected event format.
  raise ValueError(f'Cannot get function call id from event {event}')


def get_function_call_auth_config(event: Event) -> AuthConfig:
  """
  Extracts the authentication configuration details from an 'adk_request_credential' event.

  Client should use this AuthConfig to necessary authentication details (like OAuth codes and state)
  and sent it back to the ADK to continue OAuth token exchanging.

  Args:
    event: The ADK Event object containing the 'adk_request_credential' call.

  Returns:
    An AuthConfig object populated with details from the function call arguments.

  Raises:
    ValueError: If the 'auth_config' argument cannot be found in the event.
                (Corrected typo from `contents` to `content` below)
  """
  if (
      event
      and event.content
      and event.content.parts
      and event.content.parts[0] # Use content, not contents
      and event.content.parts[0].function_call
      and event.content.parts[0].function_call.args
      and event.content.parts[0].function_call.args.get('auth_config')
  ):
    # Reconstruct the AuthConfig object using the dictionary provided in the arguments.
    # The ** operator unpacks the dictionary into keyword arguments for the constructor.
    return AuthConfig(
          **event.content.parts[0].function_call.args.get('auth_config')
      )
  raise ValueError(f'Cannot get auth config from event {event}')