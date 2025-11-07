# Quickstart: Consuming a remote agent via A2A

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-go">Go</span><span class="lst-preview">Experimental</span>
</div>

This quickstart covers the most common starting point for any developer: **"There is a remote agent, how do I let my ADK agent use it via A2A?"**. This is crucial for building complex multi-agent systems where different agents need to collaborate and interact.

## Overview

This sample demonstrates the **Agent-to-Agent (A2A)** architecture in the Agent Development Kit (ADK), showcasing how multiple agents can work together to handle complex tasks. The sample implements an agent that can roll dice and check if numbers are prime.

```text
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   Root Agent    │───▶│   Roll Agent     │    │   Remote Prime     │
│  (Local)        │    │   (Local)        │    │   Agent            │
│                 │    │                  │    │  (localhost:8001)  │
│                 │───▶│                  │◀───│                    │
└─────────────────┘    └──────────────────┘    └────────────────────┘
```

The A2A Basic sample consists of:

- **Root Agent** (`root_agent`): The main orchestrator that delegates tasks to specialized sub-agents
- **Roll Agent** (`roll_agent`): A local sub-agent that handles dice rolling operations
- **Prime Agent** (`prime_agent`): A remote A2A agent that checks if numbers are prime, this agent is running on a separate A2A server

## Exposing Your Agent with the ADK Server

  In the `a2a_basic` example, you will first need to expose the `check_prime_agent` via an A2A server, so that the local root agent can use it.

### 1. Getting the Sample Code { #getting-the-sample-code }

First, make sure you have Go installed and your environment is set up.

You can clone and navigate to the [**`a2a_basic`** sample](https://github.com/google/adk-docs/tree/main/examples/go/a2a_basic) here:

```bash
cd examples/go/a2a_basic
```

As you'll see, the folder structure is as follows:

```text
a2a_basic/
├── remote_a2a/
│   └── check_prime_agent/
│       └── main.go
├── go.mod
├── go.sum
└── main.go # local root agent
```

#### Main Agent (`a2a_basic/main.go`)

- **`rollDieTool`**: Function tool for rolling dice
- **`newRollAgent`**: Local agent specialized in dice rolling
- **`newPrimeAgent`**: Remote A2A agent configuration
- **`newRootAgent`**: Main orchestrator with delegation logic

#### Remote Prime Agent (`a2a_basic/remote_a2a/check_prime_agent/main.go`)

- **`checkPrimeTool`**: Prime number checking algorithm
- **`main`**: Implementation of the prime checking service and A2A server.

### 2. Start the Remote Prime Agent server { #start-the-remote-prime-agent-server }

To show how your ADK agent can consume a remote agent via A2A, you'll first need to start a remote agent server, which will host the prime agent (under `check_prime_agent`).

```bash
# Start the remote a2a server that serves the check_prime_agent on port 8001
go run remote_a2a/check_prime_agent/main.go
```

Once executed, you should see something like:

``` shell
2025/11/06 11:00:19 Starting A2A prime checker server on port 8001
2025/11/06 11:00:19 Starting the web server: &{port:8001}
2025/11/06 11:00:19 
2025/11/06 11:00:19 Web servers starts on http://localhost:8001
2025/11/06 11:00:19        a2a:  you can access A2A using jsonrpc protocol: http://localhost:8001
```
  
### 3. Look out for the required agent card of the remote agent { #look-out-for-the-required-agent-card-of-the-remote-agent }

A2A Protocol requires that each agent must have an agent card that describes what it does.

In the Go ADK, the agent card is generated dynamically when you expose an agent using the A2A launcher. You can visit `http://localhost:8001/.well-known/agent-card.json` to see the generated card.

### 4. Run the Main (Consuming) Agent { #run-the-main-consuming-agent }

  ```bash
  # In a separate terminal, run the main agent
  go run main.go
  ```

#### How it works

The main agent uses `remoteagent.New` to consume the remote agent (`prime_agent` in our example). As you can see below, it requires the `Name`, `Description`, and the `AgentCardSource` URL.

```go title="a2a_basic/main.go"
--8<-- "examples/go/a2a_basic/main.go:new-prime-agent"
```

Then, you can simply use the remote agent in your root agent. In this case, `primeAgent` is used as one of the sub-agents in the `root_agent` below:

```go title="a2a_basic/main.go"
--8<-- "examples/go/a2a_basic/main.go:new-root-agent"
```

## Example Interactions

Once both your main and remote agents are running, you can interact with the root agent to see how it calls the remote agent via A2A:

**Simple Dice Rolling:**
This interaction uses a local agent, the Roll Agent:

```text
User: Roll a 6-sided die
Bot calls tool: transfer_to_agent with args: map[agent_name:roll_agent]
Bot calls tool: roll_die with args: map[sides:6]
Bot: I rolled a 6-sided die and the result is 6.
```

**Prime Number Checking:**

This interaction uses a remote agent via A2A, the Prime Agent:

```text
User: Is 7 a prime number?
Bot calls tool: transfer_to_agent with args: map[agent_name:prime_agent]
Bot calls tool: prime_checking with args: map[nums:[7]]
Bot: Yes, 7 is a prime number.
```

**Combined Operations:**

This interaction uses both the local Roll Agent and the remote Prime Agent:

```text
User: roll a die and check if it's a prime
Bot: Okay, I will first roll a die and then check if the result is a prime number.

Bot calls tool: transfer_to_agent with args: map[agent_name:roll_agent]
Bot calls tool: roll_die with args: map[sides:6]
Bot calls tool: transfer_to_agent with args: map[agent_name:prime_agent]
Bot calls tool: prime_checking with args: map[nums:[3]]
Bot: 3 is a prime number.
```

## Next Steps

Now that you have created an agent that's using a remote agent via an A2A server, the next step is to learn how to expose your own agent.

- [**A2A Quickstart (Exposing)**](./quickstart-exposing-go.md): Learn how to expose your existing agent so that other agents can use it via the A2A Protocol.
