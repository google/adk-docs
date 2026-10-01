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
import { LlmAgent, RoutedAgent, InMemoryRunner } from '@google/adk';

const agentA = new LlmAgent({
  name: 'agent_a',
  model: 'gemini-flash-latest',
  instruction: 'You are Agent A. Always identify yourself as Agent A.',
});

const agentB = new LlmAgent({
  name: 'agent_b',
  model: 'gemini-flash-latest',
  instruction: 'You are Agent B. Always identify yourself as Agent B.',
});

// External configuration that can change at runtime
const config = { selectedAgent: 'agent_a' };

const routedAgent = new RoutedAgent({
  name: 'my_routed_agent',
  agents: { agent_a: agentA, agent_b: agentB },
  router: () => config.selectedAgent,
});

const runner = new InMemoryRunner({
  agent: routedAgent,
  appName: 'my_app',
});

const session = await runner.sessionService.createSession({
  appName: 'my_app',
  userId: 'user_1',
});

const run = runner.runAsync({
  userId: 'user_1',
  sessionId: session.id,
  newMessage: { role: 'user', parts: [{ text: 'Who are you?' }] },
});

for await (const event of run) {
  if (event.content?.parts?.[0]?.text) {
    console.log(event.content.parts[0].text);
  }
}
// --8<-- [end:full]
