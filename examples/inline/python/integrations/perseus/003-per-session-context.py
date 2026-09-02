session = await runner.session_service.create_session(
    app_name="perseus_app",
    user_id="user",
    state={
        "_perseus_source": "@perseus\n@file AGENTS.md\n@memory deployment",
        "_perseus_workspace": "/path/to/project",
    },
)