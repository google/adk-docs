# Quickstart: Consuming a remote agent via A2A

Supported in ADKJavaExperimental

This quickstart covers the most common starting point for any developer: **"There is a remote agent, how do I let my ADK agent use it via A2A?"**. This is crucial for building complex multi-agent systems where different agents need to collaborate and interact.

## Overview

This sample demonstrates the **Agent2Agent (A2A)** architecture in the Agent Development Kit (ADK) for Java, showcasing how multiple agents can work together to handle complex tasks.

```text
┌─────────────────┐    ┌─────────────────┐    ┌────────────────────────┐
│   Root Agent    │───▶│   Roll Agent    │    │   Remote Prime Agent   │
│   (Local)       │    │   (Local)       │    │   (localhost:8001)     │
│                 │───▶│                 │◀───│                        │
└─────────────────┘    └─────────────────┘    └────────────────────────┘
```

The A2A Basic sample consists of:

- **Root Agent** (`root_agent`): The main orchestrator that delegates tasks to specialized sub-agents
- **Roll Agent** (`roll_agent`): A local sub-agent that handles dice rolling operations
- **Prime Agent** (`prime_agent`): A remote A2A agent that checks if numbers are prime, this agent is running on a separate A2A server

## Consuming Your Agent Using the ADK Java SDK

In Java, rather than manually generating requests, ADK relies on the official A2A SDK `Client` wrapped precisely over a `RemoteA2AAgent` entity. Note that the Java SDK currently uses A2A Protocol 0.3.

### 1. Getting the Sample Code

The native sample matching this quickstart workflow in Java can be found in the `adk-java` source code under `contrib/samples/a2a_basic`.

You can navigate to the [**`a2a_basic`** sample](https://github.com/google/adk-java/tree/main/contrib/samples/a2a_basic):

```bash
cd contrib/samples/a2a_basic
```

### 2. Start the Remote Prime Agent server

To show how your ADK agent can consume a remote agent via A2A, you'll first need a remote agent server running. While you can write your own custom A2A server in any language, ADK provides the `a2a_server` sample which starts a Quarkus service hosting the agent on `:9090`.

```bash
# In adk-java root, start the pre-configured Quarkus remote service on port 9090
./mvnw -f contrib/samples/a2a_server/pom.xml quarkus:dev
```

Once running successfully, the agent will be accessible via HTTP endpoints locally.

### 3. Look out for the required agent card of the remote agent

A2A Protocol requires that each agent have an agent card that describes what it does to other nodes over the network. In an A2A server, the agent card is generated dynamically on boot and hosted statically.

For an ADK Java webservice, the agent card is generally accessible dynamically using the [`.well-known/agent-card.json`](http://localhost:9090/.well-known/agent-card.json) standard endpoint format relative to its base URL.

### 4. Run the Main (Consuming) Agent

In another terminal, you can run the client agent:

```bash
./mvnw -f contrib/samples/a2a_basic/pom.xml exec:java -Dexec.args="http://localhost:9090"
```

#### How it works

The main agent accesses the required A2A JSON-RPC transport wrapper to consume the remote agent (`prime_agent` in our example). As you can see below, it queries for the `AgentCard` from the target host and registers it locally inside an official A2A `Client`.

A2aConsumerSnippet.java

```java
String primeAgentBaseUrl = "http://localhost:9090";
String agentCardUrl = primeAgentBaseUrl + "/.well-known/agent-card.json";

// 1. Resolve the public AgentCard from the remote agent's .well-known endpoint
AgentCard publicAgentCard = new A2ACardResolver(
    new JdkA2AHttpClient(), 
    primeAgentBaseUrl, 
    agentCardUrl
).getAgentCard();

// 2. Build the official A2A SDK Client using the resolved card and transport
Client a2aClient = Client.builder(publicAgentCard)
    .withTransport(JSONRPCTransport.class, new JSONRPCTransportConfig())
    .clientConfig(
        new ClientConfig.Builder()
            .setStreaming(publicAgentCard.capabilities().streaming())
            .build()
    )
    .build();

// 3. Wrap it in the ADK's RemoteA2AAgent natively
BaseAgent remotePrimeAgent = RemoteA2AAgent.builder()
    .name(publicAgentCard.name())
    .a2aClient(a2aClient)
    .agentCard(publicAgentCard)
    .build();
```

You can then pass the remote agent instance naturally to your agent builder, simply acting as just another standard ADK sub-agent. The ADK takes over internally for all translation logic over the wire.

A2aConsumerSnippet.java

```java
BaseAgent rootAgent = LlmAgent.builder()
    .name("root_agent")
    .model("gemini-2.5-flash")
    .instruction("You are a helpful assistant that can check prime numbers by delegating to prime_agent.")
    .subAgents(remotePrimeAgent)
    .build();
```

## Next Steps

Now that you have created an agent that's using a remote agent via an A2A server, the next step is to learn how to expose your own Java agent.

- [**A2A Quickstart (Exposing) for Java**](https://adk.dev/a2a/quickstart-exposing-java/index.md): Learn how to expose your existing agent so that other agents can use it via the A2A Protocol.
