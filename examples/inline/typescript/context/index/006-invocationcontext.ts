// Pseudocode: Agent implementation receiving InvocationContext
import { BaseAgent, InvocationContext, Event } from '@google/adk';

class MyAgent extends BaseAgent {
  async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event, void, undefined> {
    // Direct access example
    const agentName = ctx.agent.name;
    const sessionId = ctx.session.id;
    console.log(`Agent ${agentName} running in session ${sessionId} for invocation ${ctx.invocationId}`);
    // ... agent logic using ctx ...
    yield; // ... event ...
  }
}