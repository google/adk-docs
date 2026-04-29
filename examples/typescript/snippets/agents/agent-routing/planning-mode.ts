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
  FunctionTool,
  LlmAgent,
  RoutedAgent,
  InMemoryRunner,
} from '@google/adk';
import { z } from 'zod';

const readFileTool = new FunctionTool({
  name: 'read_file',
  description: 'Reads content from a file.',
  parameters: z.object({ filePath: z.string() }),
  execute: (args) => ({ content: `Contents of ${args.filePath}` }),
});

const writeFileTool = new FunctionTool({
  name: 'write_file',
  description: 'Writes content to a file.',
  parameters: z.object({ filePath: z.string(), content: z.string() }),
  execute: (args) => ({ result: `Wrote to ${args.filePath}` }),
});

const basicAgent = new LlmAgent({
  name: 'basic',
  model: 'gemini-flash-latest',
  instruction: 'You are a basic assistant. Use tools to help the user.',
  tools: [readFileTool, writeFileTool],
});

const planningAgent = new LlmAgent({
  name: 'planning',
  model: 'gemini-flash-latest',
  instruction: 'You are a planning expert. Analyze carefully. You can only read files.',
  tools: [readFileTool],
});

// Toggle this to switch between basic and planning agents
let planningMode = false;

const routedAgent = new RoutedAgent({
  name: 'my_routed_agent',
  agents: { basic: basicAgent, planning: planningAgent },
  router: () => (planningMode ? 'planning' : 'basic'),
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
  newMessage: { role: 'user', parts: [{ text: 'Read the file report.txt' }] },
});

for await (const event of run) {
  if (event.content?.parts?.[0]?.text) {
    console.log(event.content.parts[0].text);
  }
}
