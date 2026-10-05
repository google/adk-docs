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

// `output` is not limited to text — any serializable value flows to the next
// node, which receives it as a typed object.

// --8<-- [start:structured-output]
import { createEvent, node, NodeContext, Workflow } from '@google/adk';
import { z } from 'zod';

const cityInfoSchema = z.object({
  cityName: z.string(),
  cityTime: z.string(),
});
type CityInfo = z.infer<typeof cityInfoSchema>;

const emitStructuredOutput = node(
  async function* () {
    yield createEvent({
      output: { cityName: 'Paris', cityTime: '10:10 AM' } satisfies CityInfo,
    });
  },
  { name: 'emit_structured_output', outputSchema: cityInfoSchema },
);

const consumeStructuredOutput = node(
  (_ctx: NodeContext, cityInfo: CityInfo) =>
    `It is ${cityInfo.cityTime} in ${cityInfo.cityName} right now.`,
  { name: 'consume_structured_output', inputSchema: cityInfoSchema },
);

export const rootAgent = new Workflow({
  name: 'structured_output_workflow',
  edges: [['START', emitStructuredOutput, consumeStructuredOutput]],
});
// --8<-- [end:structured-output]
