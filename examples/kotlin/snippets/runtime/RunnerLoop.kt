package com.google.adk.kt.examples.runtime

import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.events.Event
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.types.Content
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.onEach

// --8<-- [start:conceptual_loop]
/**
 * Simplified view of Runner's main loop logic in Kotlin
 */
fun runAsync(
    userId: String,
    sessionId: String,
    newMessage: Content,
    runner: InMemoryRunner,
    sessionService: InMemorySessionService
): Flow<Event> {
    // 1. Append newMessage to session event history (via SessionService)
    // 2. Kick off event loop by calling the agent
    // 3. Process generated events, commit changes, and yield upstream
    return runner.runAsync(
        userId = userId,
        sessionId = sessionId,
        newMessage = newMessage
    ).onEach { event ->
        // Process the event and commit changes to services (done internally by Runner)
        // sessionService.appendEvent(...) 
    }
}
// --8<-- [end:conceptual_loop]

// --8<-- [start:execution_logic]
/**
 * Simplified view of logic inside Agent.runAsync, callbacks, or tools in Kotlin
 */
suspend fun executionLogic(ctx: com.google.adk.kt.agents.InvocationContext) {
    // ... previous code runs based on current state ...

    // 1. Determine a change or output is needed, construct the event
    val updateData = mapOf("field_1" to "value_2")
    val eventWithStateChange = com.google.adk.kt.events.Event(
        author = "my_agent",
        actions = com.google.adk.kt.events.EventActions(stateDelta = updateData.toMutableMap()),
        content = com.google.adk.kt.types.Content.fromText(com.google.adk.kt.types.Role.MODEL, "State updated.")
    )

    // 2. Yield the event to the Runner for processing & commit
    // In Kotlin, this is done by emitting to the Flow
    // emit(eventWithStateChange) 
    
    // <<<<<<<<<<<< EXECUTION PAUSES HERE >>>>>>>>>>>>
    // (Implicitly, when the Flow consumer collects the event and processes it)

    // <<<<<<<<<<<< RUNNER PROCESSES & COMMITS THE EVENT >>>>>>>>>>>>

    // 3. Resume execution ONLY after Runner is done processing.
    // Now, the state committed by the Runner is reliably reflected.
    val val1 = ctx.session.state["field_1"]
    println("Resumed execution. Value of field_1 is now: $val1")
}
// --8<-- [end:execution_logic]

// --8<-- [start:state_update_timing]
/**
 * Conceptual view of state update timing in Kotlin
 */
suspend fun stateUpdateTiming(ctx: com.google.adk.kt.agents.InvocationContext) {
    // 1. Modify state
    ctx.session.state["status"] = "processing"
    val event1 = com.google.adk.kt.events.Event(
        author = "my_agent",
        actions = com.google.adk.kt.events.EventActions(stateDelta = mutableMapOf("status" to "processing"))
    )

    // 2. Yield event with the delta (emit to flow)
    // emit(event1)

    // --- PAUSE --- Runner processes event1, SessionService commits 'status' = 'processing' ---

    // 3. Resume execution
    // Now it's safe to rely on the committed state
    val currentStatus = ctx.session.state["status"] // Guaranteed to be 'processing'
    println("Status after resuming: $currentStatus")
}
// --8<-- [end:state_update_timing]

// --8<-- [start:dirty_read]
/**
 * Conceptual view of dirty reads in Kotlin
 */
fun dirtyRead(ctx: com.google.adk.kt.agents.InvocationContext) {
    // Code in a callback
    ctx.session.state["field_1"] = "value_1"
    // State is locally set to 'value_1', but not yet committed by Runner

    // ... agent runs ...

    // Code in a tool called later *within the same invocation*
    // Readable (dirty read), but 'value_1' isn't guaranteed persistent yet.
    val val1 = ctx.session.state["field_1"] // 'val' will likely be 'value_1' here
    println("Dirty read value in tool: $val1")

    // Assume the event carrying the state_delta={'field_1': 'value_1'}
    // is yielded *after* this tool runs and is processed by the Runner.
}
// --8<-- [end:dirty_read]



