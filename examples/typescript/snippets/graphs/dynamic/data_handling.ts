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

// Passing data in a dynamic workflow is simpler than in a graph: `ctx.runNode()`
// hands you the child's result directly, so there are no session-state keys to
// read and write just to move a value one step downstream.

// --8<-- [start:data-handling]
import { LlmAgent, node, NodeContext, Workflow } from '@google/adk';

const draftAgent = new LlmAgent({
  name: 'draft_agent',
  model: 'gemini-flash-latest',
  instruction: 'Write a short draft for the user request.',
});

const formatFunctionNode = node(
  (_ctx: NodeContext, rawDraft: string) =>
    rawDraft
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => `| ${line}`)
      .join('\n'),
  { name: 'format_function_node' },
);

const editorialWorkflow = node(
  async (ctx: NodeContext, userRequest: string) => {
    const rawDraft = await ctx.runNode(draftAgent, userRequest);

    const formattedText = await ctx.runNode(
      formatFunctionNode,
      rawDraft.output,
    );

    return formattedText.output;
  },
  { name: 'editorial_workflow', rerunOnResume: true },
);

export const rootAgent = new Workflow({
  name: 'root_agent',
  edges: [['START', editorialWorkflow]],
});
// --8<-- [end:data-handling]
