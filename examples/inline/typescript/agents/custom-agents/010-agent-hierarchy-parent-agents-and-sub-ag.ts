// Conceptual Example: Defining Hierarchy
import { LlmAgent, BaseAgent, InvocationContext } from '@google/adk';
import type { Event, createEventActions } from '@google/adk';

class TaskExecutorAgent extends BaseAgent {
  async *runAsyncImpl(context: InvocationContext): AsyncGenerator<Event, void, void> {
    yield {
      id: 'event-1',
      invocationId: context.invocationId,
      author: this.name,
      content: { parts: [{ text: 'Task completed!' }] },
      actions: createEventActions(),
      timestamp: Date.now(),
    };
  }
  async *runLiveImpl(context: InvocationContext): AsyncGenerator<Event, void, void> {
    this.runAsyncImpl(context);
  }
}

// Define individual agents
const greeter = new LlmAgent({name: 'Greeter', model: 'gemini-flash-latest'});
const taskDoer = new TaskExecutorAgent({name: 'TaskExecutor'}); // Custom non-LLM agent

// Create parent agent and assign children via subAgents
const coordinator = new LlmAgent({
    name: 'Coordinator',
    model: 'gemini-flash-latest',
    description: 'I coordinate greetings and tasks.',
    subAgents: [ // Assign subAgents here
        greeter,
        taskDoer
    ],
});

// Framework automatically sets:
// console.assert(greeter.parentAgent === coordinator);
// console.assert(taskDoer.parentAgent === coordinator);