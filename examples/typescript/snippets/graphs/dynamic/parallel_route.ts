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

// `ctx.runNode()` returns a promise, so starting every child before awaiting any
// of them runs them concurrently, and `Promise.all` gathers the results.
//
// Prefer the built-in when the shape is "map one node over a list":
//   node(worker, {parallelWorker: true, maxParallelWorkers: 4})
// It does the fan-out for you and bounds concurrency (default 8). Hand-rolling
// it, as below, is for when you need custom scheduling or partial-failure
// handling.

// --8<-- [start:parallel-route]
import { node, NodeContext, Workflow } from '@google/adk';

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/** The worker run once per list item. */
const realNode = node(
  async (_ctx: NodeContext, item: string) => {
    await sleep(200);
    return { item, length: item.length };
  },
  { name: 'analyze_item' },
);

const parallelSupervisor = node(
  async (ctx: NodeContext, nodeInput: string) => {
    const items = nodeInput
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);

    const tasks = items.map((item) => ctx.runNode(realNode, item));
    const results = await Promise.all(tasks);

    return results.map((result) => result.output);
  },
  { name: 'parallel_supervisor', rerunOnResume: true },
);

const summarize = node(
  (_ctx: NodeContext, results: Array<{ item: string; length: number }>) =>
    results.map((r) => `${r.item}: ${r.length} chars`).join('\n'),
  { name: 'summarize' },
);

export const rootAgent = new Workflow({
  name: 'root_agent',
  edges: [['START', parallelSupervisor, summarize]],
});
// --8<-- [end:parallel-route]
