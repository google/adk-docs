/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {FunctionTool, LlmAgent} from '@google/adk';
import {RemoteA2AAgent} from '@google/adk/a2a';
import {z} from 'zod';

const rollDieTool = new FunctionTool({
  name: 'roll_die',
  description: 'Rolls a die with the specified number of sides.',
  parameters: z.object({
    sides: z.number().int().min(1).describe('The number of sides on the die.'),
  }),
  execute: ({sides}) => {
    return {result: Math.floor(Math.random() * sides) + 1};
  },
});

const rollAgent = new LlmAgent({
  name: 'roll_agent',
  model: 'gemini-flash-latest',
  description: 'Handles rolling dice of different sizes.',
  instruction:
    'You are responsible for rolling dice based on the user request. Call the roll_die tool with the number of sides as an integer.',
  tools: [rollDieTool],
});

// --8<-- [start:remote_agent]
const primeAgent = new RemoteA2AAgent({
  name: 'prime_agent',
  description: 'Agent that handles checking if numbers are prime.',
  agentCard: 'http://localhost:8001/a2a/check_prime_agent/',
});
// --8<-- [end:remote_agent]

// --8<-- [start:root_agent]
export const rootAgent = new LlmAgent({
  name: 'root_agent',
  model: 'gemini-flash-latest',
  description:
    'Assistant that rolls dice locally and delegates prime number checks to a remote A2A agent.',
  instruction: `You are DicePrimeBot, a helpful assistant that can roll dice and check if numbers are prime.
You delegate rolling dice tasks to roll_agent and prime checking tasks to prime_agent.
Follow these steps:
1. If the user asks to roll a die, delegate to roll_agent.
2. If the user asks to check primes, delegate to prime_agent.
3. If the user asks to roll a die and then check if the result is prime, call roll_agent first, then pass the result to prime_agent.
Always clarify the results before proceeding.`,
  subAgents: [rollAgent, primeAgent],
});
// --8<-- [end:root_agent]
