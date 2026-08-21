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

// A sequential graph workflow that alternates between model reasoning and plain
// code: an agent names a random city, a code function looks up the time there,
// a second agent reports it, and a final function appends a completion message.

// --8<-- [start:get-started]
import {
  createEvent,
  LlmAgent,
  node,
  NodeContext,
  Workflow,
} from "@google/adk";
import { z } from "zod";

const cityGeneratorAgent = new LlmAgent({
  name: "city_generator_agent",
  model: "gemini-flash-latest",
  instruction: `Return the name of a random city.
      Return only the name, nothing else.`,
});

/** The structured payload handed from the lookup node to the report agent. */
const cityTimeSchema = z.object({
  timeInfo: z.string().describe("Time information."),
  city: z.string().describe("City name."),
});
type CityTime = z.infer<typeof cityTimeSchema>;

/** Simulates returning the current time in the specified city. */
function lookupTimeFunction(_ctx: NodeContext, nodeInput: string): CityTime {
  return { timeInfo: "10:10 AM", city: nodeInput.trim() };
}

const cityReportAgent = new LlmAgent({
  name: "city_report_agent",
  model: "gemini-flash-latest",
  // `{CityTime.<field>}` selects a field off THIS node's input. The `CityTime.`
  // prefix is documentation; only the field name after the dot is resolved.
  instruction: `Output the following line:
    It is {CityTime.timeInfo} in {CityTime.city} right now.`,
});

function completedMessageFunction(_ctx: NodeContext, nodeInput: string) {
  // A user-facing message is the event's `content` which, unlike `output`, is
  // not handed to the next node.
  return createEvent({
    content: {
      role: "model",
      parts: [{ text: `${nodeInput}\n WORKFLOW COMPLETED.` }],
    },
  });
}

export const rootAgent = new Workflow({
  name: "root_agent",
  edges: [
    [
      "START",
      cityGeneratorAgent,
      node(lookupTimeFunction, {
        name: "lookup_time_function",
        outputSchema: cityTimeSchema,
      }),
      // The validating schema belongs to the node wrapping the agent — an
      // `LlmAgent.inputSchema` is only used when the agent is exposed as a tool.
      node(cityReportAgent, { inputSchema: cityTimeSchema }),
      node(completedMessageFunction, { name: "completed_message_function" }),
    ],
  ],
});
// --8<-- [end:get-started]
