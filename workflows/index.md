# Workflows: multi-agent, multi-node applications

Supported in ADKPython v0.1.0Typescript v0.2.0Go v0.1.0Java v0.1.0

As agentic applications grow in complexity, structuring them as a single, monolithic agent can become challenging to develop, evaluate, and maintain. Agent Development Kit (ADK) supports building sophisticated agent applications by composing multiple agents and executable nodes into *agent workflows*. Structuring agents using multiple elements can provide a number of benefits as your agent applications grow more complex and sophisticated:

- **Predictability:** Create more controlled task execution flow using templated logic or graph-based execution mechanisms.
- **Reliability:** Ensure tasks run in the required order or pattern consistently.
- **Structure:** Build complex processes more manageably by composing agents elements, separating task responsibilities, and limiting data contexts for given tasks.

Workflows can be built using several structures and architectures, as illustrated in the following diagram:

**Figure 1.** ADK workflows can have flexible execution paths, or follow specific, templated execution patterns.

The following is a quick guide to the multiple methods for building workflows for your agent application with ADK:

- [**Graph-based workflows:**](/graphs/) (ADK 2.0 and higher) This workflow type allows you to compose both AI-powered agents and deterministic execution nodes into a flexible execution graph that can include decision branching.
- [**Dynamic workflows:**](/graphs/dynamic/) (ADK 2.0 and higher) This workflow type allows you to compose AI-powered agents and deterministic execution nodes using full programmatic code logic.
- [**Collaborative workflows:**](/workflows/collaboration/) (ADK 2.0 and higher) This workflow type allows a single agent to act in a dynamic coordinator role to accomplish tasks with a set of specified sub-agents.
- [**Template workflows:**](/agents/workflow-agents/) These pre-built workflows are extended from ***BaseAgent*** and provide fixed execution logic structures including sequences, loops, and parallel execution.

Follow the links provide above for more information about each type of ADK workflow architecture.

Experimental: Agent Routing

Agent Routing is an experimental feature that allows you to select between multiple agents at runtime using router functions for fallback, A/B testing, and auto-routing. For more information, see [Agent Routing](/agents/routing/).
