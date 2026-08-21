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

// `step1` pauses the workflow until the user replies; the reply is then handed
// to the next node as its input. This is the default `rerunOnResume: false`
// handoff: the interrupted node does NOT re-run — it completes with the user's
// reply as its output. A HITL node needs no model, which makes the pause fully
// deterministic.

// --8<-- [start:get-started]
import { node, NodeContext, RequestInput, Workflow } from "@google/adk";

const step1 = node(
  async function* () {
    yield new RequestInput({ message: "Enter a number:" });
  },
  { name: "step1" },
);

const step2 = node(
  (_ctx: NodeContext, nodeInput: string | number) => {
    // An interactive reply arrives as text, so coerce before doing maths.
    const value = Number(nodeInput);
    return Number.isFinite(value)
      ? value * 2
      : `"${nodeInput}" is not a number.`;
  },
  { name: "step2" },
);

export const rootAgent = new Workflow({
  name: "root_agent",
  edges: [["START", step1, step2]],
});
// --8<-- [end:get-started]
