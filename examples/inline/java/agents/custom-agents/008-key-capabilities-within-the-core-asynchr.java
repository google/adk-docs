// Read data set by a previous agent
Object previousResult = ctx.session().state().get("some_key");

// Make a decision based on state
if ("some_value".equals(previousResult)) {
    // ... logic to include a specific sub-agent's Flowable ...
} else {
    // ... logic to include another sub-agent's Flowable ...
}

// Store a result for a later step (often done via a sub-agent's output_key)
// ctx.session().state().put("my_custom_result", "calculated_value");