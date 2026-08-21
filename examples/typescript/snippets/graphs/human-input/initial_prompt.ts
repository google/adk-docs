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

// A human-input node as the FIRST step of a workflow: instead of guessing what
// the user wants, the graph opens by asking, pauses, and then routes the reply
// into the rest of the process.
//
// `responseSchema: z.string()` asks for a plain text reply. Nothing coerces the
// human's answer into that shape; the schema tells a client what to collect.

// --8<-- [start:initial-prompt]
import { node, NodeContext, RequestInput, Workflow } from "@google/adk";
import { z } from "zod";

/** Asks the user for itinerary information. */
const initialPrompt = node(
  async function* () {
    const inputMessage = `
        This is an interactive concierge workflow tasked with making you a great
        itinerary for you in your city of choice. If you give some details about
        yourself or what you are generally looking for I can better personalize
        your itinerary.
        For example, input your:
            City (Required),
            Age,
            Hobby,
            Example of attraction you liked
    `;
    yield new RequestInput({
      message: inputMessage,
      responseSchema: z.string(),
    });
  },
  { name: "initial_prompt" },
);

// Receives the user's reply as its input and kicks off the real work.
const buildItinerary = node(
  (_ctx: NodeContext, nodeInput: string) => {
    const [city = "your city"] = nodeInput.split(",");
    return (
      `Personalized itinerary for ${city.trim()}:\n` +
      "  1. Morning walk through the old town\n" +
      "  2. Lunch at a neighbourhood favourite\n" +
      "  3. An afternoon activity matched to your hobby\n\n" +
      `(based on: ${nodeInput.trim()})`
    );
  },
  { name: "build_itinerary" },
);

export const rootAgent = new Workflow({
  name: "concierge_workflow",
  edges: [["START", initialPrompt, buildItinerary]],
});
// --8<-- [end:initial-prompt]
