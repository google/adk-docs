# Unit testing agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>


Unit tests for an agent should be fast, deterministic and free to run. You can get all three by swapping the model for a small scripted one and running the agent in-process with `InMemoryRunner`. The tests then check what your code did: which tools ran, what ended up in session state and artifacts, what the model was sent, and how a workflow behaves when it pauses for input.

This is separate from [evaluation](index.md). Evaluation scores the quality of real model answers; these tests check your agent's logic around the model and run on every commit.

## A scripted model

`BaseLlm` has one method to implement. This version replies with responses you queue up, in order, and keeps a copy of every request it receives so a test can inspect them:

```python
--8<-- "examples/python/snippets/testing/test_agents.py:imports"


--8<-- "examples/python/snippets/testing/test_agents.py:scripted_model"
```

- Each request is deep-copied, so what a test inspects is exactly what the model received, even if the object changes later.
- If the agent calls the model more times than you scripted, `pop` raises `IndexError`, so an unexpected extra model call fails the test instead of passing silently.

## Testing tool calls and state

Script the model to call a tool and then answer. `run_debug` runs one turn on an in-memory session and returns the turn's events. `quiet=True` turns off its console output.

```python
--8<-- "examples/python/snippets/testing/test_agents.py:tool_calls"
```

`run_debug` uses the user id `debug_user_id` and the session id `debug_session_id` unless you pass others, and reuses that session on later calls, so several `run_debug` calls in one test form one conversation.

## Seeding state and checking what the model was sent

Create the session yourself before the first `run_debug` call to start from known state. The recorded requests show exactly what the model received: the system instruction after `{state}` placeholders were filled in, and the history including tool results.

```python
--8<-- "examples/python/snippets/testing/test_agents.py:seed_state"
```

## Tool errors

An exception raised by a tool reaches the test, so `pytest.raises` works directly:

```python
--8<-- "examples/python/snippets/testing/test_agents.py:tool_errors"
```

## Artifacts

`InMemoryRunner` comes with an in-memory artifact service, so a test can load what a tool saved:

```python
--8<-- "examples/python/snippets/testing/test_agents.py:artifacts"
```

## Workflows that pause for input

A workflow of function nodes needs no model at all. When a node returns `RequestInput`, the turn ends with an `adk_request_input` function call whose `id` is the request's `interrupt_id`. Answer it by sending a `FunctionResponse` with the same `id` and name, as a real client does. Use `run_async` here, because the answer is a function response rather than text.

```python
--8<-- "examples/python/snippets/testing/test_agents.py:workflow"
```

Give the request a fixed `interrupt_id` in tests so the answer can refer to it. Without one, ADK generates a new id each run, and the test has to read it from the function call first, as `request.id` above does.

## Limitations

- `ScriptedModel` returns whole responses. It doesn't stream partial chunks, so code that depends on `stream=True` behaviour needs a model that yields `partial=True` responses as well.
- Live (bidirectional audio/video) agents run through `run_live` and are not covered here.
- The scripted model doesn't check that a function call's arguments match the tool's declaration, so a test can script a call a real model would never make. Keep scripted calls to arguments the tool actually declares.

The complete test module is [`examples/python/snippets/testing/test_agents.py`](https://github.com/google/adk-docs/blob/main/examples/python/snippets/testing/test_agents.py). Run it with `pytest` after installing `google-adk`, `pytest` and `pytest-asyncio`.
