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