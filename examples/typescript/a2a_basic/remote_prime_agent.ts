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
import 'dotenv/config';
import { FunctionTool, LlmAgent, toA2a } from '@google/adk';
import { z } from 'zod';

const PORT = 8001;

const checkPrime = new FunctionTool({
  name: 'check_prime',
  description: 'Checks which numbers in a list are prime.',
  parameters: z.object({
    numbers: z.array(z.number()).describe('The numbers to test for primality.'),
  }),
  execute: ({ numbers }) => {
    const primes = numbers.filter((n) => {
      if (!Number.isInteger(n) || n < 2) return false;
      for (let d = 2; d * d <= n; d++) {
        if (n % d === 0) return false;
      }
      return true;
    });
    console.log(`[server] check_prime(${numbers.join(', ')}) -> ${primes.join(', ') || 'none'}`);
    return { primes };
  },
});

const primeAgent = new LlmAgent({
  name: 'prime_agent',
  model: 'gemini-flash-latest',
  description: 'Checks whether numbers are prime.',
  instruction:
    'You check whether numbers are prime. Always call the check_prime tool, ' +
    'then answer in one short sentence.',
  tools: [checkPrime],
});

// toA2a() returns an Express application. It does NOT start a server.
const app = await toA2a(primeAgent, {
  port: PORT,
  allowUnauthenticated: true, // Local development only.
});

app.listen(PORT, () => {
  console.log(`[server] prime_agent listening on http://localhost:${PORT}`);
  console.log(`[server] agent card: http://localhost:${PORT}/.well-known/agent-card.json`);
});
// --8<-- [end:full]
