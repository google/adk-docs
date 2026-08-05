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

// --8<-- [start:full]
import { FunctionTool, LlmAgent, toA2a } from '@google/adk';
import { z } from 'zod';

// The port must match the `port` passed to toA2a() below.
const PORT = 8001;

// --8<-- [start:tool]
const rollDice = new FunctionTool({
  name: 'roll_dice',
  description: 'Rolls an N-sided die and returns the result.',
  parameters: z.object({
    sides: z.number().describe('The number of sides on the die.'),
  }),
  execute: async ({ sides }) => {
    const value = Math.floor(Math.random() * sides) + 1;
    console.log(`[dice_agent] roll_dice(sides=${sides}) -> ${value}`);
    return { result: value };
  },
});
// --8<-- [end:tool]

// --8<-- [start:agent]
const diceAgent = new LlmAgent({
  name: 'dice_agent',
  model: 'gemini-2.5-flash',
  description: 'An agent that rolls dice on request.',
  instruction:
    'You roll dice for the user. Always use the roll_dice tool. ' +
    'Report the resulting number in one short sentence.',
  tools: [rollDice],
});
// --8<-- [end:agent]

// --8<-- [start:expose]
const app = await toA2a(diceAgent, {
  // `port` only writes the URL into the agent card. It does not open a socket,
  // so it has to agree with the port passed to app.listen() below.
  port: PORT,
  // Local development only. Remove this and pass `authentication` instead
  // before you put the agent on a network anyone else can reach.
  allowUnauthenticated: true,
});

// toA2a() hands back an Express application that is not listening yet.
app.listen(PORT, () => {
  console.log(`[dice_agent] A2A server listening on http://localhost:${PORT}`);
  console.log(
    `[dice_agent] agent card: http://localhost:${PORT}/.well-known/agent-card.json`,
  );
});
// --8<-- [end:expose]
// --8<-- [end:full]
