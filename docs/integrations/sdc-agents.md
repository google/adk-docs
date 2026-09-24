---
catalog_title: SDC Agents
catalog_description: Turn enterprise data into validated, self-describing SDC4 data artifacts
catalog_icon: /integrations/assets/sdc-agents.png
catalog_tags: ["data","governance"]
---

# SDC Agents for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[SDC Agents](https://github.com/SemanticDataCharter/SDC_Agents) connect your ADK
agent to the [Semantic Data Charter (SDC)](https://axius-sdc.com/), an
open-standards substrate for trusted, verifiable data. The toolset transforms
SQL, CSV, JSON, and MongoDB sources into validated, self-describing SDC4
artifacts, with structured audit trails and enforced agent isolation boundaries.
It provides eight purpose-scoped toolsets (32 tools) covering introspection,
catalog discovery, mapping, assembly, validation, generation, knowledge, and
distribution, so an agent governs data at the point of ingestion instead of
reconstructing meaning downstream.

## Use cases

- **Govern data at ingestion**: Introspect a SQL, CSV, JSON, or MongoDB source
  and produce validated, self-describing SDC4 artifacts, so definitions,
  constraints, and provenance are bound to the data rather than reconstructed
  later.

- **Discover and reuse published schemas**: Search the SDC4 catalog for matching
  components and map source columns to them by similarity, instead of modeling
  every field from scratch.

- **Assemble and validate data models**: Compose catalog components into a
  cluster hierarchy, assemble the model, and validate the generated artifacts
  deterministically.

- **Keep an audit trail**: Every step emits a structured audit record, and the
  toolsets run within enforced isolation boundaries.

## Prerequisites

- An SDCStudio API key (get one at [sdcstudio.axius-sdc.com](https://sdcstudio.axius-sdc.com)),
  set as the `SDC_API_KEY` environment variable
- Python 3.11 or newer (the `sdc-agents` package requires Python >= 3.11)
- `sdc-agents >= 4.3.3`

## Use with agent

=== "Python"

    Install the toolset:

    ```bash
    pip install google-adk-community[sdc-agents]
    ```

    Set your API key:

    ```bash
    export SDC_API_KEY="your-sdcstudio-api-key"
    ```

    Compose the toolsets into an agent:

    ```python
    import os

    from google.adk.agents import LlmAgent
    from google.adk_community.tools.sdc_agents import (
        SDCAgentsConfig,
        IntrospectToolset,
        CatalogToolset,
        MappingToolset,
        AssemblyToolset,
        ValidationToolset,
    )

    config = SDCAgentsConfig(
        sdcstudio={
            "base_url": os.environ.get("SDC_BASE_URL", "https://sdcstudio.axius-sdc.com"),
            "api_key": os.environ["SDC_API_KEY"],
        },
        datasources={
            "sample": {"type": "csv", "path": "./data/sample.csv"},
        },
        cache={"root": ".sdc-cache"},
        audit={"path": ".sdc-cache/audit.jsonl"},
    )

    root_agent = LlmAgent(
        name="sdc_data_governance_agent",
        model="gemini-2.0-flash",
        description="Introspects data sources and maps them to validated SDC4 data models.",
        instruction=(
            "You help data engineers govern their data. Given a datasource:\n"
            "1. Introspect the structure to discover columns and types.\n"
            "2. Search the SDC4 catalog for matching published schemas.\n"
            "3. Map unmatched columns to schema components by similarity.\n"
            "4. Assemble the final data model.\n"
            "5. Validate the generated artifacts."
        ),
        tools=[
            IntrospectToolset(config=config),
            CatalogToolset(config=config),
            MappingToolset(config=config),
            AssemblyToolset(config=config),
            ValidationToolset(config=config),
        ],
    )
    ```

    The remaining toolsets (`GeneratorToolset`, `KnowledgeToolset`,
    `DistributionToolset`) can be added the same way. See
    [SemanticDataCharter/SDC_Agents](https://github.com/SemanticDataCharter/SDC_Agents)
    for the full set of toolsets and tools.
