// Pseudocode: Inside agent's runAsyncImpl
import { BaseAgent, InvocationContext } from '@google/adk';
import type { Event } from '@google/adk';

class MyControllingAgent extends BaseAgent {
  async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event, void, undefined> {
    // Example: Check if a specific service is available
    if (!ctx.memoryService) {
      console.log('Memory service is not available for this invocation.');
      // Potentially change agent behavior
    }

    // Example: Early termination based on some condition
    // Direct access to state via ctx.session.state or through ctx.session.state property if wrapped
    if ((ctx.session.state as { 'critical_error_flag': boolean })['critical_error_flag']) {
      console.log('Critical error detected, ending invocation.');
      ctx.endInvocation = true; // Signal framework to stop processing
      yield {
        author: this.name,
        invocationId: ctx.invocationId,
        content: { parts: [{ text: 'Stopping due to critical error.' }] }
      } as Event;
      return; // Stop this agent's execution
    }

    // ... Normal agent processing ...
    yield; // ... event ...
  }
}