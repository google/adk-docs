// Conceptual Code: Iterative Code Refinement
import { LoopAgent, LlmAgent, BaseAgent, InvocationContext } from '@google/adk';
import type { Event, createEvent, createEventActions } from '@google/genai';

// Agent to generate/refine code based on state['current_code'] and state['requirements']
const codeRefiner = new LlmAgent({
    name: 'CodeRefiner',
    instruction: 'Read state["current_code"] (if exists) and state["requirements"]. Generate/refine TypeScript code to meet requirements. Save to state["current_code"].',
    outputKey: 'current_code' // Overwrites previous code in state
});

// Agent to check if the code meets quality standards
const qualityChecker = new LlmAgent({
    name: 'QualityChecker',
    instruction: 'Evaluate the code in state["current_code"] against state["requirements"]. Output "pass" or "fail".',
    outputKey: 'quality_status'
});

// Custom agent to check the status and escalate if 'pass'
class CheckStatusAndEscalate extends BaseAgent {
    async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event> {
        const status = ctx.session.state.quality_status;
        const shouldStop = status === 'pass';
        if (shouldStop) {
            yield createEvent({
                author: 'StopChecker',
                actions: createEventActions(),
            });
        }
    }

    async *runLiveImpl(ctx: InvocationContext): AsyncGenerator<Event> {
        // This agent doesn't have a live implementation
        yield createEvent({ author: 'StopChecker' });
    }
}

// Loop runs: Refiner -> Checker -> StopChecker
// State['current_code'] is updated each iteration.
// Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5 iterations.
const refinementLoop = new LoopAgent({
    name: 'CodeRefinementLoop',
    maxIterations: 5,
    subAgents: [codeRefiner, qualityChecker, new CheckStatusAndEscalate({name: 'StopChecker'})]
});