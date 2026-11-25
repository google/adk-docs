# Test agents without a model API

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.18.0</span>
</div>

Most agent regressions are not model-quality regressions. A tool starts
returning a different shape, a callback stops firing, a state key is written
under a new name, an artifact lands under the wrong filename, or a run that used
to pause for input now goes straight through. None of those need a real model to
catch, and a test that calls Gemini to find them is slow, costs money, and can
fail for reasons that have nothing to do with your change.

This page shows how to test an agent entirely in process, with no API key and no
network call: a *scripted model* returns the responses your test needs, and
`InMemoryRunner` hands the turn's events back for plain Python assertions.

Every block below is a section of
[`examples/python/snippets/testing/test_agents.py`](https://github.com/google/adk-docs/blob/main/examples/python/snippets/testing/test_agents.py),
which runs as written — eight tests, nothing on disk, no fixtures to write:

```text
pytest examples/python/snippets/testing/test_agents.py
```

!!! note "Related pages"
    [Evaluation](/evaluate/) scores real model answers against criteria — use it
    when the question is *how good are the answers*, not *did my agent wire this
    turn correctly*. [API Server](/runtime/api-server/) covers the interactive
    `adk web` loop, and [Tool confirmation](/tools-custom/confirmation/) covers
    the human side of a paused run.

## Script a model instead of calling one

A model is just a `BaseLlm` subclass. This one pops one canned response per turn,
so a two-turn test needs exactly two responses, and it keeps the requests it
received so a test can assert on what the model was actually sent.

```python
--8<-- "examples/python/snippets/testing/test_agents.py:scripted_model"
```

Two helpers keep the tests readable: `call()` scripts a function call and `say()`
scripts a model turn that only speaks. Because the script is a list that gets
consumed, a model call you did not script exhausts it and fails the test instead
of passing silently.

## Run a turn and assert on it

`InMemoryRunner` builds in-memory session, artifact and memory services, so a
test needs nothing on disk. Its `run_debug()` helper sends a message and returns
the turn's `list[Event]`; with `quiet=True` it prints nothing.

```python
--8<-- "examples/python/snippets/testing/test_agents.py:tool_calls"
```

`run_debug()` reuses the user ID `debug_user_id` and the session ID
`debug_session_id` and keeps that session between calls, so two `run_debug()`
calls in one test form one conversation — which is how you test a follow-up turn.
Each `InMemoryRunner` owns its own services, so one runner per test keeps tests
independent.

## Assert on session state

State written through `tool_context.state` is visible in the session as soon as
the turn returns. Read it back through the runner's session service to assert
what your tool actually persisted:

```python
--8<-- "examples/python/snippets/testing/test_agents.py:state"
```

For the finer-grained question — *which turn* wrote a key — read
`event.actions.state_delta` on each event rather than the final session state.

### Seed state before the first turn

A test that starts from a non-empty session writes the starting state through the
runner's session service. `run_debug()` reuses `debug_user_id` and
`debug_session_id`, so seeding those is enough:

```python
--8<-- "examples/python/snippets/testing/test_agents.py:seed_state"
```

## Assert on what the model was sent

The tool result your agent hands back is part of its contract with the model.
Because the scripted model keeps its requests, you can assert on that too:

```python
--8<-- "examples/python/snippets/testing/test_agents.py:model_request"
```

This catches the failure mode a tool-level unit test cannot see: a tool that
returns the right data in the wrong shape, so the model is asked to work with
something you never intended to send. The same object holds the system
instruction after `{state}` placeholders are filled in, so a test can pin that
too.

## Assert on error paths

A tool that raises propagates out of `run_debug()`, so `pytest.raises` is enough
— no need to inspect an error payload to confirm the run failed:

```python
--8<-- "examples/python/snippets/testing/test_agents.py:tool_errors"
```

## Assert on artifacts

`InMemoryRunner` also comes with an in-memory artifact service, so a test can
assert on what a tool saved without touching a bucket or a directory:

```python
--8<-- "examples/python/snippets/testing/test_agents.py:artifacts"
```

Note that `save_artifact()` is a coroutine: a tool that saves must be `async def`
and `await` it. A sync tool that calls it without awaiting returns a coroutine and
stores nothing, which is exactly the kind of bug this assertion catches.

## Assert on a run that pauses

A tool wrapped in `FunctionTool(..., require_confirmation=True)` stops before it
executes. The turn records the pending confirmation on the event and answers the
call with an error instead of running the tool, and both are assertable:

```python
--8<-- "examples/python/snippets/testing/test_agents.py:confirmation"
```

That covers the part worth testing — the run pauses, and it pauses on the call
you expected. Completing the flow is a client concern: the confirmation is
answered with a function response carrying a `ToolConfirmation` payload. See
[Tool confirmation](/tools-custom/confirmation/) for that side.

## Assert that a workflow pauses for input

A workflow of function nodes needs no model at all. A node that yields
`RequestInput` pauses the run, and the turn ends with an `adk_request_input`
function call whose ID is the interrupt you set:

```python
--8<-- "examples/python/snippets/testing/test_agents.py:workflow"
```

Set a fixed `interrupt_id` in tests. Without one, ADK generates a new ID on every
run, so the test cannot name the pause without reading it from the function call
first.

## Run these tests in CI

Nothing here needs credentials, a network connection, or model quota, so these
tests run on every commit like any other unit test. Two settings make the async
tests work:

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

```text
# requirements.txt
google-adk
pytest
pytest-asyncio
```

If the tests need unreleased behaviour, install ADK from source (`pip install -e .`
in a clone of [google/adk-python](https://github.com/google/adk-python)) so the
scripted model runs against the same code as the rest of the repository.

## What this page does not cover

- **Streaming.** `ScriptedLlm` returns whole responses; code that depends on
  `stream=True` partial chunks needs a model that yields `partial=True`
  responses as well.
- **Live agents.** Bidirectional audio and video agents run through `run_live`
  and are not exercised here.
- **Argument validation.** The scripted model does not check a function call's
  arguments against the tool's declaration, so it can script a call a real model
  would never make. Keep scripted calls to arguments the tool declares.
- **Answer quality.** That is [Evaluation](/evaluate/).

## Where to go next

- [Conversational context](/sessions/) for the state scopes used above —
  `temp:`, `user:` and `app:` keys behave differently across turns.
- [Callbacks](/callbacks/) for asserting that a callback fired, using the same
  scripted-model approach.
- [Tool confirmation](/tools-custom/confirmation/) for the human-in-the-loop
  side of a paused run.
