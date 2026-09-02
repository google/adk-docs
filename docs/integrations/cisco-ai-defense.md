---
catalog_title: Cisco AI Defense
catalog_description: Security guardrails to monitor or block agent prompts and tool calls
catalog_icon: /integrations/assets/cisco-ai-defense.png
---

# Cisco AI Defense plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Cisco AI
Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html)
is an enterprise AI security platform that provides runtime guardrails to
protect against threats like prompt injection, data leakage, and harmful
content. The [ADK
plugin](https://github.com/cisco-ai-defense/ai-defense-google-adk) integrates
these guardrails directly into the ADK Runner lifecycle: it inspects prompts,
model responses, and tool calls, then allows or blocks them based on configurable
security policies.

## Use cases

- **Runtime protection for model calls**: Inspect user prompts before model
  calls and model outputs after generation, then allow or block based on policy
  (`monitor` or `enforce`).
- **Tool and MCP call inspection**: Inspect tool call requests before execution
  and tool responses after execution, and block unsafe tool behavior in
  `enforce` mode with clear metadata.
- **Auditable decision trace and alerts**: Capture decision context (action,
  severity, classifications, request_id/event_id) and optionally trigger an
  `on_violation` callback for monitoring and incident response.

## Prerequisites

- [Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html) account and API key
- Python >= 3.10
- [ADK](https://adk.dev) >= 1.0.0

## Installation

```bash
pip install cisco-aidefense-google-adk
```

Set the `AI_DEFENSE_API_KEY` environment variable (and `AI_DEFENSE_MCP_API_KEY`
for tool inspection).

## Use with agent

### Quickstart

Add Cisco AI Defense to any ADK agent with a single line:

```python
--8<-- "examples/inline/python/integrations/cisco-ai-defense/001-quickstart.py"
```

Or get a plugin for the entire app:

```python
--8<-- "examples/inline/python/integrations/cisco-ai-defense/002-quickstart.py"
```

### Global plugin

Use `CiscoAIDefensePlugin` to apply inspection globally to all agents in a
Runner:

```python
--8<-- "examples/inline/python/integrations/cisco-ai-defense/003-global-plugin.py"
```

### Per-agent callbacks

Use `make_aidefense_callbacks` to wire inspection into a specific agent:

```python
--8<-- "examples/inline/python/integrations/cisco-ai-defense/004-per-agent-callbacks.py"
```

## Modes

The plugin supports three operating modes:

Mode | Behavior
---- | --------
`monitor` | Inspect all traffic, log violations, never block (default)
`enforce` | Inspect all traffic, block requests/responses that violate policy
`off` | Skip inspection entirely

Modes can be set globally or per-channel:

```python
--8<-- "examples/inline/python/integrations/cisco-ai-defense/005-modes.py"
```

## Violation callback

Use the `on_violation` callback to receive notifications for every violation in
both `monitor` and `enforce` modes:

```python
--8<-- "examples/inline/python/integrations/cisco-ai-defense/006-violation-callback.py"
```

## Retry and fail-open support

For automatic retry with exponential backoff, fail-open/fail-closed semantics,
and structured `Decision` objects, use the `AgentsecPlugin` variant:

```python
--8<-- "examples/inline/python/integrations/cisco-ai-defense/007-retry-and-fail-open-support.py"
```

Or at the per-agent level:

```python
--8<-- "examples/inline/python/integrations/cisco-ai-defense/008-retry-and-fail-open-support.py"
```

## Additional resources

- [GitHub Repository](https://github.com/cisco-ai-defense/ai-defense-google-adk)
- [PyPI Package](https://pypi.org/project/cisco-aidefense-google-adk/)
- [Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html)
- [cisco-aidefense-sdk on PyPI](https://pypi.org/project/cisco-aidefense-sdk/)
