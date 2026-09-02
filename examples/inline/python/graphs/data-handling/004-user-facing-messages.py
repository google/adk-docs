async def user_message(node_input: str):
  """Tell user research process is starting."""
  yield Event(message="Beginning research process...")