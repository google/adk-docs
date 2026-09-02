from google.adk import Context
from google.adk import Event
from google.adk.agents import LlmAgent
from google.adk.workflow import node

coder_agent = LlmAgent(
    name="generator_agent",
    model="gemini-flash-latest",
    instruction="Write python code for user request.",
    output_schema=str,
)

@node(name="lint_reviewer")
async def compile_lint_check(ctx: Context, code: str):
    # Simulate API call or lint check
    class Response:
        findings = ""
    return Response()

fixer_agent = LlmAgent(
    name="fixer_agent",
    model="gemini-flash-latest",
    instruction="""Refactor current code {code}.
        Based on compile & lint review: {findings}""",
    output_schema=str,
)

@node # workflow node
async def code_workflow(ctx: Context, user_request: str):
  code = await ctx.run_node(coder_agent, user_request)
  check_resp = await ctx.run_node(compile_lint_check, code)

  while check_resp.findings:
    yield Event(state={"code": code, "findings": check_resp.findings})
    code = await ctx.run_node(fixer_agent, {"code": code, "findings": check_resp.findings})

    check_resp = await ctx.run_node(compile_lint_check, code)

  return code