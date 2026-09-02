import {z} from 'zod';
import { Schema, Type } from '@google/genai';

// Define the schema for the output
const CapitalOutputSchema: Schema = {
    type: Type.OBJECT,
    properties: {
        capital: {
            type: Type.STRING,
            description: 'The capital of the country.',
        },
    },
    required: ['capital'],
};

// Create the LlmAgent instance
const structuredCapitalAgent = new LlmAgent({
    // ... name, model, description
    instruction: `You are a Capital Information Agent. Given a country, respond ONLY with a JSON object containing the capital. Format: {"capital": "capital_name"}`,
    outputSchema: CapitalOutputSchema, // Enforce JSON output
    outputKey: 'found_capital', // Store result in state['found_capital']
    // Cannot use tools effectively here
});