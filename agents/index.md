# Agents

Supported in ADKPythonTypeScriptGoJava

In Agent Development Kit (ADK), an **Agent** is a self-contained execution unit designed to act autonomously to achieve specific goals. Agents can perform tasks, interact with users, utilize external tools, and coordinate with other agents.

The foundation for all agents in ADK is the `BaseAgent` class. It serves as the fundamental blueprint. To create functional agents, you typically extend `BaseAgent` in one of three main ways, catering to different needs – from intelligent reasoning to structured process control.

## Core Agent Categories

ADK provides distinct agent categories to build sophisticated applications:

1. [**LLM Agents (`LlmAgent`, `Agent`)**](https://google.github.io/adk-docs/agents/llm-agents/index.md): These agents utilize Large Language Models (LLMs) as their core engine to understand natural language, reason, plan, generate responses, and dynamically decide how to proceed or which tools to use, making them ideal for flexible, language-centric tasks. [Learn more about LLM Agents...](https://google.github.io/adk-docs/agents/llm-agents/index.md)
1. [**Workflow Agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`)**](https://google.github.io/adk-docs/agents/workflow-agents/index.md): These specialized agents control the execution flow of other agents in predefined, deterministic patterns (sequence, parallel, or loop) without using an LLM for the flow control itself, perfect for structured processes needing predictable execution. [Explore Workflow Agents...](https://google.github.io/adk-docs/agents/workflow-agents/index.md)
1. [**Custom Agents**](https://google.github.io/adk-docs/agents/custom-agents/index.md): Created by extending `BaseAgent` directly, these agents allow you to implement unique operational logic, specific control flows, or specialized integrations not covered by the standard types, catering to highly tailored application requirements. [Discover how to build Custom Agents...](https://google.github.io/adk-docs/agents/custom-agents/index.md)

## Choosing the Right Agent Type

The following table provides a high-level comparison to help distinguish between the agent types. As you explore each type in more detail in the subsequent sections, these distinctions will become clearer.

| Feature              | LLM Agent (`LlmAgent`)            | Workflow Agent                              | Custom Agent (`BaseAgent` subclass)       |
| -------------------- | --------------------------------- | ------------------------------------------- | ----------------------------------------- |
| **Primary Function** | Reasoning, Generation, Tool Use   | Controlling Agent Execution Flow            | Implementing Unique Logic/Integrations    |
| **Core Engine**      | Large Language Model (LLM)        | Predefined Logic (Sequence, Parallel, Loop) | Custom Code                               |
| **Determinism**      | Non-deterministic (Flexible)      | Deterministic (Predictable)                 | Can be either, based on implementation    |
| **Primary Use**      | Language tasks, Dynamic decisions | Structured processes, Orchestration         | Tailored requirements, Specific workflows |

## Agents Working Together: Multi-Agent Systems

While each agent type serves a distinct purpose, the true power often comes from combining them. Complex applications frequently employ [multi-agent architectures](https://google.github.io/adk-docs/agents/multi-agents/index.md) where:

- **LLM Agents** handle intelligent, language-based task execution.
- **Workflow Agents** manage the overall process flow using standard patterns.
- **Custom Agents** provide specialized capabilities or rules needed for unique integrations.

Understanding these core types is the first step toward building sophisticated, capable AI applications with ADK.

## Extend Agent Capabilities

Beyond the core agent types, ADK allows you to significantly expand what your agents can do through several key mechanisms:

- [**AI Models**](/adk-docs/agents/models/): Swap the underlying intelligence of your agents by integrating with different generative AI models from Google and other providers.
- [**Artifacts**](/adk-docs/artifacts/): Enable agents to create and manage persistent outputs like files, code, or documents that exist beyond the conversation lifecycle.
- [**Pre-built tools and integrations**](/adk-docs/integrations/): Equip your agents with a wide array tools, plugins, and other integrations to interact with the world, including web sites, MCP tools, applications, databases, programming interfaces, and more.
- [**Custom tools**](/adk-docs/tools-custom/): Create your own, task-specific tools for solving specific problems with precision and control.
- [**Plugins**](/adk-docs/plugins/): Integrate complex, pre-packaged behaviors and third-party services directly into your agent's workflow.
- [**Skills**](/adk-docs/skills/): Use prebuilt or custom [Agent Skills](https://agentskills.io/) to extend agent capabilities in a way that works efficiently inside AI context window limits.
- [**Callbacks**](/adk-docs/callbacks/): Hook into specific events during an agent's execution lifecycle to add logging, monitoring, or custom side-effects without altering core agent logic.

## Next Steps

Now that you have an overview of the different agent types available in ADK, dive deeper into how they work and how to use them effectively:

- [**LLM Agents:**](https://google.github.io/adk-docs/agents/llm-agents/index.md) Explore how to configure agents powered by large language models, including setting instructions, providing tools, and enabling advanced features like planning and code execution.
- [**Workflow Agents:**](https://google.github.io/adk-docs/agents/workflow-agents/index.md) Learn how to orchestrate tasks using `SequentialAgent`, `ParallelAgent`, and `LoopAgent` for structured and predictable processes.
- [**Custom Agents:**](https://google.github.io/adk-docs/agents/custom-agents/index.md) Discover the principles of extending `BaseAgent` to build agents with unique logic and integrations tailored to your specific needs.
- [**Multi-Agents:**](https://google.github.io/adk-docs/agents/multi-agents/index.md) Understand how to combine different agent types to create sophisticated, collaborative systems capable of tackling complex problems.
- [**Models:**](/adk-docs/agents/models/) Learn about the different LLM integrations available and how to select the right model for your agents.
