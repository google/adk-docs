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

// Branching is a node that emits a `route`, plus an edge row mapping each route
// value to the node that handles it. A branch target can be anything node-like:
// `taskBNode` here is an `LlmAgent`, `taskCNode` a plain function.

// --8<-- [start:branches]
import {
  createEvent,
  LlmAgent,
  node,
  NodeContext,
  Workflow,
} from "@google/adk";

const taskANode = node(
  (_ctx: NodeContext, nodeInput: string) => nodeInput.trim(),
  { name: "task_A_node" },
);

/** Stands in for an application-specific branch condition. */
const condition = (nodeInput: string) => /\d/.test(nodeInput);

/** Routes to task B or C based on nodeInput. */
const router = node(
  (_ctx: NodeContext, nodeInput: string) =>
    condition(nodeInput)
      ? createEvent({ route: "RUN_TASK_C", output: nodeInput })
      : createEvent({ route: "RUN_TASK_B", output: nodeInput }),
  { name: "router" },
);

const taskBNode = new LlmAgent({
  name: "task_B_agent",
  model: "gemini-flash-latest",
  instruction: "Answer the user in a single short sentence.",
});

const taskCNode = node(() => "Task C completed", { name: "task_C_node" });

export const rootAgent = new Workflow({
  name: "routing_workflow",
  edges: [
    ["START", taskANode, router],
    [
      router,
      {
        RUN_TASK_B: taskBNode,
        RUN_TASK_C: taskCNode,
      },
    ],
  ],
});
// --8<-- [end:branches]
