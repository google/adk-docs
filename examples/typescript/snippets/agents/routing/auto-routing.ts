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
  Gemini,
  InvocationContext,
  LlmAgent,
  RoutedAgent,
  InMemoryRunner,
} from '@google/adk';

const simpleAgent = new LlmAgent({
  name: 'simple',
  model: 'gemini-flash-latest',
  instruction: 'You are a simple assistant for basic questions.',
});

const complexAgent = new LlmAgent({
  name: 'complex',
  model: 'gemini-pro-latest',
  instruction: 'You are an expert assistant for complex analysis.',
});

// Lightweight model to classify input complexity
const classifierModel = new Gemini({ model: 'gemini-flash-latest' });

const router = async (
  agents: Readonly<Record<string, BaseAgent>>,
  context: InvocationContext,
) => {
  // Extract the user's input text
  const text = context.userContent?.parts?.[0]?.text || '';
  if (!text) return 'simple';

  const prompt =
    `Classify this request as 'simple' or 'complex'. ` +
    `Reply with ONLY that word.\nRequest: "${text}"`;

  const generator = classifierModel.generateContentAsync({
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    toolsDict: {},
    liveConnectConfig: {},
  });

  let classification = '';
  for await (const resp of generator) {
    if (resp.content?.parts?.[0]?.text) {
      classification += resp.content.parts[0].text;
    }
  }

  return classification.toLowerCase().includes('complex')
    ? 'complex'
    : 'simple';
};

const routedAgent = new RoutedAgent({
  name: 'my_routed_agent',
  agents: { simple: simpleAgent, complex: complexAgent },
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
  newMessage: { role: 'user', parts: [{ text: 'What is 1+1?' }] },
});

for await (const event of run) {
  if (event.content?.parts?.[0]?.text) {
    console.log(event.content.parts[0].text);
  }
}
