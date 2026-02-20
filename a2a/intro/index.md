# Introduction to A2A

As you build more complex agentic systems, you will find that a single agent is often not enough. You will want to create specialized agents that can collaborate to solve a problem. The [**Agent2Agent (A2A) Protocol**](https://a2a-protocol.org) is the standard that allows these agents to communicate with each other.

## When to Use A2A vs. Local Sub-Agents

- **Local Sub-Agents:** These are agents that run *within the same application process* as your main agent. They are like internal modules or libraries, used to organize your code into logical, reusable components. Communication between a main agent and its local sub-agents is very fast because it happens directly in memory, without network overhead.
- **Remote Agents (A2A):** These are independent agents that run as separate services, communicating over a network. A2A defines the standard protocol for this communication.

Consider using **A2A** when:

- The agent you need to talk to is a **separate, standalone service** (e.g., a specialized financial modeling agent).
- The agent is maintained by a **different team or organization**.
- You need to connect agents written in **different programming languages or agent frameworks**.
- You want to enforce a **strong, formal contract** (the A2A protocol) between your system's components.

### When to Use A2A: Concrete Examples

- **Integrating with a Third-Party Service:** Your main agent needs to get real-time stock prices from an external financial data provider. This provider exposes its data through an A2A-compatible agent.
- **Microservices Architecture:** You have a large system broken down into smaller, independent services (e.g., an Order Processing Agent, an Inventory Management Agent, a Shipping Agent). A2A is ideal for these services to communicate with each other across network boundaries.
- **Cross-Language Communication:** Your core business logic is in a Python agent, but you have a legacy system or a specialized component written in Java that you want to integrate as an agent. A2A provides the standardized communication layer.
- **Formal API Enforcement:** You are building a platform where different teams contribute agents, and you need a strict contract for how these agents interact to ensure compatibility and stability.

### When NOT to Use A2A: Concrete Examples (Prefer Local Sub-Agents)

- **Internal Code Organization:** You are breaking down a complex task within a single agent into smaller, manageable functions or modules (e.g., a `DataValidator` sub-agent that cleans input data before processing). These are best handled as local sub-agents for performance and simplicity.
- **Performance-Critical Internal Operations:** A sub-agent is responsible for a high-frequency, low-latency operation that is tightly coupled with the main agent's execution (e.g., a `RealTimeAnalytics` sub-agent that processes data streams within the same application).
- **Shared Memory/Context:** When sub-agents need direct access to the main agent's internal state or shared memory for efficiency, A2A's network overhead and serialization/deserialization would be counterproductive.
- **Simple Helper Functions:** For small, reusable pieces of logic that don't require independent deployment or complex state management, a simple function or class within the same agent is more appropriate than a separate A2A agent.

## The A2A Workflow in ADK: A Simplified View

Agent Development Kit (ADK) simplifies the process of building and connecting agents using the A2A protocol. Here's a straightforward breakdown of how it works:

1. **Making an Agent Accessible (Exposing):** You start with an existing ADK agent that you want other agents to be able to interact with. The ADK provides a simple way to "expose" this agent, turning it into an **A2AServer**. This server acts as a public interface, allowing other agents to send requests to your agent over a network. Think of it like setting up a web server for your agent.
1. **Connecting to an Accessible Agent (Consuming):** In a separate agent (which could be running on the same machine or a different one), you'll use a special ADK component called `RemoteA2aAgent`. This `RemoteA2aAgent` acts as a client that knows how to communicate with the **A2AServer** you exposed earlier. It handles all the complexities of network communication, authentication, and data formatting behind the scenes.

From your perspective as a developer, once you've set up this connection, interacting with the remote agent feels just like interacting with a local tool or function. The ADK abstracts away the network layer, making distributed agent systems as easy to work with as local ones.

## Visualizing the A2A Workflow

To further clarify the A2A workflow, let's look at the "before and after" for both exposing and consuming agents, and then the combined system.

### Exposing an Agent

**Before Exposing:** Your agent code runs as a standalone component, but in this scenario, you want to expose it so that other remote agents can interact with your agent.

```text
+-------------------+
| Your Agent Code   |
|   (Standalone)    |
+-------------------+
```

**After Exposing:** Your agent code is integrated with an `A2AServer` (an ADK component), making it accessible over a network to other remote agents.

```text
+-----------------+
|   A2A Server    |
| (ADK Component) |<--------+
+-----------------+         |
        |                   |
        v                   |
+-------------------+       |
| Your Agent Code   |       |
| (Now Accessible)  |       |
+-------------------+       |
                            |
                            | (Network Communication)
                            v
+-----------------------------+
|       Remote Agent(s)       |
|    (Can now communicate)    |
+-----------------------------+
```

### Consuming an Agent

**Before Consuming:** Your agent (referred to as the "Root Agent" in this context) is the application you are developing that needs to interact with a remote agent. Before consuming, it lacks the direct mechanism to do so.

```text
+----------------------+         +-------------------------------------------------------------+
|      Root Agent      |         |                        Remote Agent                         |
| (Your existing code) |         | (External Service that you want your Root Agent to talk to) |
+----------------------+         +-------------------------------------------------------------+
```

**After Consuming:** Your Root Agent uses a `RemoteA2aAgent` (an ADK component that acts as a client-side proxy for the remote agent) to establish communication with the remote agent.

```text
+----------------------+         +-----------------------------------+
|      Root Agent      |         |         RemoteA2aAgent            |
| (Your existing code) |<------->|         (ADK Client Proxy)        |
+----------------------+         |                                   |
                                 |  +-----------------------------+  |
                                 |  |         Remote Agent        |  |
                                 |  |      (External Service)     |  |
                                 |  +-----------------------------+  |
                                 +-----------------------------------+
      (Now talks to remote agent via RemoteA2aAgent)
```

### Final System (Combined View)

This diagram shows how the consuming and exposing parts connect to form a complete A2A system.

```text
Consuming Side:
+----------------------+         +-----------------------------------+
|      Root Agent      |         |         RemoteA2aAgent            |
| (Your existing code) |<------->|         (ADK Client Proxy)        |
+----------------------+         |                                   |
                                 |  +-----------------------------+  |
                                 |  |         Remote Agent        |  |
                                 |  |      (External Service)     |  |
                                 |  +-----------------------------+  |
                                 +-----------------------------------+
                                                 |
                                                 | (Network Communication)
                                                 v
Exposing Side:
                                               +-----------------+
                                               |   A2A Server    |
                                               | (ADK Component) |
                                               +-----------------+
                                                       |
                                                       v
                                               +-------------------+
                                               | Your Agent Code   |
                                               | (Exposed Service) |
                                               +-------------------+
```

## Concrete Use Case: Customer Service and Product Catalog Agents

Let's consider a practical example: a **Customer Service Agent** that needs to retrieve product information from a separate **Product Catalog Agent**.

### Before A2A

Initially, your Customer Service Agent might not have a direct, standardized way to query the Product Catalog Agent, especially if it's a separate service or managed by a different team.

```text
+-------------------------+         +--------------------------+
| Customer Service Agent  |         |  Product Catalog Agent   |
| (Needs Product Info)    |         | (Contains Product Data)  |
+-------------------------+         +--------------------------+
      (No direct, standardized communication)
```

### After A2A

By using the A2A Protocol, the Product Catalog Agent can expose its functionality as an A2A service. Your Customer Service Agent can then easily consume this service using ADK's `RemoteA2aAgent`.

```text
+-------------------------+         +-----------------------------------+
| Customer Service Agent  |         |         RemoteA2aAgent            |
| (Your Root Agent)       |<------->|         (ADK Client Proxy)        |
+-------------------------+         |                                   |
                                    |  +-----------------------------+  |
                                    |  |     Product Catalog Agent   |  |
                                    |  |      (External Service)     |  |
                                    |  +-----------------------------+  |
                                    +-----------------------------------+
                                                 |
                                                 | (Network Communication)
                                                 v
                                               +-----------------+
                                               |   A2A Server    |
                                               | (ADK Component) |
                                               +-----------------+
                                                       |
                                                       v
                                               +------------------------+
                                               | Product Catalog Agent  |
                                               | (Exposed Service)      |
                                               +------------------------+
```

In this setup, first, the Product Catalog Agent needs to be exposed via an A2A Server. Then, the Customer Service Agent can simply call methods on the `RemoteA2aAgent` as if it were a tool, and the ADK handles all the underlying communication to the Product Catalog Agent. This allows for clear separation of concerns and easy integration of specialized agents.

## Next Steps

Now that you understand the "why" of A2A, let's dive into the "how."

- **Continue to the next guide:** [Quickstart: Exposing Your Agent](https://google.github.io/adk-docs/a2a/quickstart-exposing/index.md)
