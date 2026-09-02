root_agent = Agent(
    # ...
    tools = [
        # Set require_confirmation to True to require user confirmation
        # for the tool call.
        FunctionTool(reimburse, require_confirmation=True),
    ],
    # ...
)

# This implementation method requires minimal code, but is limited to simple
# approvals from the user or confirming system. For a complete example of this
# approach, see the following code sample for a more detailed example:
# https://github.com/google/adk-python/blob/main/contributing/samples/human_tool_confirmation/agent.py