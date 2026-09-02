# Conceptual Example: Defining Hierarchy
from google.adk.agents import LlmAgent, BaseAgent


# Define individual agents
greeter = LlmAgent(name="Greeter", model="gemini-flash-latest")
task_doer = BaseAgent(name="TaskExecutor") # Custom non-LLM agent


# Create parent agent and assign children via sub_agents
coordinator = LlmAgent(
    name="Coordinator",
    model="gemini-flash-latest",
    description="I coordinate greetings and tasks.",
    sub_agents=[ # Assign sub_agents here
        greeter,
        task_doer
    ]
)


# Framework automatically sets:
# assert greeter.parent_agent == coordinator
# assert task_doer.parent_agent == coordinator