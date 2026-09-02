# First run: process crashes after tool 1 completes.
# Second run: Dapr automatically resumes and executes tools 2 and 3.
runner = DaprWorkflowAgentRunner(agent=agent, name="sequential-agent")
runner.start()

async for event in runner.run_async(
    user_message="Run the three-step pipeline.",
    session_id="pipeline-001",
):
    if event["type"] == "workflow_completed":
        print(event["final_response"])