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

// A node takes an explicit `(ctx, input)` pair and reads and writes session
// state through `ctx.state`. A write is visible to every later node in the same
// run, and is committed with the writing node's events.

// --8<-- [start:session-state]
import { node, NodeContext, Workflow } from '@google/adk';

const initStateNode = node(
  (ctx: NodeContext, nodeInput: string) => {
    ctx.state.set('topic', nodeInput.trim());
    ctx.state.set('temp:started_at', new Date().toISOString());
    ctx.state.set('attempts', 0);
  },
  { name: 'init_state_node' },
);

const taskAttemptNode = node(
  (ctx: NodeContext) => {
    const attempts = ctx.state.get<number>('attempts') ?? 0;
    ctx.state.set('attempts', attempts + 1);
  },
  { name: 'task_attempt_node' },
);

const readStateNode = node(
  (ctx: NodeContext) =>
    `attempts state: ${ctx.state.get('attempts')} ` +
    `(topic: ${ctx.state.get('topic')}, ` +
    `started: ${ctx.state.get('temp:started_at')})`,
  { name: 'read_state_node' },
);

export const rootAgent = new Workflow({
  name: 'session_state_workflow',
  edges: [['START', initStateNode, taskAttemptNode, readStateNode]],
});
// --8<-- [end:session-state]
