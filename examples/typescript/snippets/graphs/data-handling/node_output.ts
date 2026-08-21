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

// A node hands data to its successor through the event's `output` field.

// --8<-- [start:node-output]
import { createEvent, node, NodeContext, Workflow } from "@google/adk";

const returnRawValue = node(
  (_ctx: NodeContext, nodeInput: string) => nodeInput.toUpperCase(),
  { name: "return_raw_value" },
);

const returnEventOutput = node(
  (_ctx: NodeContext, nodeInput: string) =>
    createEvent({ output: `${nodeInput}!` }),
  { name: "return_event_output" },
);

const yieldProgressThenOutput = node(
  async function* (_ctx: NodeContext, nodeInput: string) {
    yield createEvent({
      content: { role: "model", parts: [{ text: "Working on it..." }] },
    });
    yield createEvent({ output: `<<${nodeInput}>>` });
  },
  { name: "yield_progress_then_output" },
);

export const rootAgent = new Workflow({
  name: "node_output_workflow",
  edges: [
    ["START", returnRawValue, returnEventOutput, yieldProgressThenOutput],
  ],
});
// --8<-- [end:node-output]
