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

// `RequestInput` takes three configuration options:
//   message         text shown to the user explaining what is being asked
//   payload         structured data sent alongside the prompt, so a client can
//                   render richer context (here, the full itinerary)
//   responseSchema  the shape the reply is expected to take
//
// `RequestInput` does NOT reformat a human reply to fit `responseSchema` — the
// reply must already be in that shape.

// --8<-- [start:payload-and-schema]
import { node, NodeContext, RequestInput, Workflow } from '@google/adk';
import { z } from 'zod';

/**
 * Itinerary is a list of activities. Each activity has a name and a
 * description.
 */
const activitiesListSchema = z.object({
  itinerary: z.array(z.object({ name: z.string(), description: z.string() })),
});
type ActivitiesList = z.infer<typeof activitiesListSchema>;

/** Expected response structure from the user. */
const userFeedbackSchema = z.object({
  userResponse: z.string(),
});

const buildItinerary = node(
  (_ctx: NodeContext, city: string): ActivitiesList => {
    const place = city.trim() || 'your city';
    return {
      itinerary: [
        { name: 'Morning walk', description: `A stroll through old ${place}.` },
        { name: 'Local lunch', description: `Regional food in ${place}.` },
        { name: 'Museum visit', description: `The main museum of ${place}.` },
      ],
    };
  },
  { name: 'build_itinerary', outputSchema: activitiesListSchema },
);

/**
 * Retrieves the user's thoughts on the agent's initial itinerary in order to
 * either expand on it, change the list, or exit the loop.
 */
const getUserFeedback = node(
  async function* (_ctx: NodeContext, nodeInput: ActivitiesList) {
    const rendered = nodeInput.itinerary
      .map((a, i) => `  ${i + 1}. ${a.name} — ${a.description}`)
      .join('\n');

    yield new RequestInput({
      message:
        `Here is your recommended base itinerary:\n${rendered}\n\n` +
        'Which of these items appeal to you (if any)?',
      payload: nodeInput,
      responseSchema: userFeedbackSchema,
    });
  },
  { name: 'get_user_feedback' },
);

const applyFeedback = node(
  (_ctx: NodeContext, nodeInput: unknown) => {
    const feedback =
      typeof nodeInput === 'string'
        ? nodeInput
        : String(
            (nodeInput as { userResponse?: unknown } | null)?.userResponse ??
              JSON.stringify(nodeInput),
          );
    return `Noted. Building the final itinerary around: ${feedback}`;
  },
  { name: 'apply_feedback' },
);

export const rootAgent = new Workflow({
  name: 'concierge_workflow',
  edges: [['START', buildItinerary, getUserFeedback, applyFeedback]],
});
// --8<-- [end:payload-and-schema]
