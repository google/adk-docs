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

// A `JoinNode` is a fan-in barrier: it waits for EVERY predecessor to finish
// and then hands the next node an object keyed by predecessor node name.

// --8<-- [start:fan-out-join]
import { JoinNode, node, NodeContext, Workflow } from "@google/adk";

const parallelTaskA = node(
  (_ctx: NodeContext, text: string) => text.toUpperCase(),
  { name: "parallel_task_A" },
);

const parallelTaskB = node((_ctx: NodeContext, text: string) => text.length, {
  name: "parallel_task_B",
});

const parallelTaskC = node(
  (_ctx: NodeContext, text: string) => text.split("").reverse().join(""),
  { name: "parallel_task_C" },
);

const myJoinNode = new JoinNode({ name: "my_join_node" });

const finalTaskD = node(
  (_ctx: NodeContext, results: Record<string, unknown>) =>
    [
      `Uppercase: ${results["parallel_task_A"]}`,
      `Length:    ${results["parallel_task_B"]}`,
      `Reversed:  ${results["parallel_task_C"]}`,
    ].join("\n"),
  { name: "final_task_D" },
);

export const rootAgent = new Workflow({
  name: "fan_out_workflow",
  edges: [
    ["START", parallelTaskA, myJoinNode],
    ["START", parallelTaskB, myJoinNode],
    ["START", parallelTaskC, myJoinNode],
    [myJoinNode, finalTaskD],
  ],
});
// --8<-- [end:fan-out-join]
