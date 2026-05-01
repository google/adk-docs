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

// --8<-- [start:config]
import {
  BaseAgent,
  InvocationContext,
  LlmAgent,
  RoutedAgent,
  InMemoryRunner,
} from '@google/adk';

const primaryAgent = new LlmAgent({
  name: 'primary',
  model: 'gemini-flash-latest',
  instruction: 'You are the primary agent.',
});

const fallbackAgent = new LlmAgent({
  name: 'fallback',
  model: 'gemini-pro-latest',
  instruction: 'You are the fallback agent.',
});

const router = (
  agents: Readonly<Record<string, BaseAgent>>,
  context: InvocationContext,
  // errorContext is provided when a previously selected agent fails
  errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
) => {
  if (!errorContext) {
    return 'primary'; // Try primary first
  }
  if (errorContext.failedKeys.has('primary')) {
    return 'fallback'; // Fall back if primary failed
  }
  return undefined; // No more options, propagate the error
};

const routedAgent = new RoutedAgent({
  name: 'my_routed_agent',
  agents: { primary: primaryAgent, fallback: fallbackAgent },
  router,
});
// --8<-- [end:config]

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
