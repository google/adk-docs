# A2UI — Agent-to-UI for ADK

Supported in ADKPython

A2UI lets your agent generate **real UI** — cards, forms, charts, tables — not just text. Your agent outputs structured JSON, and a renderer on the client turns it into interactive components.

It's transport-agnostic: A2UI payloads work over A2A, MCP, REST, WebSockets, or any other protocol. The agent describes *what* to show; the client decides *how* to render it.

Learn more about A2UI

[a2ui.org](https://a2ui.org/) has the full specification, component gallery, catalog reference, and renderer documentation.

## Quickstart

### Install the SDK

```bash
pip install a2ui-agent-sdk
```

### 1. Set up the Schema Manager

The `A2uiSchemaManager` loads component catalogs and generates system prompts that teach the LLM how to produce valid A2UI JSON.

```python
from a2ui.core.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

schema_manager = A2uiSchemaManager(
    catalogs=[
        BasicCatalog.get_config(
            examples_path="examples",
        ),
    ],
)
```

Note

The schema manager will automatically detect the A2UI version from incoming client requests. You can also set a version explicitly by passing `version=VERSION_0_9` if needed.

Tip

If you omit the `catalogs` parameter, the schema manager uses the [Basic Catalog](https://a2ui.org/concepts/catalogs/) maintained by the A2UI team, which includes common components like Text, Card, Button, Image, and more. You can also create [custom catalogs](#custom-catalogs) with domain-specific components, or mix the basic catalog with your own — see [Advanced patterns](#advanced-patterns) below.

### 2. Generate the system prompt

The `generate_system_prompt` method combines your agent's role description with the A2UI JSON schema and few-shot examples, so the LLM knows exactly how to format its output.

```python
instruction = schema_manager.generate_system_prompt(
    role_description="You are a helpful assistant that presents information with rich UI.",
    workflow_description="Analyze the user's request and return structured UI when appropriate.",
    ui_description="Use cards for summaries, tables for comparisons, and forms for user input.",
    include_schema=True,
    include_examples=True,
    allowed_components=["Heading", "Text", "Card", "Button", "Table"],
)
```

### 3. Create your ADK agent

Use the generated instruction as the agent's system prompt:

```python
from google.adk.agents.llm_agent import LlmAgent

agent = LlmAgent(
    model="gemini-flash-latest",
    name="ui_agent",
    description="An agent that generates rich UI responses.",
    instruction=instruction,
)
```

### 4. Validate and stream A2UI output

Always validate the LLM's JSON output before sending it to the client. The SDK provides parsing, fixing, and validation utilities:

```python
from a2ui.core.parser.parser import parse_response
from a2ui.a2a import parse_response_to_parts

# Get the active catalog's validator
selected_catalog = schema_manager.get_selected_catalog()

# Option A: Manual parse + validate
response_parts = parse_response(llm_output_text)
for part in response_parts:
    if part.a2ui_json:
        selected_catalog.validator.validate(part.a2ui_json)

# Option B: One-liner that returns A2A Parts
parts = parse_response_to_parts(
    llm_output_text,
    validator=selected_catalog.validator,
    fallback_text="Here's what I found.",
)
```

A2UI payloads are wrapped in A2A `DataPart` with the MIME type `application/json+a2ui` so renderers can identify them:

```python
from a2ui.a2a import create_a2ui_part

part = create_a2ui_part({"type": "Card", "props": {"title": "Hello"}})
# → DataPart(data={...}, metadata={"mimeType": "application/json+a2ui"})
```

## Advanced patterns

### Dynamic catalogs

For agents that need different UI components depending on context (e.g., charts for data queries, forms for configuration), resolve the catalog at runtime and store it in session state:

```python
async def _prepare_session(self, context, run_request, runner):
    session = await super()._prepare_session(context, run_request, runner)

    # Determine client capabilities from request metadata
    capabilities = context.message.metadata.get("a2ui_client_capabilities")

    # Select the right catalog
    a2ui_catalog = self.schema_manager.get_selected_catalog(
        client_ui_capabilities=capabilities
    )
    examples = self.schema_manager.load_examples(a2ui_catalog, validate=True)

    # Store in session state for tool access
    await runner.session_service.append_event(
        session,
        Event(
            actions=EventActions(
                state_delta={
                    "system:a2ui_enabled": True,
                    "system:a2ui_catalog": a2ui_catalog,
                    "system:a2ui_examples": examples,
                }
            ),
        ),
    )
    return session
```

### Custom catalogs

You can define your own component catalogs for domain-specific UI:

```python
from a2ui.core.schema.manager import CatalogConfig

schema_manager = A2uiSchemaManager(
    catalogs=[
        BasicCatalog.get_config(),
        CatalogConfig.from_path(
            name="my_dashboard_catalog",
            catalog_path="catalogs/dashboard.json",
            examples_path="catalogs/dashboard_examples",
        ),
    ],
)
```

### Multi-agent orchestration

Orchestrator agents can aggregate A2UI capabilities from sub-agents and advertise them in the agent card:

```python
from a2ui.a2a import get_a2ui_agent_extension

# Collect catalog IDs from sub-agents
supported_catalog_ids = set()
for subagent in subagents:
    for extension in subagent_card.capabilities.extensions:
        if extension.uri == "https://a2ui.org/a2a-extension/a2ui/v0.9":
            supported_catalog_ids.update(
                extension.params.get("supportedCatalogIds") or []
            )

# Advertise in the orchestrator's AgentCard
agent_card = AgentCard(
    capabilities=AgentCapabilities(
        extensions=[
            get_a2ui_agent_extension(
                supported_catalog_ids=list(supported_catalog_ids),
            )
        ]
    )
)
```

## Samples

The A2UI repository includes ADK sample agents you can run immediately:

| Sample                                                                                            | Description                                                                   |
| ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| [restaurant_finder](https://github.com/google/A2UI/tree/main/samples/agent/adk/restaurant_finder) | Static schema agent for searching and displaying restaurant information       |
| [rizzcharts](https://github.com/google/A2UI/tree/main/samples/agent/adk/rizzcharts)               | Dynamic catalog agent that selects chart components based on context          |
| [orchestrator](https://github.com/google/A2UI/tree/main/samples/agent/adk/orchestrator)           | Multi-agent setup that delegates to sub-agents and aggregates UI capabilities |

## Resources

- [A2UI specification](https://a2ui.org/)
- [A2UI GitHub repository](https://github.com/google/A2UI)
- [A2UI Python SDK (`a2ui-agent-sdk`)](https://pypi.org/project/a2ui-agent-sdk/)
- [Agent development guide](https://github.com/google/A2UI/blob/main/agent_sdks/python/agent_development.md)
- [Component gallery](https://a2ui.org/reference/components/)
- [A2A protocol](https://a2a-protocol.org)
