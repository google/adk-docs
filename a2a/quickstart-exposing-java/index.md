# Quickstart: Exposing a remote agent via A2A

Supported in ADKJavaExperimental

This quickstart covers the most common starting point for any developer: **"I have an agent. How do I expose it so that other agents can use my agent via A2A?"**. This is crucial for building complex multi-agent systems where different agents need to collaborate and interact.

## Overview

This sample demonstrates how you can expose an ADK agent using Quarkus so that it can be then consumed by another agent using the A2A Protocol.

In Java, you build an A2A server natively by relying on the ADK A2A extension. This uses the Quarkus framework, meaning you just configure your agent directly within your standard Quarkus `@ApplicationScoped` bindings.

```text
┌─────────────────┐                             ┌───────────────────────────────┐
│   Root Agent    │       A2A Protocol          │ A2A-Exposed Check Prime Agent │
│                 │────────────────────────────▶│       (localhost:9090)        │
└─────────────────┘                             └───────────────────────────────┘
```

## Exposing the Remote Agent with Quarkus

Using Quarkus, you map your agent into an A2A execution endpoint without manually wrangling incoming HTTP JSON-RPC payloads or sessions.

### 1. Getting the Sample Code

The fastest way to get started is by checking the standalone Quarkus app inside the `contrib/samples/a2a_server` folder within the [**`adk-java`** repo](https://github.com/google/adk-java).

```bash
cd contrib/samples/a2a_server
```

### 2. How it works

The core runtime uses a provided `AgentExecutor` which requires you to build a CDI `@Produces` bean configuring your native `BaseAgent`. The Quarkus A2A extension discovers this and wires the endpoints automatically.

A2aExposingSnippet.java

```java
import com.google.adk.a2a.executor.AgentExecutorConfig;
import com.google.adk.core.BaseAgent;
import com.google.adk.core.LlmAgent;
import com.google.adk.sessions.InMemorySessionService;
import io.a2a.server.agentexecution.AgentExecutor;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;

import com.google.adk.artifacts.InMemoryArtifactService;

/**
 * Exposing an agent to the A2A network using ADK's Quarkus module.
 * By defining an AgentExecutor as a CDI @Produces, the framework
 * automatically binds your agent to the A2A endpoint.
 */
@ApplicationScoped
public class A2aExposingSnippet {

    @Produces
    public AgentExecutor agentExecutor() {
        BaseAgent myRemoteAgent = LlmAgent.builder()
            .name("prime_agent")
            .model("gemini-2.5-flash")
            .instruction("You are an expert in mathematics. Check if numbers are prime.")
            .build();

        return new com.google.adk.a2a.executor.AgentExecutor.Builder()
            .agent(myRemoteAgent)
            .appName("my-adk-a2a-server")
            .sessionService(new InMemorySessionService())
            .artifactService(new InMemoryArtifactService())
            .agentExecutorConfig(AgentExecutorConfig.builder().build())
            .build();
    }
}
```

The app handles incoming JSON-RPC calls over HTTP mounted on `/a2a/remote/v1/message:send` automatically forwarding parts, history, and contexts directly into your `BaseAgent` flow.

### 3. Start the Remote A2A Agent server

Within the native ADK structure, you can run the Quarkus dev mode task:

```bash
./mvnw -f contrib/samples/a2a_server/pom.xml quarkus:dev
```

Once executed, Quarkus automatically hosts your A2A compliant REST paths. A manual `curl` allows you to immediately smoke test the payload using native A2A specifications:

```bash
curl -X POST http://localhost:9090 \
  -H "Content-Type: application/json" \
  -d '{
        "jsonrpc": "2.0",
        "id": "cli-check",
        "method": "message/send",
        "params": {
          "message": {
            "kind": "message",
            "contextId": "cli-demo-context",
            "messageId": "cli-check-id",
            "role": "user",
            "parts": [
              { "kind": "text", "text": "Is 3 prime?" }
            ]
          }
        }
      }'
```

### 4. Check that your remote agent is running

A proper agent card is exposed over a standard path representing your instance automatically: <http://localhost:9090/.well-known/agent-card.json>

You should be able to see the name dynamically mirrored from your agent configuration inside the response JSON.

## Next Steps

Now that you have exposed your agent via A2A, the next step is to learn how to consume it from another agent orchestrator natively.

- [**A2A Quickstart (Consuming) for Java**](https://adk.dev/a2a/quickstart-consuming-java/index.md): Learn how your agent orchestrator wrapper connects downstream to exposed services.
