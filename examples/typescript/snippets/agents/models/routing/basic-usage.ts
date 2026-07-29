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
import {
  BaseLlm,
  Gemini,
  LlmRequest,
  LlmAgent,
  RoutedLlm,
  InMemoryRunner,
} from '@google/adk';

const primaryModel = new Gemini({ model: 'gemini-flash-latest' });
const fallbackModel = new Gemini({ model: 'gemini-pro-latest' });

const router = (
  models: Readonly<Record<string, BaseLlm>>,
  request: LlmRequest,
  // errorContext is provided when a previously selected model fails
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

const routedLlm = new RoutedLlm({
  models: { primary: primaryModel, fallback: fallbackModel },
  router,
});

// Use RoutedLlm as the model for an LlmAgent
const agent = new LlmAgent({
  name: 'my_agent',
  model: routedLlm,
  instruction: 'You are a helpful assistant.',
});

const runner = new InMemoryRunner({ agent, appName: 'my_app' });

const session = await runner.sessionService.createSession({
  appName: 'my_app',
  userId: 'user_1',
});

const run = runner.runAsync({
  userId: 'user_1',
  sessionId: session.id,
  newMessage: { role: 'user', parts: [{ text: 'Hello!' }] },
});

for await (const event of run) {
  if (event.content?.parts?.[0]?.text) {
    console.log(event.content.parts[0].text);
  }
}
// --8<-- [end:full]
