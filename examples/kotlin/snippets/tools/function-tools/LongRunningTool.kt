package com.google.adk.kt.examples.tools

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.events.Event
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
 * `askForApproval` is long running, so its return value is only a `pending`
 * placeholder: the real decision arrives out of band and is handed back on a
 * later turn as a `FunctionResponse`.
 *
 * What turn 1 looks like depends on the app. Because this tool returns a value
 * rather than `Unit`, a non-resumable app emits the placeholder as a function
 * response and calls the model a second time, so the user sees an interim reply
 * before the decision exists. A resumable app pauses on the function call
 * instead, with no second model call.
 */
suspend fun approveReimbursement(
    runner: Runner,
    userId: String,
    sessionId: String,
) {
    val firstTurn =
        runner
            .runAsync(
                userId = userId,
                sessionId = sessionId,
                newMessage = Content.fromText(Role.USER, "Please reimburse 200 USD for meals."),
            ).toList()
    firstTurn.printText()

    // A pending call is one whose id the event also lists in longRunningToolIds.
    val pendingCall =
        firstTurn.firstNotNullOfOrNull { event ->
            event.functionCalls().firstOrNull { it.id != null && it.id in event.longRunningToolIds }
        }
    if (pendingCall == null) {
        println("The model answered without calling the tool; nothing to approve.")
        return
    }

    // The id is not optional bookkeeping: the framework matches the response to
    // the original call by id, and a missing or unknown one throws rather than
    // degrading. It also tells a resumable app which invocation to resume, so no
    // invocationId argument is needed here.
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
            newMessage = approval,
        ).toList()
        .printText()
}

private fun List<Event>.printText() =
    forEach { event ->
        event.content?.parts?.forEach { part -> part.text?.let(::println) }
    }
// --8<-- [end:call_reimbursement_tool]
