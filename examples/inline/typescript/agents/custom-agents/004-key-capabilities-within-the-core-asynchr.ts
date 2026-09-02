// Read data set by a previous agent
const previousResult = ctx.session.state['some_key'];

// Make a decision based on state
if (previousResult === 'some_value') {
  // ... call a specific sub-agent ...
} else {
  // ... call another sub-agent ...
}

// Store a result for a later step (often done via a sub-agent's outputKey)
// ctx.session.state['my_custom_result'] = 'calculated_value';