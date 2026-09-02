---
catalog_title: A2UI
catalog_description: Generate rich, structured UIs from your agents using the Agent-to-UI protocol
catalog_icon: /integrations/assets/a2ui.svg
---

# A2UI — Agent-to-UI for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

A2UI lets your agent generate **real UI** — cards, forms, charts, tables — not
just text. Your agent outputs structured JSON, and a renderer on the client
turns it into interactive components.

It's transport-agnostic: A2UI payloads work over A2A, MCP, REST, WebSockets,
or any other protocol. The agent describes *what* to show; the client decides
*how* to render it.

!!! info "Learn more about A2UI"
    [a2ui.org](https://a2ui.org/) has the full specification, component
    gallery, catalog reference, and renderer documentation.

## Quickstart

### Install the SDK

```bash
pip install a2ui-agent-sdk
```

### 1. Set up the Schema Manager

The `A2uiSchemaManager` loads component catalogs and generates system prompts
that teach the LLM how to produce valid A2UI JSON.

```python
--8<-- "examples/inline/python/integrations/a2ui/001-1-set-up-the-schema-manager.py"
```

!!! note
    The schema manager will automatically detect the A2UI version from
    incoming client requests. You can also set a version explicitly by
    passing `version=VERSION_0_9` if needed.

!!! tip
    If you omit the `catalogs` parameter, the schema manager uses the
    [Basic Catalog](https://a2ui.org/concepts/catalogs/) maintained by the
    A2UI team, which includes common components like Text, Card, Button,
    Image, and more. You can also create [custom catalogs](#custom-catalogs)
    with domain-specific components, or mix the basic catalog with your own
    — see [Advanced patterns](#advanced-patterns) below.

### 2. Generate the system prompt

The `generate_system_prompt` method combines your agent's role description with
the A2UI JSON schema and few-shot examples, so the LLM knows exactly how to
format its output.

```python
--8<-- "examples/inline/python/integrations/a2ui/002-2-generate-the-system-prompt.py"
```

### 3. Create your ADK agent

Use the generated instruction as the agent's system prompt:

```python
--8<-- "examples/inline/python/integrations/a2ui/003-3-create-your-adk-agent.py"
```

### 4. Validate and stream A2UI output

Always validate the LLM's JSON output before sending it to the client. The SDK
provides parsing, fixing, and validation utilities:

```python
--8<-- "examples/inline/python/integrations/a2ui/004-4-validate-and-stream-a2ui-output.py"
```

A2UI payloads are wrapped in A2A `DataPart` with the MIME type
`application/json+a2ui` so renderers can identify them:

```python
--8<-- "examples/inline/python/integrations/a2ui/005-option-b-one-liner-that-returns-a2a-part.py"
```

## Advanced patterns

### Dynamic catalogs

For agents that need different UI components depending on context (e.g., charts
for data queries, forms for configuration), resolve the catalog at runtime and
store it in session state:

```python
--8<-- "examples/inline/python/integrations/a2ui/006-dynamic-catalogs.py"
```

### Custom catalogs

You can define your own component catalogs for domain-specific UI:

```python
--8<-- "examples/inline/python/integrations/a2ui/007-custom-catalogs.py"
```

### Multi-agent orchestration

Orchestrator agents can aggregate A2UI capabilities from sub-agents and
advertise them in the agent card:

```python
--8<-- "examples/inline/python/integrations/a2ui/008-multi-agent-orchestration.py"
```

## Samples

The A2UI repository includes ADK sample agents you can run immediately:

| Sample | Description |
|---|---|
| [restaurant_finder](https://github.com/a2ui-project/a2ui/tree/main/samples/agent/adk/restaurant_finder) | Static schema agent for searching and displaying restaurant information |
| [rizzcharts](https://github.com/a2ui-project/a2ui/tree/main/samples/community/agent/adk/rizzcharts) | Dynamic catalog agent that selects chart components based on context |
| [orchestrator](https://github.com/a2ui-project/a2ui/tree/main/samples/community/agent/adk/orchestrator) | Multi-agent setup that delegates to sub-agents and aggregates UI capabilities |

## Resources

- [A2UI specification](https://a2ui.org/)
- [A2UI GitHub repository](https://github.com/a2ui-project/a2ui)
- [A2UI Python SDK (`a2ui-agent-sdk`)](https://pypi.org/project/a2ui-agent-sdk/)
- [Agent development guide](https://github.com/a2ui-project/a2ui/blob/main/agent_sdks/python/a2ui_agent/agent_development.md)
- [Component gallery](https://a2ui.org/reference/components/)
- [A2A protocol](https://a2a-protocol.org)
