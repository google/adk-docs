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

import {APP_NAME, runner, TurnText} from './agent.js';

const session = await runner.sessionService.createSession({
  appName: APP_NAME,
  userId: 'user_1',
});

const turn = new TurnText();
let answer = '';

for await (const event of runner.runAsync({
  userId: 'user_1',
  sessionId: session.id,
  newMessage: {role: 'user', parts: [{text: 'Why is the sky blue?'}]},
  // Without this line you get ONE event containing the whole answer.
  runConfig: {streamingMode: StreamingMode.SSE},
})) {
  // Everything not printed yet: the chunk itself, or — before a tool call — the
  // text that only ever arrives in the consolidated event. Never a repeat.
  const text = turn.unshown(event);
  if (text) {
    answer += text;
    process.stdout.write(text);
  }

  // Model failures arrive as events, not thrown exceptions. So does any finish
  // reason other than STOP, which is why this comes after the write: an event
  // that reports MAX_TOKENS also carries the last of the answer.
  if (event.errorCode) {
    const detail = event.errorMessage ? ` ${event.errorMessage}` : '';
    console.error(`\n[${event.errorCode}]${detail}`);
    break;
  }
}

console.log(`\n\n--- ${answer.length} characters ---`);
// --8<-- [end:full]
