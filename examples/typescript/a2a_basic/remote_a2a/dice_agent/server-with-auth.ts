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
import { createHash, timingSafeEqual } from 'node:crypto';
import { FunctionTool, LlmAgent, toA2a } from '@google/adk';
import type { Request } from 'express';
import { z } from 'zod';

const PORT = 8001;

// Read the shared secret from the environment; never hard-code it. Put it in
// .env rather than on the command line: argv is visible to `ps` and lands in
// your shell history.
const EXPECTED_TOKEN = process.env.A2A_SHARED_TOKEN;
if (!EXPECTED_TOKEN) {
  throw new Error('Set A2A_SHARED_TOKEN (e.g. in .env) before starting.');
}

// Compare fixed-length digests, not the strings themselves: timingSafeEqual
// requires equal-length inputs, and a plain `===` on a secret leaks how much
// of it the caller guessed through response timing.
const sha256 = (value: string) => createHash('sha256').update(value).digest();
const EXPECTED_DIGEST = sha256(EXPECTED_TOKEN);

const rollDice = new FunctionTool({
  name: 'roll_dice',
  description: 'Rolls an N-sided die and returns the result.',
  parameters: z.object({
    sides: z.number().describe('The number of sides on the die.'),
  }),
  execute: async ({ sides }) => ({
    result: Math.floor(Math.random() * sides) + 1,
  }),
});

const diceAgent = new LlmAgent({
  name: 'dice_agent',
  model: 'gemini-2.5-flash',
  description: 'An agent that rolls dice on request.',
  instruction:
    'You roll dice for the user. Always use the roll_dice tool. ' +
    'Report the resulting number in one short sentence.',
  tools: [rollDice],
});

// --8<-- [start:auth]
const app = await toA2a(diceAgent, {
  port: PORT,
  // A UserBuilder: (req: express.Request) => Promise<User>. Return a user to
  // accept the request; throw to reject it.
  authentication: async (req: Request) => {
    const header = req.headers.authorization ?? '';
    const token = header.toLowerCase().startsWith('bearer ')
      ? header.slice('bearer '.length)
      : '';
    if (!timingSafeEqual(sha256(token), EXPECTED_DIGEST)) {
      throw new Error('A2A request rejected: bad bearer token.');
    }
    return { isAuthenticated: true, userName: 'a2a-caller' };
  },
});
// --8<-- [end:auth]

app.listen(PORT, () => {
  console.log(`[dice_agent] authenticated A2A server on http://localhost:${PORT}`);
});
// --8<-- [end:full]
