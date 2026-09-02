from google.adk.agents import LlmAgent
from google.adk.code_executors import GkeCodeExecutor
from google.adk.code_executors import CodeExecutionInput
from google.adk.agents.invocation_context import InvocationContext

# Initialize the executor for Job Mode
# Namespace should have RBAC for Jobs, ConfigMaps, Pods, Logs
gke_executor = GkeCodeExecutor(
    namespace="agent-ns",
    executor_type="job",
    timeout_seconds=600,
    cpu_limit="1000m",  # 1 CPU core
    mem_limit="1Gi",
)

# Example direct execution:
ctx = InvocationContext()
result = gke_executor.execute_code(ctx, CodeExecutionInput(code="print('Hello from Job Mode')"))
print(result.stdout)

# Example with an Agent:
gke_agent = LlmAgent(
    name="gke_coding_agent",
    model="gemini-flash-latest",
    instruction="You are a helpful AI agent that writes and executes Python code.",
    code_executor=gke_executor,
)