/*
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.google.adk.kt.examples.tools.overview

// --8<-- [start:snippet]

import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool

class OrderTools {
    /**
     * Fetches the current status of a customer's order using its ID.
     *
     * Use this tool ONLY when a user explicitly asks for the status of a specific
     * order and provides the order ID. Do not use it for general inquiries.
     *
     * Returns a map indicating the outcome. On success, "status" is "success" and
     * an "order" map holds the "state" and "tracking_number". On failure, "status"
     * is "error" and "error_message" explains why.
     */
    @Tool
    fun lookupOrderStatus(
        @Param("The unique identifier of the order to look up.") orderId: String,
    ): Map<String, Any> {
        val statusDetails = fetchStatusFromBackend(orderId)
        return if (statusDetails != null) {
            mapOf(
                "status" to "success",
                "order" to
                    mapOf(
                        "state" to statusDetails.state,
                        "tracking_number" to statusDetails.tracking,
                    ),
            )
        } else {
            mapOf(
                "status" to "error",
                "error_message" to "Order ID $orderId not found.",
            )
        }
    }
}

private data class OrderStatusDetails(val state: String, val tracking: String)

private fun fetchStatusFromBackend(orderId: String): OrderStatusDetails? =
    if (orderId == "1Z9") OrderStatusDetails(state = "shipped", tracking = "1Z9...") else null
// --8<-- [end:snippet]
