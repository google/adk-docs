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

// A message for the human is the event's `content`: the runtime renders it, and
// the graph does NOT forward it as node input. `content` is for the user,
// `output` is for the next node.

// --8<-- [start:user-message]
import { createEvent, node, NodeContext, Workflow } from "@google/adk";

/** Emits a user-facing message: `content`, with no `output`. */
const message = (text: string) =>
  createEvent({ content: { role: "model", parts: [{ text }] } });

const userMessage = node(
  async function* (_ctx: NodeContext, nodeInput: string) {
    yield message(`Beginning research process for "${nodeInput}"...`);
  },
  { name: "user_message" },
);

const research = node(
  async function* () {
    yield message("Gathering sources...");
    yield createEvent({ output: ["source-a", "source-b", "source-c"] });
  },
  { name: "research" },
);

const report = node(
  (_ctx: NodeContext, sources: string[]) =>
    `Research complete. ${sources.length} sources: ${sources.join(", ")}.`,
  { name: "report" },
);

export const rootAgent = new Workflow({
  name: "user_message_workflow",
  edges: [["START", userMessage, research, report]],
});
// --8<-- [end:user-message]
