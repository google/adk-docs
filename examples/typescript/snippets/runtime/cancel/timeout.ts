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

import { Runner, InMemorySessionService, LlmAgent, FunctionTool } from '@google/adk';
import { z } from 'zod';

const getInfo = new FunctionTool({
  name: 'get_info',
  description: 'Gets information about a topic.',
  parameters: z.object({ topic: z.string() }),
  execute: (args) => ({ result: `Info about ${args.topic}` }),
});

const agent = new LlmAgent({
  name: 'my_agent',
  model: 'gemini-flash-latest',
  instruction: 'Always use the get_info tool before answering.',
  tools: [getInfo],
});

const sessionService = new InMemorySessionService();
const runner = new Runner({ agent, appName: 'my_app', sessionService });
const session = await sessionService.createSession({ appName: 'my_app', userId: 'user_1' });

// --8<-- [start:run]
const run = runner.runAsync({
  userId: session.userId,
  sessionId: session.id,
  newMessage: { role: 'user', parts: [{ text: 'Tell me about quantum computing.' }] },
  abortSignal: AbortSignal.timeout(2_000), // Cancel after 2 seconds
});

let count = 0;
for await (const event of run) {
  count++;
  console.log('Event:', event.author);
}
console.log(`Done. Received ${count} event(s).`);
// --8<-- [end:run]
