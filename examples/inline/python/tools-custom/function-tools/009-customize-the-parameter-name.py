from google.adk.tools import ToolContext

def my_tool(arg1: str, ctx: ToolContext):
    # 'ctx' receives the ToolContext because of its type annotation
    user_id = ctx.state.get("user_id")