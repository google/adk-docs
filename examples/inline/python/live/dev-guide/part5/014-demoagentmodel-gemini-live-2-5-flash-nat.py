from dotenv import load_dotenv
from pathlib import Path

# Load .env file BEFORE importing agent
load_dotenv(Path(__file__).parent / ".env")

# Now safe to import modules that use environment variables
from google_search_agent.agent import agent