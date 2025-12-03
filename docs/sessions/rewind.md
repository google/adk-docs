# Rewind sessions for agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.17.0</span>
</div>

The ADK session Rewind feature allows you to revert a session to a previous
state, enabling you to undo mistakes, explore alternative paths, or restart a
process from a known good point. This document provides an overview of the
feature, how to use it, and its limitations.

## Rewind a session

You can rewind a session to a prior invocation by using the ***rewind*** method
on a ***Runner*** instance, specifying the user, session, and invocation, as
shown in the following code example:

```python
# Create runner
runner = InMemoryRunner(
    agent=agent.root_agent,
    app_name=APP_NAME,
)

# Create a session
session = await runner.session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID

# call agent with wrapper function call_agent_async()
await call_agent_async(
    runner, USER_ID, session.id, "set state color to red"
)
# ... more agent calls ...
events_list = await call_agent_async(
    runner, USER_ID, session.id, "update state color to blue"
)

# get first invocation id
rewind_invocation_id=events_list[0].invocation_id

# rewind to first invocation (state color: red)
await runner.rewind_async(
    user_id=USER_ID,
    session_id=session.id,
    rewind_before_invocation_id=rewind_invocation_id,
)
```

When you call the ***rewind*** method, all ADK managed session-level resources
are restored to the state they were in at the rewind point specified by the
***invocation id***. However, global resources, such as app-level or user-level state
and artifacts, are not restored. For a complete example of an agent session rewind, see the
[rewind_session](https://github.com/google/adk-python/tree/main/contributing/samples/rewind_session)
sample code. For more information on the limitations of the Rewind feature,
see [Limitations](#limitations).

## How It Works

The Rewind feature creates a special *rewind* event that restores the session's
state and artifacts to their condition at the rewind point specified by an
invocation id. This approach means that all events, including rewound events,
are preserved in the event log for later debugging, analysis, or auditing. After
the rewind, the system ignores events that came after rewind point when it
prepares the next request for the AI model. This behavior means AI model used by
the agent effectively forgets any interactions between the rewind point and the
next request.

## Limitations {#limitations}

The Rewind feature has some limitations that you should be aware of when using
it with your agent workflow:

*   **Global agent resources:** App-level and user-level state and artifacts are
    *not* restored by the rewind feature. Only session-level state and artifacts
    are restored.
*   **External dependencies:** The rewind feature does not manage external
    dependencies. If a tool in your agent interacts with an external system,
    it's your responsibility to handle the state restoration of that system to
    its prior state.
*   **Atomicity:** State updates, artifact updates, and event persistence are
    not performed in a single atomic transaction. Therefore, you should avoid
    rewinding active sessions or concurrently manipulating session artifacts
    during a rewind to prevent inconsistencies.
