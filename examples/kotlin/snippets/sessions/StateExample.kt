package com.google.adk.kt.examples.sessions

import com.google.adk.kt.agents.CallbackContext
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.agents.ReadonlyContext
import com.google.adk.kt.callbacks.AfterAgentCallback
import com.google.adk.kt.callbacks.CallbackChoice
import com.google.adk.kt.events.Event
import com.google.adk.kt.events.EventActions
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.sessions.SessionKey
import com.google.adk.kt.tools.ToolContext
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Role
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.runBlocking

/**
 * This example demonstrates various ways to manage session state in Kotlin.
 */
// --8<-- [start:full_example]
fun main() = runBlocking {
    // --- Constants ---
    val appName = "state_example_app"
    val userId = "state_user"
    val model = Gemini(name = "gemini-flash-latest")

    // --- Services ---
    val sessionService = InMemorySessionService()

    // --- 1. Instruction Templating ---
    // Inject state values into agent instructions using {key} syntax.
    val templateAgent = LlmAgent(
        name = "TemplateAgent",
        model = model,
        instruction = Instruction("Greet the user and mention their favorite color: {favorite_color}.")
    )

    // --- 2. State Updates in Callbacks ---
    // Update state directly in a callback using context.updateState()
    val logTurnCallback = AfterAgentCallback { context ->
        val turnCount = context.state["turn_count"] as? Int ?: 0
        context.updateState("turn_count", turnCount + 1)
        println("Turn #$turnCount logged in callback.")
        CallbackChoice.Continue(Unit)
    }

    val callbackAgent = LlmAgent(
        name = "CallbackAgent",
        model = model,
        instruction = Instruction("Answer concisely."),
        afterAgentCallbacks = listOf(logTurnCallback)
    )

    // --- 3. Manual State Updates via EventActions ---
    println("--- Manual State Update ---")
    val sessionId = "manual_session"
    val sessionKey = SessionKey(appName, userId, sessionId)
    val session = sessionService.createSession(
        key = sessionKey,
        state = mapOf("favorite_color" to "blue", "turn_count" to 0)
    )

    val stateUpdateEvent = Event(
        invocationId = "manual_update",
        author = "system",
        actions = EventActions(
            stateDelta = mutableMapOf("user:preferred_language" to "en")
        ),
        timestamp = System.currentTimeMillis()
    )
    val unused = sessionService.appendEvent(session, stateUpdateEvent)
    
    val updatedSession = sessionService.getSession(sessionKey)
    println("Updated State: ${updatedSession?.state}")

    // --- 4. Running with Templating ---
    println("\n--- Running with Templating ---")
    val runner = InMemoryRunner(
        agent = templateAgent,
        appName = appName,
        sessionService = sessionService
    )
    val userMessage = Content.fromText(Role.USER, "Hello!")
    
    runner.runAsync(
        userId = userId,
        sessionId = sessionId,
        newMessage = userMessage
    ).collect { event ->
        event.content?.parts?.forEach { part ->
            if (!part.text.isNullOrBlank()) {
                println("Agent Response: ${part.text}")
            }
        }
    }
}
// --8<-- [end:full_example]

// --8<-- [start:instruction_templating]
fun instructionTemplating(model: Gemini) {
    val storyGenerator = LlmAgent(
        name = "StoryGenerator",
        model = model,
        instruction = Instruction("Write a short story about a cat, focusing on the theme: {topic}.")
    )

    // Assuming session.state["topic"] is set to "friendship", the LLM
    // will receive the following instruction:
    // "Write a short story about a cat, focusing on the theme: friendship."
}
// --8<-- [end:instruction_templating]

// --8<-- [start:instruction_provider]
fun instructionProvider(model: Gemini) {
    // This is an Instruction.Provider
    val myInstructionProvider = Instruction { context: ReadonlyContext ->
        // No state injection occurs — curly braces are treated as literal text.
        Content(
            parts = listOf(Part(text = "Format your output as JSON: {\"city\": \"<name>\", \"population\": <number>}"))
        )
    }

    val agent = LlmAgent(
        model = model,
        name = "template_helper_agent",
        instruction = myInstructionProvider
    )
}
// --8<-- [end:instruction_provider]

// --8<-- [start:state_updates_context]
fun myCallbackFunction(context: CallbackContext) {
    // Update existing state using updateState helper
    val count = context.state["user_action_count"] as? Int ?: 0
    context.updateState("user_action_count", count + 1)

    // Add new state
    context.updateState("temp:last_operation_status", "success")
}

suspend fun myToolFunction(context: ToolContext, args: Map<String, Any>) {
    // Access state via context.context.state
    val count = context.context.state["user_action_count"] as? Int ?: 0
    
    // Update state via context.actions.stateDelta
    context.actions.stateDelta["user_action_count"] = count + 1
    context.actions.stateDelta["temp:last_operation_status"] = "success"
}
// --8<-- [end:state_updates_context]
