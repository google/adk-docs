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

package com.google.adk.kt.examples.tools.confirmation

import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.tools.ToolContext

// --8<-- [start:boolean_confirmation]
class ReimbursementTools {
    /** Reimburse an amount. */
    @Tool(requireConfirmation = true) // Pause for user confirmation before every call.
    fun reimburse(
        @Param("The amount to reimburse.") amount: Int,
    ): Map<String, Any?> = mapOf("status" to "ok", "reimbursedAmount" to amount)
}

val reimbursementAgent =
    LlmAgent(
        name = "reimbursement_agent",
        model = Gemini(name = "gemini-flash-latest"),
        tools = ReimbursementTools().generatedTools(),
    )
// --8<-- [end:boolean_confirmation]

// --8<-- [start:advanced_confirmation]
class TimeOffTools {
    /** Request day off for the employee. */
    @Tool
    fun requestTimeOff(
        context: ToolContext,
        @Param("The number of days requested.") days: Int,
    ): Map<String, Any?> {
        val confirmation = context.toolConfirmation
        if (confirmation == null) {
            context.requestConfirmation(
                hint =
                    "Please approve or reject the tool call requestTimeOff() by responding " +
                        "with a FunctionResponse with an expected ToolConfirmation payload.",
                payload = mapOf("approved_days" to 0),
            )
            // Return an intermediate status indicating that the tool is waiting for
            // a confirmation response:
            return mapOf("status" to "Manager approval is required.")
        }

        // The payload comes back decoded from JSON, so the number may arrive as any
        // Number subtype. Read it through Number rather than casting straight to Int.
        val payload = confirmation.payload as? Map<*, *>
        val approvedDays =
            minOf((payload?.get("approved_days") as? Number)?.toInt() ?: 0, days)
        if (approvedDays == 0) {
            return mapOf("status" to "The time off request is rejected.", "approved_days" to 0)
        }
        return mapOf("status" to "ok", "approved_days" to approvedDays)
    }
}
// --8<-- [end:advanced_confirmation]
