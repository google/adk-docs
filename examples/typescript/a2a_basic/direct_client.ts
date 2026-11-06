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
import { InMemorySessionService, RemoteA2AAgent, Runner } from '@google/adk';

const APP_NAME = 'prime_client';
const USER_ID = 'user_1';

// --8<-- [start:remote-agent]
const primeAgent = new RemoteA2AAgent({
  name: 'prime_agent',
  description: 'Remote agent that checks whether numbers are prime.',
  // A BASE URL, not the card URL. RemoteA2AAgent appends
  // ".well-known/agent-card.json" itself.
  agentCard: 'http://localhost:8001',
});
// --8<-- [end:remote-agent]

const sessionService = new InMemorySessionService();
const runner = new Runner({
  appName: APP_NAME,
  agent: primeAgent,
  sessionService,
});
const session = await sessionService.createSession({
  appName: APP_NAME,
  userId: USER_ID,
});

console.log('user > Is 7 a prime number?');
// --8<-- [start:event-loop]
for await (const event of runner.runAsync({
  userId: USER_ID,
  sessionId: session.id,
  newMessage: { role: 'user', parts: [{ text: 'Is 7 a prime number?' }] },
})) {
  // Failures on the remote side arrive as an event, not as a thrown error.
  if (event.errorMessage) {
    console.error(`[error] ${event.author}: ${event.errorMessage}`);
    continue;
  }
  // Skip the streamed chunks so the completed answer prints once.
  if (event.partial) continue;
  for (const part of event.content?.parts ?? []) {
    if (part.text) console.log(`${event.author} > ${part.text}`);
  }
}
// --8<-- [end:event-loop]
// --8<-- [end:full]
