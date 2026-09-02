# Read data set by a previous agent
previous_result = ctx.session.state.get("some_key")

# Make a decision based on state
if previous_result == "some_value":
    # ... call a specific sub-agent ...
else:
    # ... call another sub-agent ...

# Store a result for a later step (often done via a sub-agent's output_key)
# ctx.session.state["my_custom_result"] = "calculated_value"