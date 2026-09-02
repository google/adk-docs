---
catalog_title: GoodMem
catalog_description: Add persistent semantic memory to agents across conversations
catalog_icon: /integrations/assets/goodmem.svg
catalog_tags: ["data"]
---

# GoodMem plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [GoodMem ADK plugin](https://github.com/PAIR-Systems-Inc/goodmem-adk)
connects your ADK agent to [GoodMem](https://goodmem.ai), a vector-based
semantic memory service. This integration gives your agent persistent,
searchable memory across conversations, enabling it to recall past interactions,
user preferences, and uploaded documents.

There are two integration approaches:

| Approach | Description |
|----------|-------------|
| **Plugin** (`GoodmemPlugin`) | Implicit, deterministic memory at every turn via ADK callbacks. Saves all conversation turns and file attachments automatically. |
| **Tools** (`GoodmemSaveTool`, `GoodmemFetchTool`) | Explicit, agent-controlled memory. The agent decides when to save and retrieve information. |

## Use cases

- **Persistent memory for agents**: Give your agents long-term memory that
  they can rely on across conversations.
- **Hands-free, multimodal memory management**: Automatically saves and
  retrieves information in conversations, including user messages, agent
  responses, and file attachments (PDF, DOCX, etc.).
- **Never start from scratch**: Agents recall who you are, what you've
  discussed, and solutions you've already worked through — saving tokens and
  avoiding redundant work.

## Prerequisites

- A [GoodMem](https://goodmem.ai/quick-start) instance (self-hosted or cloud)
- GoodMem API key
- [Gemini API key](https://aistudio.google.com/app/api-keys) (for auto-creating embeddings with Gemini)

## Installation

```bash
pip install goodmem-adk
```

## Use with agent

=== "Plugin (Automatic memory)"

    ```python
    --8<-- "examples/inline/python/integrations/goodmem/001-use-with-agent.py"
    ```

=== "Tools (Agent-controlled memory)"

    ```python
    --8<-- "examples/inline/python/integrations/goodmem/002-use-with-agent.py"
    ```

## Available tools

### Plugin callbacks

The `GoodmemPlugin` uses ADK callbacks to manage memory automatically:

Callback | Description
-------- | -----------
`on_user_message_callback` | Saves user messages and file attachments to memory
`before_model_callback` | Retrieves relevant memories and injects them into the prompt
`after_model_callback` | Saves the agent's response to memory

These callbacks are deterministic and run during every agent interaction, saving
all information passed through the agent to memory. The agent doesn't need to
decide when to save or retrieve information.

### Tools

When using the tools approach, the agent has access to:

Tool | Description
---- | -----------
`goodmem_save` | Save text content and file attachments to persistent memory
`goodmem_fetch` | Search memories using semantic similarity queries

These tools are invoked by the agent on demand, and the agent can choose when to
save (possibly with rewrites) or retrieve information based on the conversation
context.

## Configuration

### Environment variables

Variable | Required | Description
-------- | -------- | -----------
`GOODMEM_BASE_URL` | Yes | GoodMem server URL (without `/v1` suffix)
`GOODMEM_API_KEY` | Yes | API key for GoodMem
`GOOGLE_API_KEY` | Yes | Gemini API key for auto-creating Gemini embedder
`GOODMEM_EMBEDDER_ID` | No | Pin a specific embedder (must exist)
`GOODMEM_SPACE_ID` | No | Pin a specific memory space (must exist)
`GOODMEM_SPACE_NAME` | No | Override default space name (auto-created if missing)

### Space resolution

If no space is configured, one is auto-created per user:

- Plugin: `adk_chat_{user_id}`
- Tools: `adk_tool_{user_id}`

## Additional resources

- [GoodMem ADK on GitHub](https://github.com/PAIR-Systems-Inc/goodmem-adk)
- [GoodMem Documentation](https://goodmem.ai)
- [GoodMem ADK on PyPI](https://pypi.org/project/goodmem-adk/)
