---
catalog_title: GoodMem
catalog_description: Add persistent semantic memory to agents across conversations
catalog_icon: /adk-docs/integrations/assets/goodmem.svg
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
