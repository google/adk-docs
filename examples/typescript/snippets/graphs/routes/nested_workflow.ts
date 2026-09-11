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

// A `Workflow` is itself a node, so you can use one inside another workflow's
// edges to encapsulate a reusable sub-process.

// --8<-- [start:nested-workflow]
import { createEvent, node, NodeContext, Workflow } from '@google/adk';

const taskA1 = node(
  (_ctx: NodeContext, nodeInput: string) => nodeInput.trim(),
  {
    name: 'task_A1',
  },
);

const router = node(
  (_ctx: NodeContext, text: string) =>
    createEvent({
      route: text === text.toUpperCase() ? 'RUN_WORKFLOW_C' : 'RUN_WORKFLOW_B',
      output: text,
    }),
  { name: 'router' },
);

/**
 * Upper-cases the first letter of each word.
 *
 * Unicode-aware on purpose: `\b\w` is ASCII-only, so `ü` never matches — and
 * the word boundary it creates before the *next* ASCII letter upper-cases that
 * one instead ("strässe" -> "SträSse"). A letter whose uppercase form is more
 * than one code point (German `ß` -> "SS") is left alone rather than mangled.
 */
const titleCase = (text: string) =>
  text.replace(/(^|\P{L})(\p{L})/gu, (_match, sep: string, ch: string) => {
    const upper = ch.toUpperCase();
    return sep + ([...upper].length === 1 ? upper : ch);
  });

const workflowB = new Workflow({
  name: 'workflow_B',
  edges: [
    [
      'START',
      node((_ctx: NodeContext, text: string) => titleCase(text), {
        name: 'b_title_case',
      }),
      node((_ctx: NodeContext, text: string) => `[B] ${text}`, {
        name: 'b_frame',
      }),
    ],
  ],
});

const workflowC = new Workflow({
  name: 'workflow_C',
  edges: [
    [
      'START',
      node((_ctx: NodeContext, text: string) => text.toLowerCase(), {
        name: 'c_lower_case',
      }),
      node((_ctx: NodeContext, text: string) => `[C] ${text}`, {
        name: 'c_frame',
      }),
    ],
  ],
});

export const rootAgent = new Workflow({
  name: 'parent_workflow',
  edges: [
    ['START', taskA1, router],
    [
      router,
      {
        RUN_WORKFLOW_B: workflowB,
        RUN_WORKFLOW_C: workflowC,
      },
    ],
  ],
});
// --8<-- [end:nested-workflow]
