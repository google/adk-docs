from dotenv import load_dotenv
from google_search_agent.agent import agent  # Agent reads env var here

# Too late! Agent already initialized with default model
load_dotenv(Path(__file__).parent / ".env")