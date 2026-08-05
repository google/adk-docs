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
import express from 'express';
import type {Request, Response} from 'express';

import {APP_NAME, runner, textOf} from './agent.js';

const app = express();
app.use(express.json());
app.use(express.static('public'));

app.post('/api/chat', async (req: Request, res: Response) => {
  const {userId, sessionId, message} = req.body as {
    userId: string;
    sessionId: string;
    message: string;
  };

  // runAsync needs a session that already exists.
  const existing = await runner.sessionService.getSession({
    appName: APP_NAME,
    userId,
    sessionId,
  });
  if (!existing) {
    await runner.sessionService.createSession({
      appName: APP_NAME,
      userId,
      sessionId,
    });
  }

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('X-Accel-Buffering', 'no');
  res.flushHeaders(); // Without this, Node buffers and nothing arrives early.

  // Stop generating (and billing) when the browser tab goes away.
  const abortController = new AbortController();
  res.on('close', () => abortController.abort());

  const send = (payload: unknown) =>
    res.write(`data: ${JSON.stringify(payload)}\n\n`);

  try {
    for await (const event of runner.runAsync({
      userId,
      sessionId,
      newMessage: {role: 'user', parts: [{text: message}]},
      // Without this line the browser gets the whole answer in one frame.
      runConfig: {streamingMode: StreamingMode.SSE},
      abortSignal: abortController.signal,
    })) {
      if (event.errorCode) {
        send({error: `[${event.errorCode}] ${event.errorMessage}`});
        break;
      }

      const text = textOf(event);
      if (!text) continue;

      // Forward deltas only. The last event repeats the whole answer, so
      // forwarding it too would render the answer twice in the browser.
      if (event.partial) send({delta: text});
    }
    send({done: true});
  } catch (err) {
    send({error: String(err)});
  } finally {
    res.end();
  }
});

const port = Number(process.env.PORT ?? 3000);
app.listen(port, () => {
  console.log(`Open http://localhost:${port}`);
});
// --8<-- [end:full]
