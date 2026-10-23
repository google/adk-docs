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

// A prompt-based agent turned into a graph: one agent classifies the message,
// a router node emits the categories as routes, and the graph dispatches to the
// matching handler(s). Because the classifier may return more than one
// category, the router emits an ARRAY of routes — every matching branch fires.

// --8<-- [start:process-pipeline]
import {
  createEvent,
  DEFAULT_ROUTE,
  LlmAgent,
  node,
  NodeContext,
  Workflow,
} from '@google/adk';

/** The routes this graph has edges for. */
const ROUTES = ['BUG', 'CUSTOMER_SUPPORT', 'LOGISTICS'] as const;

const processMessage = new LlmAgent({
  name: 'process_message',
  model: 'gemini-flash-latest',
  instruction: `Classify user message into either "BUG", "CUSTOMER_SUPPORT",
      or "LOGISTICS". If you think a message applies to more than one category,
      reply with a comma separated list of categories.
      Reply with the categories only, nothing else.`,
});

const router = node(
  (_ctx: NodeContext, nodeInput: string) => {
    const text = String(nodeInput).toUpperCase();
    const matched = ROUTES.filter((route) =>
      new RegExp(`\\b${route}\\b`).test(text),
    );
    return createEvent({ route: matched.length > 0 ? matched : DEFAULT_ROUTE });
  },
  { name: 'router' },
);

/** Emits a user-facing message: `content`, with no `output`. */
const message = (text: string) =>
  createEvent({ content: { role: 'model', parts: [{ text }] } });

const response1Bug = node(() => message('Handling bug...'), {
  name: 'response_1_bug',
});
const response2Support = node(() => message('Handling customer support...'), {
  name: 'response_2_support',
});
const response3Logistics = node(() => message('Handling logistics...'), {
  name: 'response_3_logistics',
});
const responseUnknown = node(
  (_ctx: NodeContext, nodeInput: string) =>
    message(`Could not classify that (classifier said: ${nodeInput}).`),
  { name: 'response_unknown' },
);

export const rootAgent = new Workflow({
  name: 'routing_workflow',
  edges: [
    ['START', processMessage, router],
    [
      router,
      {
        BUG: response1Bug,
        CUSTOMER_SUPPORT: response2Support,
        LOGISTICS: response3Logistics,
        [DEFAULT_ROUTE]: responseUnknown,
      },
    ],
  ],
});
// --8<-- [end:process-pipeline]
