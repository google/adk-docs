# Secure implementation example
from google.adk.tools.bash_tool import BashToolPolicy

strict_policy = BashToolPolicy(
    allowed_command_prefixes=("ls ", "cat ", "pwd")
)