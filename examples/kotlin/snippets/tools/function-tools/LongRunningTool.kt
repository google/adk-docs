package com.google.adk.kt.examples.tools

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.events.Event
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.FunctionResponse
import com.google.adk.kt.types.Part

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

// --8<-- [start:call_reimbursement_tool]
private fun printText(event: Event) {
    val text = event.content?.parts?.mapNotNull { it.text }?.joinToString("").orEmpty()
    if (text.isNotEmpty()) println("[${event.author}]: $text")
}

suspend fun callReimbursementAgent(
    runner: InMemoryRunner,
    userId: String,
    sessionId: String,
    query: String,
) {
    var pendingCallId: String? = null
    var pendingResponse: FunctionResponse? = null

    runner
        .runAsync(
            userId = userId,
            sessionId = sessionId,
            newMessage = Content(role = "user", parts = listOf(Part(text = query))),
        ).collect { event ->
            val callId = pendingCallId
            if (callId == null) {
                // A long-running call is the one whose id the event lists in longRunningToolIds.
                pendingCallId =
                    event
                        .functionCalls()
                        .firstOrNull { it.id != null && it.id in event.longRunningToolIds }
                        ?.id
            } else {
                event
                    .functionResponses()
                    .firstOrNull { it.id == callId }
                    ?.let { pendingResponse = it }
            }
            printText(event)
        }

    // The tool returned "pending" and the invocation paused. Resume it by sending the
    // outcome back as a FunctionResponse carrying the same id.
    val paused = pendingResponse ?: return
    val updated = paused.copy(response = mapOf("status" to "approved"))
    runner
        .runAsync(
            userId = userId,
            sessionId = sessionId,
            newMessage = Content(role = "user", parts = listOf(Part(functionResponse = updated))),
        ).collect(::printText)
}
// --8<-- [end:call_reimbursement_tool]
