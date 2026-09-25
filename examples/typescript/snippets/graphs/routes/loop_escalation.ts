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

// A loop is a BACK-EDGE in the graph: a downstream node routes back to an
// earlier node, and the engine re-activates that node with a fresh lifecycle on
// each iteration. The loop exits when the router picks the terminal branch.
//
//   START -> seed_draft -> critic -> router --REVISE--> refine --+
//                             ^                                  |
//                             +----------------------------------+
//                                        router --DONE--> finalize

// --8<-- [start:loop-escalation]
import { createEvent, node, NodeContext, Workflow } from '@google/adk';

interface Draft {
  topic: string;
  bullets: string[];
}

/** The critic is satisfied once the draft has at least this many bullets. */
const REQUIRED_BULLETS = 3;

const seedDraft = node(
  (_ctx: NodeContext, topic: string): Draft => ({
    topic: topic.trim(),
    bullets: [`${topic.trim()} — point 1`],
  }),
  { name: 'seed_draft' },
);

const critic = node(
  (_ctx: NodeContext, draft: Draft) =>
    createEvent({
      route: draft.bullets.length >= REQUIRED_BULLETS ? 'DONE' : 'REVISE',
      output: draft,
    }),
  { name: 'critic' },
);

const refine = node(
  (_ctx: NodeContext, draft: Draft): Draft => ({
    ...draft,
    bullets: [
      ...draft.bullets,
      `${draft.topic} — point ${draft.bullets.length + 1}`,
    ],
  }),
  { name: 'refine' },
);

const finalize = node(
  (_ctx: NodeContext, draft: Draft) =>
    `Approved after ${draft.bullets.length} bullets:\n` +
    draft.bullets.map((b) => `  • ${b}`).join('\n'),
  { name: 'finalize' },
);

export const rootAgent = new Workflow({
  name: 'loop_workflow',
  edges: [
    ['START', seedDraft, critic],
    [critic, { REVISE: refine, DONE: finalize }],
    [refine, critic],
  ],
});
// --8<-- [end:loop-escalation]
