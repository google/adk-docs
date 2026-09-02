// Conceptual Setup: Agent as a Tool
import { LlmAgent, BaseAgent, AgentTool, InvocationContext } from '@google/adk';
import type { Part, createEvent, Event } from '@google/genai';

// Define a target agent (could be LlmAgent or custom BaseAgent)
class ImageGeneratorAgent extends BaseAgent { // Example custom agent
    constructor() {
        super({name: 'ImageGen', description: 'Generates an image based on a prompt.'});
    }
    // ... internal logic ...
    async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event> { // Simplified run logic
        const prompt = ctx.session.state['image_prompt'] || 'default prompt';
        // ... generate image bytes ...
        const imageBytes = new Uint8Array(); // placeholder
        const imagePart: Part = {inlineData: {data: Buffer.from(imageBytes).toString('base64'), mimeType: 'image/png'}};
        yield createEvent({content: {parts: [imagePart]}});
    }

    async *runLiveImpl(ctx: InvocationContext): AsyncGenerator<Event, void, void> {
        // Not implemented for this agent.
    }
}

const imageAgent = new ImageGeneratorAgent();
const imageTool = new AgentTool({agent: imageAgent}); // Wrap the agent

// Parent agent uses the AgentTool
const artistAgent = new LlmAgent({
    name: 'Artist',
    model: 'gemini-flash-latest',
    instruction: 'Create a prompt and use the ImageGen tool to generate the image.',
    tools: [imageTool] // Include the AgentTool
});
// Artist LLM generates a prompt, then calls:
// {functionCall: {name: 'ImageGen', args: {image_prompt: 'a cat wearing a hat'}}}
// Framework calls imageTool.runAsync(...), which runs ImageGeneratorAgent.
// The resulting image Part is returned to the Artist agent as the tool result.