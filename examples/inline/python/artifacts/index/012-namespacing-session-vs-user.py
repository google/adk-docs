# Example illustrating namespace difference (conceptual)

# Session-specific artifact filename
session_report_filename = "summary.txt"

# User-specific artifact filename
user_config_filename = "user:settings.json"

# When saving 'summary.txt' via context.save_artifact,
# it's tied to the current app_name, user_id, and session_id.

# When saving 'user:settings.json' via context.save_artifact,
# the ArtifactService implementation should recognize the "user:" prefix
# and scope it to app_name and user_id, making it accessible across sessions for that user.