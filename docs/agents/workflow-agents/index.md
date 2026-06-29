# Template agent workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

This section introduces *template workflows*, also known as *workflow agents*,
which are specialized agents that control the execution flow of one or more
sub-agents. Template workflow agents are specialized components designed for
orchestrating the execution flow of sub-agents. Their primary role is to manage
how and when other agents run, defining the control flow of a process.

!!! note "Alternative: graph-based workflows"

    Starting in ADK 2.0 for Python and Go, template workflows have been superseded

    by more flexible workflow structures, including
    [graph-based workflows](/graphs/) and
    [dynamic workflows](/graphs/dynamic/).
    These workflow architectures provide more control, flexibility
    and capability to evolve your agent workflows over time.

<img src="/assets/template_workflows.svg" alt="Template agent workflows in ADK">

**Figure 1.** Execution patterns of template workflows in ADK

Template workflow agents operate based on predefined logic. They determine the
execution sequence according to their type, such as sequential, parallel, or
loop, without consulting an AI model for assistance with the orchestration. This
approach results in deterministic and predictable execution patterns. Template
workflows include the following task execution structures, which each implement
a distinct task completion pattern:

<div class="grid cards" markdown>

- :material-console-line: **Sequential Agent workflow**

    ---

    Executes sub-agents one after another, in sequence.

    [:octicons-arrow-right-24: Learn more](sequential-agents.md)

- :material-console-line: **Loop Agent workflow**

    ---

    Repeatedly executes its sub-agents until a specific termination condition is met.

    [:octicons-arrow-right-24: Learn more](loop-agents.md)

- :material-console-line: **Parallel Agent workflow**

    ---

    Executes multiple sub-agents in parallel.

    [:octicons-arrow-right-24: Learn more](parallel-agents.md)

</div>