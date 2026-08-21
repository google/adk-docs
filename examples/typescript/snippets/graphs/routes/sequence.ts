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

// A sequential route runs each node once, in the listed order. Each node's
// return value is delivered to the next node as its input.

// --8<-- [start:sequence]
import { node, NodeContext, Workflow } from "@google/adk";

const taskANode = node(
  (_ctx: NodeContext, nodeInput: string) => `Summary: ${nodeInput.trim()}`,
  { name: "task_A_node" },
);

const taskBNode = node(
  (_ctx: NodeContext, summary: string) => summary.toUpperCase(),
  { name: "task_B_node" },
);

const taskCNode = node(
  (_ctx: NodeContext, shouted: string) => `${shouted} (done)`,
  { name: "task_C_node" },
);

export const rootAgent = new Workflow({
  name: "sequential_workflow",
  edges: [["START", taskANode, taskBNode, taskCNode]],
});
// --8<-- [end:sequence]
