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