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

// ADK gives every child execution a deterministic id derived from the parent id
// and a per-node-name counter ("1", "2", "3", ...). Those ids are how a resumed
// or retried workflow recognises work that already completed and skips it.
//
// Avoid custom run ids. The one legitimate case is a REORDERABLE collection,
// where position is not stable but identity is — key the run id off the item's
// own id, as below.

// --8<-- [start:custom-execution-ids]
import { node, NodeContext, Workflow } from "@google/adk";

interface Order {
  orderId: string;
  cartItems: string[];
}

/** Stands in for loading orders from a database. */
async function getOrders(): Promise<Order[]> {
  return [
    { orderId: "a91", cartItems: ["keyboard", "mouse"] },
    { orderId: "b02", cartItems: ["monitor"] },
    { orderId: "c73", cartItems: ["dock", "cable", "hub"] },
  ];
}

const processOrder = node(
  (_ctx: NodeContext, order: Order) =>
    `order ${order.orderId}: ${order.cartItems.length} item(s) shipped`,
  { name: "process_order" },
);

const processAllOrders = node(
  async (ctx: NodeContext) => {
    const orders = await getOrders();

    const processTasks = orders.map((order) =>
      ctx.runNode(processOrder, order, { runId: `order-${order.orderId}` }),
    );

    const results = await Promise.all(processTasks);
    return results.map((result) => result.output).join("\n");
  },
  { name: "process_all_orders", rerunOnResume: true },
);

export const rootAgent = new Workflow({
  name: "root_agent",
  edges: [["START", processAllOrders]],
});
// --8<-- [end:custom-execution-ids]
