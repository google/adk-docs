import {z} from 'zod';
import { LlmAgent, FunctionTool } from '@google/adk';

// Define the schema for the tool's input parameters
const getCapitalCityParamsSchema = z.object({
    country: z.string().describe('The country to get capital for.'),
});

// Define the tool function itself
async function getCapitalCity(params: z.infer<typeof getCapitalCityParamsSchema>): Promise<{ capitalCity: string }> {
const capitals: Record<string, string> = {
    'france': 'Paris',
    'japan': 'Tokyo',
    'canada': 'Ottawa',
};
const result = capitals[params.country.toLowerCase()] ??
    `Sorry, I don't know the capital of ${params.country}.`;
return {capitalCity: result}; // Tools must return an object
}

// Create an instance of the FunctionTool
const getCapitalCityTool = new FunctionTool({
    name: 'getCapitalCity',
    description: 'Retrieves the capital city for a given country.',
    parameters: getCapitalCityParamsSchema,
    execute: getCapitalCity,
});

// Add the tool to the agent
const capitalAgent = new LlmAgent({
    model: 'gemini-flash-latest',
    name: 'capitalAgent',
    description: 'Answers user questions about the capital city of a given country.',
    instruction: 'You are an agent that provides the capital city of a country...', // Note: the full instruction is omitted for brevity
    tools: [getCapitalCityTool], // Provide the FunctionTool instance in an array
});