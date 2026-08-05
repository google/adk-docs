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
import {InMemoryRunner, LlmAgent, StreamingMode} from '@google/adk';
import type {Event} from '@google/adk';

const agent = new LlmAgent({
  name: 'explainer',
  model: 'gemini-2.5-flash',
  description: 'Explains things clearly and at length.',
  instruction: 'You are a patient explainer. Answer in three short paragraphs.',
});

const runner = new InMemoryRunner({appName: 'streaming_quickstart', agent});
const session = await runner.sessionService.createSession({
  appName: 'streaming_quickstart',
  userId: 'user_1',
});

/** Joins the answer text in an event, skipping tool calls and reasoning. */
function textOf(event: Event): string {
  return (event.content?.parts ?? [])
    .filter((part) => part.text && !part.thought)
    .map((part) => part.text)
    .join('');
}

let answer = '';

for await (const event of runner.runAsync({
  userId: 'user_1',
  sessionId: session.id,
  newMessage: {role: 'user', parts: [{text: 'Why is the sky blue?'}]},
  // Without this line you get ONE event containing the whole answer.
  runConfig: {streamingMode: StreamingMode.SSE},
})) {
  // Model failures arrive as events, not thrown exceptions.
  if (event.errorCode) {
    console.error(`\n[${event.errorCode}] ${event.errorMessage}`);
    break;
  }

  const text = textOf(event);
  if (!text) continue;

  if (event.partial) {
    // An incremental chunk: append it.
    answer += text;
    process.stdout.write(text);
  } else {
    // The last event repeats the WHOLE answer. Replace, never append.
    answer = text;
  }
}

console.log(`\n\n--- ${answer.length} characters ---`);
// --8<-- [end:full]
