# Example: In a Callback
from google.adk.agents.context import Context

def check_initial_intent(context: Context, **kwargs):
    initial_text = "N/A"
    if context.user_content and context.user_content.parts:
        initial_text = context.user_content.parts[0].text or "Non-text input"

    print(f"This invocation started with user input: '{initial_text}'")

# Example: In an Agent's _run_async_impl
# async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
#     if ctx.user_content and ctx.user_content.parts:
#         initial_text = ctx.user_content.parts[0].text
#         print(f"Agent logic remembering initial query: {initial_text}")
#     ...