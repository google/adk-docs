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

// A dynamic workflow defines the iteration as an ordinary loop rather than a
// back-edge in a graph. Values are held in local variables, and state is
// written only where an agent's instruction template needs to read it back
// (`{code}`, `{findings}`).

// --8<-- [start:loop-route]
import { LlmAgent, node, NodeContext, Workflow } from '@google/adk';

/** Safety bound on the refine loop. */
const MAX_FIX_ROUNDS = 3;

const coderAgent = new LlmAgent({
  name: 'generator_agent',
  model: 'gemini-flash-latest',
  instruction: 'Write TypeScript code for the user request. Output code only.',
});

/** Simulates a compile / lint pass. Empty findings means "clean". */
const compileLintCheck = node(
  (_ctx: NodeContext, code: string) => {
    const findings: string[] = [];
    if (!/\/\*\*/.test(code)) {
      findings.push('every function needs a JSDoc comment');
    }
    if (!/\)\s*:\s*\w/.test(code)) {
      findings.push('add return type annotations');
    }
    return { findings: findings.join('; ') };
  },
  { name: 'lint_reviewer' },
);

const fixerAgent = new LlmAgent({
  name: 'fixer_agent',
  model: 'gemini-flash-latest',
  instruction: `Refactor current code {code}.
      Based on compile & lint review: {findings}
      Output code only.`,
});

const codeWorkflow = node(
  async (ctx: NodeContext, userRequest: string) => {
    let code = (await ctx.runNode(coderAgent, userRequest)).output as string;
    let checkResp = (await ctx.runNode(compileLintCheck, code)).output as {
      findings: string;
    };

    for (let round = 0; checkResp.findings && round < MAX_FIX_ROUNDS; round++) {
      ctx.state.set('code', code);
      ctx.state.set('findings', checkResp.findings);

      code = (
        await ctx.runNode(fixerAgent, { code, findings: checkResp.findings })
      ).output as string;
      checkResp = (await ctx.runNode(compileLintCheck, code)).output as {
        findings: string;
      };
    }

    return code;
  },
  { name: 'code_workflow', rerunOnResume: true },
);

export const rootAgent = new Workflow({
  name: 'root_agent',
  edges: [['START', codeWorkflow]],
});
// --8<-- [end:loop-route]
