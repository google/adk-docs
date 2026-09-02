# Resume stopped agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.16.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

An ADK agent's execution can be interrupted by various factors including
dropped network connections, power failure, or a required external system going
offline. The Resume feature of ADK allows an agent workflow to pick up where it
left off, avoiding the need to restart the entire workflow. In ADK Python 1.16
and higher, you can configure an ADK workflow to be resumable, so that it tracks
the execution of workflow and then allows you to resume it after an unexpected
interruption.

This guide explains how to configure your ADK agent workflow to be resumable.
If you use Custom Agents, you can update them to be resumable. For more
information, see
[Add resume to custom Agents](#custom-agents).

## Add resumable configuration

Enable the Resume function for an agent workflow by applying a Resumability
configuration to the App object of your ADK workflow, as shown in the following
code example:

=== "Python"

    ```python
    --8<-- "examples/inline/python/runtime/resume/001-add-resumable-configuration.py"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/runtime/RunConfigExample.kt:resumability_config"
    ```

!!! warning "Caution: Long Running Functions, Confirmations, Authentication"
    For agents that use
    [Long Running Functions](/tools-custom/function-tools/#long-run-tool),
    [Confirmations](/tools-custom/confirmation/), or
    [Authentication](/tools-custom/authentication/)
    requiring user input, adding a resumable confirmation changes how these features
    operate. For more information, see the documentation for those features.

!!! info "Note: Custom Agents"
    Resume is not supported by default for Custom Agents. You must
    update the agent code for a Custom Agent to support the Resume feature. For
    information on modifying Custom Agents to support incremental resume
    functionality, see
    [Add resume to custom Agents](#custom-agents).

## Resume a stopped workflow

When an ADK workflow stops execution you can resume the workflow using a
command containing the Invocation ID for the workflow instance, which can be
found in the
[Event](/events/#understanding-and-using-events)
history of the workflow. Make sure the ADK API server is running, in case it was
interrupted or powered off, and then run the following command to resume the
workflow, as shown in the following API request example.

```console
# restart the API server if needed:
adk api_server my_resumable_agent/

# resume the agent:
curl -X POST http://localhost:8000/run_sse \
 -H "Content-Type: application/json" \
 -d '{
   "app_name": "my_resumable_agent",
   "user_id": "u_123",
   "session_id": "s_abc",
   "invocation_id": "invocation-123"
 }'
```

You can also resume a workflow using the Runner object Run Async method, as
shown below:

=== "Python"

    ```python
    --8<-- "examples/inline/python/runtime/resume/002-resume-the-agent.py"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/runtime/RunConfigExample.kt:resume_usage"
    ```

!!! info "Note"
    Resuming a workflow from the ADK Web user interface or using the ADK
    command line (CLI) tool is not currently supported.

## How it works

The Resume feature works by logging completed Agent workflow tasks,
including incremental steps using
[Events](/events/) and
[Event Actions](/events/#detecting-actions-and-side-effects).
tracking completion of agent tasks within a resumable workflow. If a workflow is
interrupted and then later restarted, the system resumes the workflow by setting
the completion state of each agent. If an agent did not complete, the workflow
system reinstates any completed Events for that agent, and restarts the workflow
from the partially completed state. For multi-agent workflows, the specific
resume behavior varies, based on the multi-agent classes in your workflow, as
described below:

-   **Sequential Agent**: Reads the current_sub_agent from its saved state
    to find the next sub-agent to run in the sequence.
-   **Loop Agent**: Uses the current_sub_agent and times_looped values to
    continue the loop from the last completed iteration and sub-agent.
-   **Parallel Agent**: Determines which sub-agents have already completed
    and only runs those that have not finished.

Event logging includes results from Tools which successfully returned a result.
So if an agent successfully executed Function Tools A and B, and then failed
during execution of tool C, the system reinstates the results from the
tools A and B, and resumes the workflow by re-running the tool C request.

!!! warning "Caution: Tool execution behavior"
    When resuming a workflow with Tools, the Resume feature ensures
    that the Tools in an agent are run ***at least once***, and may run more than
    once when resuming a workflow. If your agent uses Tools where duplicate runs
    would have a negative impact, such as purchases, you should modify the Tool to
    check for and prevent duplicate runs.

!!! note "Note: Workflow modification with Resume not supported"
    Do not modify a stopped agent workflow before resuming it.
    For example adding or removing agents from workflow that has stopped
    and then resuming that workflow is not supported.

## Add resume to custom Agents {#custom-agents}

Custom agents have specific implementation requirements in order to support
resumability. You must decide on and define workflow steps within your custom
agent which produce a result which can be preserved before handing off to the
next step of processing. The following steps outline how to modify a Custom
Agent to support a workflow Resume.

-   **Create CustomAgentState class**: Extend the BaseAgentState to create
    an object that preserves the state of your agent.
    -   **Optionally, create WorkFlowStep class**: If your custom agent
        has sequential steps, consider creating a WorkFlowStep list object that
        defines the discrete, savable steps of the agent.
-   **Add initial agent state:** Modify your agent's async run function to
    set the initial state of your agent.
-   **Add agent state checkpoints**: Modify your agent's async run function
    to generate and save the agent state for each completed step of the agent's
    overall task.
-   **Add end of agent status to track agent state:** Modify your agent's
    async run function to include an `end_of_agent=True` status upon successful
    completion of the agent's full task.

The following example shows the required code modifications to the example
StoryFlowAgent class shown in the
[Custom Agents](/agents/custom-agents/#full-code-example)
guide:

```python
--8<-- "examples/inline/python/runtime/resume/003-add-resume-to-custom-agents-custom-agent.py"
```
