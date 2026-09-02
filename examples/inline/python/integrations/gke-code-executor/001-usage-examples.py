from google.adk.agents import LlmAgent
from google.adk.code_executors import GkeCodeExecutor
from google.adk.code_executors import CodeExecutionInput
from google.adk.agents.invocation_context import InvocationContext

# Initialize the executor for Sandbox Mode
# Namespace should have RBAC for SandboxClaims and Sandbox
gke_sandbox_executor = GkeCodeExecutor(
    namespace="agent-sandbox-system",  # Typically where agent-sandbox is installed
    executor_type="sandbox",
    sandbox_template="python-sandbox-template",
    sandbox_gateway_name="your-gateway-name", # Optional
)

# Example direct execution:
ctx = InvocationContext()
result = gke_sandbox_executor.execute_code(ctx, CodeExecutionInput(code="print('Hello from Sandbox Mode')"))
print(result.stdout)

# Example with an Agent:
gke_sandbox_agent = LlmAgent(
    name="gke_sandbox_coding_agent",
    model="gemini-flash-latest",
    instruction="You are a helpful AI agent that writes and executes Python code using sandboxes.",
    code_executor=gke_sandbox_executor,
)