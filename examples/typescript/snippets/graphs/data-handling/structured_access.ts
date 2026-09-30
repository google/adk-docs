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

// Two data-selection forms are available inside an agent instruction:
//
//   {Class.field}                    reads a field off THIS node's input
//   <Class.field from source_node>   reads a field off a named predecessor's
//                                    output — more restrictive, and unambiguous
//                                    when several upstream nodes share a field
//
// Both are distinct from `{state_key}`, which reads session state.

// --8<-- [start:structured-access]
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

/** Simulates returning the current time in the specified city. */
const lookupTimeFunction = node(
  (_ctx: NodeContext, city: string): CityTime => ({
    timeInfo: '10:10 AM',
    city: city.trim(),
  }),
  { name: 'lookup_time_function', outputSchema: cityTimeSchema },
);

const cityReportAgent = new LlmAgent({
  name: 'city_report_agent',
  model: 'gemini-flash-latest',
  instruction:
    'Return a sentence in the following format: It is ' +
    '<CityTime.timeInfo from lookup_time_function> in ' +
    '<CityTime.city from lookup_time_function> right now.',
});

export const rootAgent = new Workflow({
  name: 'root_agent',
  edges: [
    [
      'START',
      cityGeneratorAgent,
      lookupTimeFunction,
      node(cityReportAgent, { inputSchema: cityTimeSchema }),
    ],
  ],
});
// --8<-- [end:structured-access]
