# my_agent/agent.py
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool


def calculator(a: float, b: float) -> str:
    """Add two numbers and return the result."""
    return str(a + b)


calculator_tool = FunctionTool(func=calculator)

root_agent = LlmAgent(
    name="MathAgent",
    model="gemini-flash-latest",
    instruction=(
        "You are a helpful assistant that can do math. "
        "When asked a math problem, use the calculator tool to solve it."
    ),
    tools=[calculator_tool],
)