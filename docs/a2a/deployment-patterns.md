# A2A Deployment Patterns

This guide covers an advanced deployment pattern for A2A agents: running your
agent as a standalone service using a standard ASGI server like `uvicorn`.

## The `adk api_server` vs. `uvicorn`

- `adk api_server`: This is the simplest way to run your A2A agent. It's great
  for development and for most standard use cases.
- `uvicorn`: This is a production-grade ASGI server. Using `uvicorn` directly
  gives you more control over the server's configuration and allows you to
  deploy your agent as a standard Python web application.

## The Remote Root Agent Pattern

This pattern inverts the usual structure. Instead of a local agent calling
remote services, your **main entry point is a remote agent**. This is ideal for
deploying a complete agent system as a self-contained web service.

### Why Choose This Pattern?

- **Microservices Architecture:** This pattern is a natural fit for a
  microservices architecture. You can deploy your agent as a standalone service
  with a well-defined API, and other services can interact with it.
- **Scalability:** By running your agent as a separate service, you can scale it
  independently of other services.
- **Language Independence:** Once your agent is exposed as a web service, it can
  be called by clients written in any programming language.

### How it Works

1. You build your complete agent with all its tools and logic.
2. At the end of your agent's Python file, you convert it into an ASGI
   application using the `.to_a2a()` method.
3. You run this application using `uvicorn`.
4. Your "local" `main.py` becomes a very thin proxy, containing only a
   `RemoteA2AAgent` that points to your `uvicorn` service.

### Example Code

**Remote Agent with ASGI entry point:**

```python title="my_remote_service/agent.py"
from google.adk import Agent

# ... (all your tools and agent logic) ...

root_agent = Agent(
    name="my_full_service_agent",
    # ...
)

# Convert the agent to a servable application
a2a_app = root_agent.to_a2a()
```

**Running with Uvicorn:**

```bash
# Note we point directly to the a2a_app object
uvicorn my_remote_service.agent:a2a_app --host localhost --port 8001
```

**The Thin Local Proxy:**

```python title="main.py"
from google.adk.agents import RemoteA2AAgent

# This is the only thing in the main file.
root_agent = RemoteA2AAgent(
    name="my_service",
    agent_card="http://localhost:8001/.well-known/agent.json",
)
```