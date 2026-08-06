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

import {APP_NAME, runner, TurnText} from './agent.js';

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

  const turn = new TurnText();

  try {
    for await (const event of runner.runAsync({
      userId,
      sessionId,
      newMessage: {role: 'user', parts: [{text: message}]},
      // Without this line the browser gets the whole answer in one frame.
      runConfig: {streamingMode: StreamingMode.SSE},
      abortSignal: abortController.signal,
    })) {
      // Forward what the browser has not seen: the chunk itself, or — before a
      // tool call — the text that only the consolidated event carries. The
      // repeated part of that event is never forwarded, so nothing renders
      // twice.
      const delta = turn.unshown(event);
      if (delta) send({delta});

      // After the write, because the event that reports a finish reason other
      // than STOP also carries the last of the answer. errorMessage may be
      // absent; `[MAX_TOKENS] undefined` in the UI helps nobody.
      if (event.errorCode) {
        const detail = event.errorMessage ? ` ${event.errorMessage}` : '';
        send({error: `[${event.errorCode}]${detail}`});
        break;
      }
    }
    send({done: true});
  } catch (err) {
    send({error: String(err)});
  } finally {
    res.end();
  }
});

const port = Number(process.env.PORT ?? 3000);
const server = app.listen(port);

server.on('listening', () => {
  console.log(`Open http://localhost:${port}`);
});

// Do not skip this. Express 5 registers the app.listen() success callback as an
// 'error' listener too, so the obvious one-liner prints "Open http://..." and
// exits 0 when the port is busy — a failure that looks exactly like a success.
server.on('error', (err: NodeJS.ErrnoException) => {
  console.error(
    err.code === 'EADDRINUSE'
      ? `Port ${port} is already in use. Free it, or run PORT=3100 npm start.`
      : `Could not start the server: ${err.message}`,
  );
  process.exit(1);
});
// --8<-- [end:full]
