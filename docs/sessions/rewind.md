# Rewind sessions for agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.17.0</span>
</div>

The ADK session Rewind feature allows you to revert a session to a previous
request state, enabling you to undo mistakes, explore alternative paths, or
restart a process from a known good point. This document provides an overview of
the feature, how to use it, and its limitations.

## Rewind a session

When you rewind a session, you specify a user request, or ***invocation***, that
you want to undo, and the system undoes that request and the requests after it.
So if you have three requests (A, B, C) and you want to return to the state at
request A, you specify B, which undoes the changes from requests B and C. You
rewind a session by using the rewind method on a ***Runner*** instance,
specifying the user, session, and invocation id, as shown in the following code
snippet:

```python
# Create runner
runner = InMemoryRunner(
    agent=agent.root_agent,
    app_name=APP_NAME,
)

# Create a session
session = await runner.session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID
)
# call agent with wrapper function "call_agent_async()"
await call_agent_async(
    runner, USER_ID, session.id, "set state color to red"
)
# ... more agent calls ...
events_list = await call_agent_async(
    runner, USER_ID, session.id, "update state color to blue"
)

# get invocation id
rewind_invocation_id=events_list[1].invocation_id

# rewind invocations (state color: red)
await runner.rewind_async(
    user_id=USER_ID,
    session_id=session.id,
    rewind_before_invocation_id=rewind_invocation_id,
)
```

When you call the ***rewind*** method, all ADK managed session-level resources
are restored to the state they were in *before* the request you specified with
the ***invocation id***. However, global resources, such as app-level or
user-level state and artifacts, are not restored. For a complete example of an
agent session rewind, see the
[rewind_session](https://github.com/google/adk-python/tree/main/contributing/samples/rewind_session)
sample code. For more information on the limitations of the Rewind feature,
see [Limitations](#limitations).

## How it works

The Rewind feature creates a special ***rewind*** request that restores the
session's state and artifacts to their condition *before* the rewind point
specified by an invocation id. This approach means that all requests, including
rewound requests, are preserved in the log for later debugging, analysis, or
auditing. After the rewind, the system ignores the rewound requests when
it prepares the next requests for the AI model. This behavior means the AI model
used by the agent effectively forgets any interactions from the rewind point up
to the next request.

## Limitations {#limitations}

The Rewind feature has some limitations that you should be aware of when using
it with your agent workflow:

*   **Global agent resources:** App-level and user-level state and artifacts are
    *not* restored by the rewind feature. Only session-level state and artifacts
    are restored.
*   **External dependencies:** The rewind feature does not manage external
    dependencies. If a tool in your agent interacts with external systems,
    it is your responsibility to handle the restoration of those systems to
    their prior state.
*   **Atomicity:** State updates, artifact updates, and event persistence are
    not performed in a single atomic transaction. Therefore, you should avoid
    rewinding active sessions or concurrently manipulating session artifacts
    during a rewind to prevent inconsistencies.
