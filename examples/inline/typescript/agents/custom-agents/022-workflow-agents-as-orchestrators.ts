// Conceptual Example: Loop with Condition
import { LoopAgent, LlmAgent, BaseAgent, InvocationContext } from '@google/adk';
import type { Event, createEventActions, EventActions } from '@google/adk';

class CheckConditionAgent extends BaseAgent { // Custom agent to check state
    async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event> {
        const status = ctx.session.state['status'] || 'pending';
        const isDone = status === 'completed';
        yield createEvent({ author: 'check_condition', actions: createEventActions({ escalate: isDone }) });
    }

    async *runLiveImpl(ctx: InvocationContext): AsyncGenerator<Event> {
        // This is not implemented.
    }
};

const processStep = new LlmAgent({name: 'ProcessingStep'}); // Agent that might update state['status']

const poller = new LoopAgent({
    name: 'StatusPoller',
    maxIterations: 10,
    // Executes its sub_agents sequentially in a loop
    subAgents: [processStep, new CheckConditionAgent ({name: 'Checker'})]
});
// When poller runs, it executes processStep then Checker repeatedly
// until Checker escalates (state['status'] === 'completed') or 10 iterations pass.