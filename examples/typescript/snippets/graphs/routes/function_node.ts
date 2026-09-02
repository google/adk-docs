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

// The simplest node type: a plain function wrapped as a FunctionNode. It takes
// text in, returns text out, and the framework hands that value to the next
// node as its input — no session-state writes needed.

// --8<-- [start:function-node]
import {
  createEvent,
  node,
  NodeContext,
  Workflow,
  type FunctionNodeHandler,
} from '@google/adk';

/** A bare return value: boxed into an event's `output` for you. */
const myFunctionNode: FunctionNodeHandler<string, string> = (
  _ctx: NodeContext,
  nodeInput: string,
) => {
  const inputTextModified = nodeInput.toUpperCase();
  return inputTextModified;
};

/** The explicit form — identical behaviour, useful when you also set `route`. */
const myExplicitEventNode = (_ctx: NodeContext, nodeInput: string) =>
  createEvent({ output: `${nodeInput} IS AWESOME!` });

export const rootAgent = new Workflow({
  name: 'function_node_pipeline',
  edges: [
    [
      'START',
      node(myFunctionNode, { name: 'my_function_node' }),
      node(myExplicitEventNode, { name: 'add_suffix' }),
    ],
  ],
});
// --8<-- [end:function-node]
