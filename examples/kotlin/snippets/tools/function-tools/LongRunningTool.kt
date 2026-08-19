package com.google.adk.kt.examples.tools

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.runners.Runner
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.FunctionResponse
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Role
import kotlinx.coroutines.flow.toList

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

/**
 * Drives the approval from the client side.
 *
 * `askForApproval` is long running, so it returns a `pending` placeholder and the
 * turn ends. The real decision arrives out of band and is handed back on a later
 * turn as a `FunctionResponse`.
 */
suspend fun approveReimbursement(
    runner: Runner,
    userId: String,
    sessionId: String,
    // True when the app was built with ResumabilityConfig(isResumable = true).
    appIsResumable: Boolean = false,
) {
    val firstTurn =
        runner
            .runAsync(
                userId = userId,
                sessionId = sessionId,
                newMessage = Content.fromText(Role.USER, "Please reimburse 200 USD for meals."),
            ).toList()

    // A pending call is one whose id the event also lists in longRunningToolIds.
    val pendingCall =
        firstTurn.firstNotNullOfOrNull { event ->
            event.functionCalls().firstOrNull { it.id != null && it.id in event.longRunningToolIds }
        } ?: return

    // Reuse the id of the original call, or the model cannot match this answer to
    // the request it is still waiting on.
    val approval =
        Content(
            role = Role.USER,
            parts =
                listOf(
                    Part(
                        functionResponse =
                            FunctionResponse(
                                name = pendingCall.name,
                                id = pendingCall.id,
                                response = mapOf("status" to "approved", "approver" to "Sean Zhou"),
                            ),
                    ),
                ),
        )

    runner
        .runAsync(
            userId = userId,
            sessionId = sessionId,
            // A resumable app must resume the invocation that raised the call;
            // without the id the response starts a new invocation instead. A
            // non-resumable app passes null and continues in a fresh invocation.
            invocationId = if (appIsResumable) firstTurn.firstOrNull()?.invocationId else null,
            newMessage = approval,
        ).collect { event ->
            event.content?.parts?.forEach { part -> part.text?.let(::println) }
        }
}
// --8<-- [end:call_reimbursement_tool]
