from google.adk import Agent
from google.adk.planners import PlanReActPlanner

my_agent = Agent(
    model="gemini-flash-latest",
    planner=PlanReActPlanner(),
    # ... your tools here
)