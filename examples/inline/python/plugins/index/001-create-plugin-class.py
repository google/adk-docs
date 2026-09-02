from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin

class CountInvocationPlugin(BasePlugin):
"""A custom plugin that counts agent and tool invocations."""

def __init__(self) -> None:
    """Initialize the plugin with counters."""
    super().__init__(name="count_invocation")
    self.agent_count: int = 0
    self.tool_count: int = 0
    self.llm_request_count: int = 0

async def before_agent_callback(
    self, *, agent: BaseAgent, callback_context: CallbackContext
) -> None:
    """Count agent runs."""
    self.agent_count += 1
    print(f"[Plugin] Agent run count: {self.agent_count}")

async def before_model_callback(
    self, *, callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """Count LLM requests."""
    self.llm_request_count += 1
    print(f"[Plugin] LLM request count: {self.llm_request_count}")