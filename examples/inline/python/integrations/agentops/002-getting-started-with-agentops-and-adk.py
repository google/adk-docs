import agentops
import os
from dotenv import load_dotenv

# Load environment variables (optional, if you use a .env file for API keys)
load_dotenv()

agentops.init(
    api_key=os.getenv("AGENTOPS_API_KEY"), # Your AgentOps API Key
    trace_name="my-adk-app-trace"  # Optional: A name for your trace
    # auto_start_session=True is the default.
    # Set to False if you want to manually control session start/end.
)