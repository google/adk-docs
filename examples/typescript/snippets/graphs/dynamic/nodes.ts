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

// The two ways to build a node, and the orchestrator that composes them.

// --8<-- [start:node-forms]
import { FunctionNode, node, NodeContext, Workflow } from "@google/adk";

/** The plain function both node forms wrap. */
function myFunctionNode(_ctx: NodeContext, nodeInput: unknown): string {
  return `Hello ${nodeInput ?? "World"}`;
}

// Form 1 — the `node()` factory. TypeScript has no `@node` decorator form.
const helloNode = node(myFunctionNode, { name: "hello_node" });

// Form 2 — the explicit constructor, same function, different configuration.
// Reach for it when you are wrapping a function from another library, need
// several differently-configured nodes from one function, or keep node
// references in a registry for advanced orchestration.
const successNode = new FunctionNode("hello", myFunctionNode, {
  rerunOnResume: true,
});
// --8<-- [end:node-forms]

// --8<-- [start:workflows]
const myFormattingNode = node(
  (_ctx: NodeContext, nodeInput: string) => `>> ${nodeInput.trim()} <<`,
  { name: "my_formatting_node" },
);

// The orchestrator: run children in order and return the last result.
const myWorkflow = node(
  async (ctx: NodeContext, nodeInput: unknown) => {
    const greeted = await ctx.runNode(helloNode, nodeInput);
    const again = await ctx.runNode(successNode, greeted.output);
    const formatted = await ctx.runNode(myFormattingNode, again.output);
    return formatted.output;
  },
  { name: "my_workflow", rerunOnResume: true },
);

export const rootAgent = new Workflow({
  name: "root_agent",
  edges: [["START", myWorkflow]],
});
// --8<-- [end:workflows]
