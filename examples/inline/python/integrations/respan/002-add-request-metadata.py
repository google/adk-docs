from respan import Respan, propagate_attributes
from respan_instrumentation_google_adk import GoogleADKInstrumentor

respan = Respan(instrumentations=[GoogleADKInstrumentor()])


async def handle_user_request(user_id: str, message: str):
    with propagate_attributes(
        customer_identifier=user_id,
        thread_identifier="conversation_123",
        metadata={"source": "web"},
    ):
        return await run_adk_agent(message)