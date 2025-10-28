// Copyright 2025 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { LlmAgent, FunctionTool, InMemoryRunner, isFinalResponse } from '@google/adk';
import { createUserContent, Schema, Type } from '@google/genai';
import type { Part } from '@google/genai';
 import { z } from 'zod';

// --- 1. Define Constants ---
const APP_NAME = "capital_app_ts";
const USER_ID = "test_user_789";
const SESSION_ID_TOOL_AGENT = "session_tool_agent_ts";
const SESSION_ID_SCHEMA_AGENT = "session_schema_agent_ts";
const MODEL_NAME = "gemini-2.5-flash"; // Using flash for speed

// --- 2. Define Schemas ---

// A. Schema for the Tool's parameters (using Zod)
const CountryInput = z.object({
    country: z.string().describe('The country to get the capital for.'),
});

// B. Output schema ONLY for the second agent (using ADK's Schema type)
const CapitalInfoOutputSchema: Schema = {
    type: Type.OBJECT,
    description: "Schema for capital city information.",
    properties: {
        capital: {
            type: Type.STRING,
            description: "The capital city of the country."
        },
        population_estimate: {
            type: Type.STRING,
            description: "An estimated population of the capital city."
        },
    },
    required: ["capital", "population_estimate"],
};


// --- 3. Define the Tool (Only for the first agent) ---
async function getCapitalCity(params: z.infer<typeof CountryInput>): Promise<{ result: string }> {
    console.log(`\n-- Tool Call: getCapitalCity(country='${params.country}') --`);
    const capitals: Record<string, string> = {
        'united states': 'Washington, D.C.',
        'canada': 'Ottawa',
        'france': 'Paris',
        'japan': 'Tokyo',
    };
    const result = capitals[params.country.toLowerCase()] ??
        `Sorry, I couldn't find the capital for ${params.country}.`;
    console.log(`-- Tool Result: '${result}' --`);
    return { result: result }; // Tools must return an object
}

// --- 4. Configure Agents ---

// Agent 1: Uses a tool and outputKey
const getCapitalCityTool = new FunctionTool({
    name: 'get_capital_city',
    description: 'Retrieves the capital city for a given country',
    parameters: CountryInput,
    execute: getCapitalCity,
});

const capitalAgentWithTool = new LlmAgent({
    model: MODEL_NAME,
    name: 'capital_agent_tool',
    description: 'Retrieves the capital city using a specific tool.',
    instruction: `You are a helpful agent that provides the capital city of a country using a tool.
The user will provide the country name in a JSON format like {"country": "country_name"}.
1. Extract the country name.
2. Use the \`get_capital_city\` tool to find the capital.
3. Respond with a JSON object with the key 'capital' and the value as the capital city.
`,
    tools: [getCapitalCityTool],
    outputKey: "capital_tool_result", // Store final text response
});

// Agent 2: Uses outputSchema (NO tools possible)
const structuredInfoAgentSchema = new LlmAgent({
    model: MODEL_NAME,
    name: 'structured_info_agent_schema',
    description: 'Provides capital and estimated population in a specific JSON format.',
    instruction: `You are an agent that provides country information.
The user will provide the country name in a JSON format like {"country": "country_name"}.
Respond ONLY with a JSON object matching this exact schema:
${JSON.stringify(CapitalInfoOutputSchema, null, 2)}
Use your knowledge to determine the capital and estimate the population. Do not use any tools.
`,
    // *** NO tools parameter here - using outputSchema prevents tool use ***
    outputSchema: CapitalInfoOutputSchema,
    outputKey: "structured_info_result",
});


// --- 5. Define Agent Interaction Logic ---
async function callAgentAndPrint(
    runner: InMemoryRunner,
    agent: LlmAgent,
    sessionId: string,
    queryJson: string
) {
    console.log(`\n>>> Calling Agent: '${agent.name}' | Query: ${queryJson}`);
    const message = createUserContent(queryJson);

    let finalResponseContent = "No final response received.";
    for await (const event of runner.runAsync({ userId: USER_ID, sessionId: sessionId, newMessage: message })) {
        if (isFinalResponse(event) && event.content?.parts?.length) {
            finalResponseContent = event.content.parts.map((part: Part) => part.text ?? '').join('');
        }
    }
    console.log(`<<< Agent '${agent.name}' Response: ${finalResponseContent}`);

    // Check the session state
    const currentSession = await runner.sessionService.getSession({ appName: APP_NAME, userId: USER_ID, sessionId: sessionId });
    if (!currentSession) {
        console.log(`--- Session not found: ${sessionId} ---`);
        return;
    }
    const storedOutput = currentSession.state[agent.outputKey!];

    console.log(`--- Session State ['${agent.outputKey}']: `);
    try {
        // Attempt to parse and pretty print if it's JSON
        const parsedOutput = JSON.parse(storedOutput as string);
        console.log(JSON.stringify(parsedOutput, null, 2));
    } catch (e) {
        // Otherwise, print as a string
        console.log(storedOutput);
    }
    console.log("-".repeat(30));
}

// --- 6. Run Interactions ---
async function main() {
    // Set up runners for each agent
    const capitalRunner = new InMemoryRunner({ appName: APP_NAME, agent: capitalAgentWithTool });
    const structuredRunner = new InMemoryRunner({ appName: APP_NAME, agent: structuredInfoAgentSchema });

    // Create sessions
    console.log("--- Creating Sessions ---");
    await capitalRunner.sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: SESSION_ID_TOOL_AGENT });
    await structuredRunner.sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: SESSION_ID_SCHEMA_AGENT });

    console.log("\n--- Testing Agent with Tool ---");
    await callAgentAndPrint(capitalRunner, capitalAgentWithTool, SESSION_ID_TOOL_AGENT, '{"country": "France"}');
    await callAgentAndPrint(capitalRunner, capitalAgentWithTool, SESSION_ID_TOOL_AGENT, '{"country": "Canada"}');

    console.log("\n\n--- Testing Agent with Output Schema (No Tool Use) ---");
    await callAgentAndPrint(structuredRunner, structuredInfoAgentSchema, SESSION_ID_SCHEMA_AGENT, '{"country": "France"}');
    await callAgentAndPrint(structuredRunner, structuredInfoAgentSchema, SESSION_ID_SCHEMA_AGENT, '{"country": "Japan"}');
}

main();