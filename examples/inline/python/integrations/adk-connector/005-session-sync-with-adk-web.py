connector = DiscordConnector(
    token=token,
    agent=assistant,
    session_management_across_device=True,  # Spin up DB & mapping persistence
    dev_user_id=os.getenv("DISCORD_USER_ID")  # Syncs this ID to the "user" Web UI namespace
)