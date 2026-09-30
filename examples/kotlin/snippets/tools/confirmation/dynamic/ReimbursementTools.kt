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

package com.google.adk.kt.examples.tools.confirmation.dynamic

import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.tools.ToolContext

// --8<-- [start:dynamic_confirmation]
class ReimbursementTools {
    /** Reimburse an amount, requiring manager approval above a threshold. */
    @Tool
    fun reimburse(
        context: ToolContext,
        @Param("The amount to reimburse.") amount: Int,
    ): Map<String, Any?> {
        // The @Tool annotation's requireConfirmation flag is a compile-time constant,
        // so the threshold is evaluated here using the ToolContext instead.
        if (amount > 1000) {
            val confirmation = context.toolConfirmation
            if (confirmation == null) {
                context.requestConfirmation(hint = "Amount > 1000 requires approval.")
                // Return an intermediate status while the confirmation is pending.
                return mapOf("status" to "Pending manager approval.")
            }
            if (!confirmation.confirmed) {
                return mapOf("status" to "Reimbursement rejected.")
            }
        }
        return mapOf("status" to "ok", "reimbursedAmount" to amount)
    }
}
// --8<-- [end:dynamic_confirmation]
