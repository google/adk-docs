# Agent implementation receiving InvocationContext
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator

class MyAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Direct access example
        agent_name = ctx.agent.name
        session_id = ctx.session.id
        print(f"Agent {agent_name} running in session {session_id} for invocation {ctx.invocation_id}")
        # ... agent logic using ctx ...
        yield # ... event ...