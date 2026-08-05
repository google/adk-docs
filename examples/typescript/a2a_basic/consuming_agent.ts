// Copyright 2026 Google LLC
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

// --8<-- [start:imports]
import 'dotenv/config';
import {
  FunctionTool,
  InMemorySessionService,
  LlmAgent,
  RemoteA2AAgent,
  Runner,
} from '@google/adk';
import { z } from 'zod';
// --8<-- [end:imports]

const APP_NAME = 'a2a_basic';
const USER_ID = 'user_1';

// --8<-- [start:roll-agent]
const rollDie = new FunctionTool({
  name: 'roll_die',
  description: 'Rolls an N-sided die and returns the result.',
  parameters: z.object({
    sides: z.number().describe('The number of sides on the die.'),
  }),
  execute: ({ sides }) => ({ result: Math.floor(Math.random() * sides) + 1 }),
});

const rollAgent = new LlmAgent({
  name: 'roll_agent',
  model: 'gemini-2.5-flash',
  description: 'Rolls dice of any size.',
  instruction: 'You roll dice. Always call the roll_die tool, then report the number.',
  tools: [rollDie],
});
// --8<-- [end:roll-agent]

// --8<-- [start:remote-agent]
const primeAgent = new RemoteA2AAgent({
  name: 'prime_agent',
  description: 'Checks whether numbers are prime. Use this for any primality question.',
  agentCard: 'http://localhost:8001',
});
// --8<-- [end:remote-agent]

// --8<-- [start:root-agent]
const rootAgent = new LlmAgent({
  name: 'root_agent',
  model: 'gemini-2.5-flash',
  description: 'Rolls dice and checks primes by delegating to specialist agents.',
  instruction: `You coordinate two specialists.
Delegate any dice rolling to roll_agent.
Delegate any question about whether a number is prime to prime_agent.
If the user asks for both, roll first, then pass the rolled number to prime_agent.`,
  subAgents: [rollAgent, primeAgent],
});
// --8<-- [end:root-agent]

// --8<-- [start:run]
const sessionService = new InMemorySessionService();
const runner = new Runner({
  appName: APP_NAME,
  agent: rootAgent,
  sessionService,
});
const session = await sessionService.createSession({
  appName: APP_NAME,
  userId: USER_ID,
});

const prompt = 'Roll a 6-sided die and tell me whether the result is prime.';
console.log(`user > ${prompt}`);

for await (const event of runner.runAsync({
  userId: USER_ID,
  sessionId: session.id,
  newMessage: { role: 'user', parts: [{ text: prompt }] },
})) {
  // Failures on the remote side arrive as an event, not as a thrown error.
  if (event.errorMessage) {
    console.error(`[error] ${event.author}: ${event.errorMessage}`);
    continue;
  }
  // Skip the streamed chunks so each completed answer prints once.
  if (event.partial) continue;
  for (const part of event.content?.parts ?? []) {
    if (part.functionCall) {
      console.log(
        `${event.author} calls ${part.functionCall.name}(${JSON.stringify(part.functionCall.args)})`,
      );
    }
    if (part.text) {
      console.log(`${event.author} > ${part.text}`);
    }
  }
}
// --8<-- [end:run]
