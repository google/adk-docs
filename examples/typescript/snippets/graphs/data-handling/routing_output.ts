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

// `route` drives conditional edge dispatch. It is independent of `output`, so a
// router can select a branch AND forward a payload in the same event.

// --8<-- [start:routing-output]
import {
  createEvent,
  DEFAULT_ROUTE,
  node,
  NodeContext,
  Workflow,
} from "@google/adk";

const router = node(
  (_ctx: NodeContext, nodeInput: string) =>
    createEvent({
      route: /bug|crash|error/i.test(nodeInput) ? "BUG" : "OTHER",
      output: nodeInput,
    }),
  { name: "router" },
);

const handleBug = node(
  (_ctx: NodeContext, nodeInput: string) => `Filed a bug for: ${nodeInput}`,
  { name: "handle_bug" },
);

const handleAnythingElse = node(
  (_ctx: NodeContext, nodeInput: string) => `No bug detected in: ${nodeInput}`,
  { name: "handle_anything_else" },
);

export const rootAgent = new Workflow({
  name: "routing_output_workflow",
  edges: [
    ["START", router],
    [
      router,
      {
        BUG: handleBug,
        [DEFAULT_ROUTE]: handleAnythingElse,
      },
    ],
  ],
});
// --8<-- [end:routing-output]
