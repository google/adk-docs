package com.google.adk.kt.examples.tools

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.models.Gemini

// --8<-- [start:long_running_tool]
data class ReimbursementApproval(
    val status: String,
    val approver: String,
    val purpose: String,
    val amount: Double,
    val ticketId: String,
)

class ReimbursementService {
    /**
     * Asks for approval for the reimbursement.
     */
    @Tool(isLongRunning = true)
    fun askForApproval(
        @Param("The purpose of the reimbursement.") purpose: String,
        @Param("The amount to be reimbursed.") amount: Double,
    ): ReimbursementApproval {
        // Simulate creating a ticket and sending a notification.
        // This tool returns the initial result and then the agent pauses.
        return ReimbursementApproval(
            status = "pending",
            approver = "Sean Zhou",
            purpose = purpose,
            amount = amount,
            ticketId = "approval-ticket-1",
        )
    }
}

fun main() {
    val service = ReimbursementService()
    val agent =
        LlmAgent(
            name = "approver_agent",
            model = Gemini(name = "gemini-flash-latest"),
            instruction = Instruction("You are a helpful reimbursement assistant."),
            tools = service.generatedTools(),
        )
}
// --8<-- [end:long_running_tool]
