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

// A sequential route in a dynamic workflow is just awaiting `ctx.runNode()`
// calls one after another — each finishes before the next starts. Schemas work
// the same as in a graph: attach them to the nodes you run.

// --8<-- [start:sequence-route]
import { LlmAgent, node, NodeContext, Workflow } from '@google/adk';
import { z } from 'zod';

const cityTimeSchema = z.object({
  timeInfo: z.string().describe('Time information.'),
  city: z.string().describe('City name.'),
});
type CityTime = z.infer<typeof cityTimeSchema>;

const cityGeneratorAgent = new LlmAgent({
  name: 'city_generator_agent',
  model: 'gemini-flash-latest',
  instruction: 'Return the name of a random city. Return only the name.',
});

/** Simulates returning the current time in a specified city. */
const cityTimeFunction = node(
  (_ctx: NodeContext, city: string): CityTime => ({
    timeInfo: '10:10 AM',
    city: city.trim(),
  }),
  { name: 'city_time_function', outputSchema: cityTimeSchema },
);

const cityReportAgent = node(
  new LlmAgent({
    name: 'city_report_agent',
    model: 'gemini-flash-latest',
    instruction: 'Output the data provided by the previous node as a sentence.',
  }),
  { inputSchema: cityTimeSchema },
);

const cityWorkflow = node(
  async (ctx: NodeContext) => {
    const city = await ctx.runNode(cityGeneratorAgent);
    const cityTime = await ctx.runNode(cityTimeFunction, city.output);
    const reportText = await ctx.runNode(cityReportAgent, cityTime.output);

    return reportText.output;
  },
  { name: 'city_workflow', rerunOnResume: true },
);

export const rootAgent = new Workflow({
  name: 'root_agent',
  edges: [['START', cityWorkflow]],
});
// --8<-- [end:sequence-route]
