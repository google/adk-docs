# Build collaborative agent teams

Supported in ADKPython v2.0.0Beta

Some complex tasks may require multiple agents with specific responsibilities and benefit from less structured procedures, particularly for iterative processes with several, substantial sub-tasks. In a collaborative agent team in ADK, a coordinator agent handles delegation of tasks to one or more subagents. This approach makes it easier to build complex, self-managing agent systems, with subagents defined to handle specific tasks, and automatic return to the parent after completing a task.

When using this self-managed agent team approach, the subagents are assigned an operating ***mode*** to manage their behavior and limit their scope of work. These ***modes*** set general behavior guidelines for subagents and create more predictable and reliable mulit-agent workflows. The following settings are available for collaboration modes:

- ***Chat***: Full user interaction, manual return to parent agent (default, current behavior)
- ***Task***: User interaction for clarifications with automatic return to parent agent
- ***Single-turn:*** No user interaction with automatic return and can be run in parallel

This guide covers how to use modes for your subagents and how these modes impact agent behavior.

Beta Release

ADK 2.0 is a Beta release and may cause breaking changes when used with prior versions of ADK. Do not use ADK 2.0 if you require backwards compatibility, such as in production environments. We encourage you to test this release and we welcome your [feedback](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)!

## Get started

The following code example shows how to set operating modes for a small team of subagents and assign them to a coordinator agent:

```python
from google.adk import Agent

weather_agent = Agent(
    name="weather_checker",
    mode="single_turn",         # no user interaction
    tools=[get_weather, user_info, geocode_address],
)
flight_agent = Agent(
    name="flight_booker",
    mode="task",                # can ask user questions
    input_schema=FlightInput,
    output_schema=FlightResult,
    tools=[search_flights, book_flight],
)
root = Agent(
    name="travel_planner",      # coordinator agent
    sub_agents=[weather_agent, flight_agent],
    # Auto-injects: request_task_weather_checker, request_task_flight_booker
)
```

When you run this workflow, the `travel_planner` coordinator agent automatically identifies and assigns tasks to the subagents. When a subagent completes a task, it automatically returns to the coordinator agent. For more information about structuring data using ***input_schema*** and ***output_schema*** with agents, subagents, and workflow nodes, see [Data handling for agent workflows](/workflows/data-handling/).

## Mode configuration and behaviors

Each collaboration mode has specific behaviors and limitations associated with it. The following table compares the attributes of a subagent configured with each mode:

Caution: Mode only for subagents

The ***mode*** setting is intended specifically for use with subagents invoked by a coordinator parent agent. Do not configure a root agent with the mode setting.

| **Topic \\ Mode**      | `chat` (default)                    | `task`                             | `single_turn`                      |
| ---------------------- | ----------------------------------- | ---------------------------------- | ---------------------------------- |
| **Human in the Loop**  | Full interaction                    | For clarification only             | Disallowed                         |
| **User interaction**   | User chats freely with agent        | Agent asks questions as needed     | No user interaction                |
| **Control flow**       | Agent controls until manual handoff | Agent controls until task complete | Returns immediately after task     |
| **Parallel execution** | Not supported                       | Not supported                      | Multiple tasks can run in parallel |
| **Return to parent**   | Manual (via transfer)               | Automatic (via `complete_task`)    | Automatic (with result)            |

**Table 1.** Comparison of ADK Collaboration agent ***mode*** behavior and limitations.

## Operating considerations

When using collaboration agent modes, there are a few control transfer and context management considerations to consider, as described in the following sections.

### Workflow Node and Agent transfers

Agents configured with ***task*** or ***single-turn*** modes can be used as Workflow Agent graph nodes, and with ***LlmAgent*** instances. However the execution transfer behavior is different depending on the calling, or parent, agent:

**As a workflow graph node:** When a task agent is placed within a workflow graph, such as ***SequentialAgent***, ***ParallelAgent***, the agent executes its task. Upon completion, control automatically advances to the next node based on the logic of the workflow agent's graph.

**As a transferee from an LlmAgent:** When a parent ***LlmAgent*** transfers control to a task agent via `request_task`, the task agent executes until it calls `complete_task`. At that point, control automatically returns to the originating agent that initiated the transfer. This behavior differs from default, chat ***mode*** agents, which require explicit `transfer_to_agent` calls to hand back control.

| **Invocation Context** | **After Task Completion**                |
| ---------------------- | ---------------------------------------- |
| Workflow node          | Advances to next node in the graph       |
| Transfer from LlmAgent | Returns control to the originating agent |

This distinction allows the same task agent to be reused in both contexts without modification. The runtime determines the appropriate control flow based on how the agent was invoked.

### Agent context isolation

Each ***task*** or ***single-turn*** mode agent operates in its own isolated session branch. When these agents operate in parallel, each agent only sees events from its own branch when building context for AI model calls, and cannot see what its peer agents are doing. Once all parallel branches complete, the parent agent receives the collected results and can proceed.

## Known limitations

There are some known limitations with agent collaboration modes:

- ***Task* mode agents** must be leaf agents and cannot have subagents.
