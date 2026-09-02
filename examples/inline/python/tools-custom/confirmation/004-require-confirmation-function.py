async def confirmation_threshold(
    amount: int, tool_context: ToolContext
) -> bool:
  """Returns true if the amount is greater than 1000."""
  return amount > 1000

root_agent = Agent(
    # ...
    tools = [
        # Pass the threshold function to dynamically require confirmation
        FunctionTool(reimburse, require_confirmation=confirmation_threshold),
    ],
    # ...
)