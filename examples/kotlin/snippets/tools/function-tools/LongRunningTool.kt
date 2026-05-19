package com.google.adk.kt.examples.tools

import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool

// --8<-- [start:long_running_tool]
class ReimbursementService {
    /**
     * Asks for approval for the reimbursement.
     */
    @Tool(isLongRunning = true)
    fun askForApproval(
        @Param("The purpose of the reimbursement.") purpose: String,
        @Param("The amount to be reimbursed.") amount: Double
    ): Map<String, Any> {
        // Simulate creating a ticket and sending a notification.
        // This tool returns the initial result and then the agent pauses.
        return mapOf(
            "status" to "pending",
            "approver" to "Sean Zhou",
            "purpose" to purpose,
            "amount" to amount,
            "ticket-id" to "approval-ticket-1"
        )
    }
}

fun main() {
    val service = ReimbursementService()
    val agent = LlmAgent(
        name = "approver_agent",
        // ...
        tools = service.generatedTools()
    )
}
// --8<-- [end:long_running_tool]
