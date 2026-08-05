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
import {StreamingMode} from '@google/adk';

import {APP_NAME, runner, textOf} from './agent.js';

const session = await runner.sessionService.createSession({
  appName: APP_NAME,
  userId: 'user_1',
});

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
