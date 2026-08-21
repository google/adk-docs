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

// A dynamic workflow drops the static edge graph and orchestrates in plain
// code: an outer node calls `ctx.runNode(child, input)` to execute children in
// whatever order your loops and conditionals dictate.

// --8<-- [start:get-started]
import { node, NodeContext, Workflow } from "@google/adk";

const myNode = node(() => "Hello World", { name: "hello_node" });

// An orchestrator that calls `ctx.runNode` must set `rerunOnResume: true`, so
// its body re-runs on resume and already-finished children are replayed from
// their checkpoints rather than executed again.
const myWorkflow = node(
  async (ctx: NodeContext, _nodeInput: string) => {
    // runNode executes a node and resolves to its RESULT, so read `.output`.
    const result = await ctx.runNode(myNode, "hello");
    return result.output;
  },
  { name: "my_workflow", rerunOnResume: true },
);

export const rootAgent = new Workflow({
  name: "root_agent",
  edges: [["START", myWorkflow]],
});
// --8<-- [end:get-started]
