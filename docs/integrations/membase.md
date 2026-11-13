---
catalog_title: Membase
catalog_description: Search and save a user's long-term memory, with cited recall
catalog_icon: /integrations/assets/membase.svg
catalog_tags: ["data"]
---

# Membase memory for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [`membase-google-adk`](https://pypi.org/project/membase-google-adk/)
package connects your ADK agent to [Membase](https://membase.com), a long-term
memory layer that a user keeps across the AI tools they use. Memory lives in
named Memories, and every search result names the Memory it came from, so the
agent can cite where a fact was learned.

There are two integration approaches, and they can be combined:

| Approach | Description |
|----------|-------------|
| **Tools** (`membase_tools()`) | The agent decides when to search, save, or read the user's profile. |
| **Memory service** (`MembaseMemoryService`) | A `BaseMemoryService` that ADK's `preload_memory` and `load_memory` tools search. |

## Use cases

- **Memory across tools**: The agent recalls what the user told other
  assistants, and the projects, decisions, and documents in their Memories.
- **Cited recall**: Each passage is prefixed with the Memory it came from, for
  example `[Project decisions] We chose Postgres for the ledger.`
- **Deliberate saving**: The agent saves a note in the user's own words when
  the user asks it to remember something. There is no delete tool.

## Prerequisites

- A [Membase](https://app.membase.com) account and a developer key from
  **Connect › Developer keys**. A Read key can search; saving needs a Read &
  write key that reaches a single Memory.
- [Gemini API key](https://aistudio.google.com/app/api-keys) (or any other model
  provider configured with ADK)

## Installation

```bash
pip install membase-google-adk
```

Set the following environment variable:

```bash
export MEMBASE_API_KEY="your-membase-developer-key"
```

## Use with agent

=== "Tools"

    ```python
    from google.adk.agents import Agent
    from membase_google_adk import membase_tools

    root_agent = Agent(
        model="gemini-flash-latest",
        name="membase_agent",
        instruction=(
            "You are a helpful assistant with long-term memory. Search Membase "
            "before answering anything that may depend on what the user told you "
            "before, and cite the Memory in brackets. Save to Membase only when "
            "the user asks you to remember something."
        ),
        tools=membase_tools(),  # reads MEMBASE_API_KEY
    )
    ```

    Run with:

    ```bash
    adk run path/to/your_agent
    ```

=== "Memory service"

    ```python
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import preload_memory
    from membase_google_adk import MembaseMemoryService

    root_agent = Agent(
        model="gemini-flash-latest",
        name="membase_agent",
        instruction="You are a helpful assistant with long-term memory.",
        tools=[preload_memory],
    )

    runner = Runner(
        app_name="membase_app",
        agent=root_agent,
        session_service=InMemorySessionService(),
        memory_service=MembaseMemoryService(),  # reads MEMBASE_API_KEY
    )
    ```

    The `preload_memory` tool searches Membase with the user's message before
    each turn. That search gets 8 seconds by default (`recall_timeout`),
    because the first search after a quiet spell can take up to a minute while
    the memory wakes. When it runs out, the turn continues without memory.

## Available tools

Tool | Description
---- | -----------
`membase_search` | Searches every Memory the key reaches. Each passage names the Memory it came from, and a Memory that could not answer is reported as such.
`membase_save` | Saves one note in the user's own words, when the user asks.
`membase_profile` | Reads the user's profile facts (name, role, lasting preferences), newest first. Needs a key with Profile access.

Use `membase_tools(tools=("search", "profile"))` to leave saving out, for
example with a Read key.

## Configuration

A Membase key belongs to one person's account. In a multi-user app, pass
`client_for`, which maps the user ID that ADK passes to that user's own client:

```python
from membase import Membase
from membase_google_adk import MembaseMemoryService, membase_tools


def client_for(user_id: str) -> Membase:
    # Each user's own Membase developer key, stored by your app.
    return Membase(api_key=get_membase_key(user_id))


memory_service = MembaseMemoryService(client_for=client_for)
tools = membase_tools(client_for=client_for)
```

Writing ADK sessions to memory (`add_session_to_memory`) is off by default.
`MembaseMemoryService(capture=True)` turns it on and keeps only the user's own
words.

## Additional resources

- [`membase-google-adk` on PyPI](https://pypi.org/project/membase-google-adk/)
- [Source and full options](https://github.com/unibaseio/membase/tree/main/integrations/google-adk)
- [Membase documentation](https://docs.membase.com)
