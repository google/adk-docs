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

// A parent node that calls `ctx.runNode` must set `rerunOnResume: true`, or it
// cannot handle an interrupt raised by a child. The leaf keeps
// `rerunOnResume: false`: on resume it does not re-run its body, it completes
// with the human's reply as its output.

// --8<-- [start:human-input]
import { node, NodeContext, RequestInput, Workflow } from "@google/adk";

/**
 * Pauses the workflow and waits for user input.
 *
 * `rerunOnResume: false` (the default, spelled out here because it is the
 * point) is what makes this a one-liner: the reply is handed to the node as
 * its output instead of the body running a second time to collect it.
 */
const getUserApproval = node(
  () => new RequestInput({ message: "Please approve this request (Yes/No)" }),
  { name: "get_user_approval", rerunOnResume: false },
);

/** The orchestrator calling the interactive step. */
const handleProcess = node(
  async (ctx: NodeContext, nodeInput: unknown) => {
    const approval = await ctx.runNode(getUserApproval, nodeInput);

    if (approval.interruptIds.length > 0) {
      return undefined;
    }

    const userResponse = String(approval.output ?? "")
      .trim()
      .toLowerCase();

    if (userResponse === "yes") {
      return "Approved";
    }
    return "Denied";
  },
  { name: "handle_process", rerunOnResume: true },
);

export const rootAgent = new Workflow({
  name: "root_agent",
  edges: [["START", handleProcess]],
});
// --8<-- [end:human-input]
