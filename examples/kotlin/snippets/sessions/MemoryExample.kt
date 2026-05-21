package com.google.adk.kt.examples.sessions

import com.google.adk.kt.agents.CallbackContext
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.callbacks.AfterAgentCallback
import com.google.adk.kt.callbacks.CallbackChoice
import com.google.adk.kt.memory.InMemoryMemoryService
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.sessions.SessionKey
import com.google.adk.kt.tools.LoadMemoryTool
import com.google.adk.kt.tools.PreloadMemoryTool
import com.google.adk.kt.tools.ToolContext
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Role
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.runBlocking

/**
 * This example demonstrates the basic flow using the `InMemoryMemoryService` in Kotlin.
 * It shows how to capture information in one session, add it to memory, and recall it in another.
 */
// --8<-- [start:full_example]
fun main() =
    runBlocking {
        // --- Constants ---
        val appName = "memory_example_app"
        val userId = "mem_user"
        val model = Gemini(name = "gemini-flash-latest")

        // --- Agent Definitions ---

        // Agent 1: Simple agent to capture information
        val infoCaptureAgent =
            LlmAgent(
                name = "InfoCaptureAgent",
                model = model,
                instruction = Instruction("Acknowledge the user's statement."),
            )

        // Agent 2: Agent that can use memory
        val memoryRecallAgent =
            LlmAgent(
                name = "MemoryRecallAgent",
                model = model,
                instruction =
                    Instruction(
                        "Answer the user's question. Use the 'load_memory' tool " +
                            "if the answer might be in past conversations.",
                    ),
                tools = listOf(LoadMemoryTool()), // Give the agent the tool
            )

        // --- Services ---
        // Services must be shared across runners to share state and memory
        val sessionService = InMemorySessionService()
        val memoryService = InMemoryMemoryService()

        // --- Turn 1: Capturing Information ---
        println("--- Turn 1: Capturing Information ---")
        val runner1 =
            InMemoryRunner(
                agent = infoCaptureAgent,
                appName = appName,
                sessionService = sessionService,
                memoryService = memoryService,
            )
        val sessionId1 = "session_info"
        val userInput1 = Content.fromText(Role.USER, "My favorite project is Project Alpha.")

        // Run the agent
        runner1
            .runAsync(
                userId = userId,
                sessionId = sessionId1,
                newMessage = userInput1,
            ).collect { event ->
                event.content?.parts?.forEach { part ->
                    if (!part.text.isNullOrBlank()) {
                        println("Agent Response: ${part.text}")
                    }
                }
            }

        // Get the completed session using SessionKey
        val session1 = sessionService.getSession(SessionKey(appName, userId, sessionId1))

        // Add this session's content to the Memory Service
        println("\n--- Adding Session 1 to Memory ---")
        if (session1 != null) {
            memoryService.addSessionToMemory(session1)
            println("Session added to memory.")
        }

        // --- Turn 2: Recalling Information ---
        println("\n--- Turn 2: Recalling Information ---")
        val runner2 =
            InMemoryRunner(
                agent = memoryRecallAgent,
                appName = appName,
                sessionService = sessionService, // Reuse the same service
                memoryService = memoryService, // Reuse the same service
            )
        val sessionId2 = "session_recall"
        val userInput2 = Content.fromText(Role.USER, "What is my favorite project?")

        // Run the second agent
        runner2
            .runAsync(
                userId = userId,
                sessionId = sessionId2,
                newMessage = userInput2,
            ).collect { event ->
                event.content?.parts?.forEach { part ->
                    if (!part.text.isNullOrBlank()) {
                        println("Agent Response: ${part.text}")
                    }
                }
            }
    }
// --8<-- [end:full_example]

// --8<-- [start:instantiate_service]
fun instantiateMemoryService() {
    val memoryService = InMemoryMemoryService()
}
// --8<-- [end:instantiate_service]

// --8<-- [start:search_within_tool]
suspend fun searchWithinTool(
    context: ToolContext,
    args: Map<String, Any>,
): String {
    val query = args["query"] as String
    val response =
        context.invocationContext.memoryService?.searchMemory(
            appName = context.invocationContext.session.key.appName,
            userId = context.invocationContext.session.key.userId,
            query = query,
        )
    // process response
    return response?.memories?.joinToString("\n") {
        it.content.parts.joinToString(" ") { p -> p.text ?: "" }
    } ?: ""
}
// --8<-- [end:search_within_tool]

// --8<-- [start:preload_memory_agent]
fun preloadMemoryAgent(model: Gemini) {
    val agent =
        LlmAgent(
            model = model,
            name = "weather_sentiment_agent",
            instruction = Instruction("..."),
            tools = listOf(PreloadMemoryTool()),
        )
}
// --8<-- [end:preload_memory_agent]

// --8<-- [start:auto_save_callback]

// --8<-- [start:multi_memory]

/**
 * Example of using two memory services in Kotlin.
 */
suspend fun searchAllMemory(
    toolContext: ToolContext,
    query: String,
    docsMemory: InMemoryMemoryService,
): Map<String, List<String>> {
    // Search the conversational memory (configured in the runner)
    val conversational =
        toolContext.invocationContext.memoryService?.searchMemory(
            appName = toolContext.invocationContext.session.key.appName,
            userId = toolContext.invocationContext.session.key.userId,
            query = query,
        )

    // Search a separate docs knowledge base
    val docs =
        docsMemory.searchMemory(
            appName = "docs",
            userId = "shared",
            query = query,
        )

    return mapOf(
        "from_conversations" to
            (
                conversational?.memories?.map {
                    it.content.parts.joinToString(" ") { p -> p.text ?: "" }
                } ?: emptyList()
            ),
        "from_docs" to
            docs.memories.map {
                it.content.parts.joinToString(" ") { p -> p.text ?: "" }
            },
    )
}

fun multiMemoryAgent(model: Gemini) {
    // docs_memory could be any MemoryService implementation
    val docsMemory = InMemoryMemoryService()

    val agent =
        LlmAgent(
            model = model,
            name = "multi_memory_agent",
            instruction =
                Instruction(
                    "Answer questions using both your conversation history and the " +
                        "docs knowledge base. Use the search_all_memory tool.",
                ),
            // In a real app, you'd wrap searchAllMemory in a @Tool annotated class
            // and pass docsMemory to its constructor.
        )
}
// --8<-- [end:multi_memory]

suspend fun autoSaveSessionToMemoryCallback(
    context: CallbackContext,
): CallbackChoice<Unit, Content> {
    context.addSessionToMemory()
    return CallbackChoice.Continue(Unit)
}

fun agentWithCallback(model: Gemini) {
    val agent =
        LlmAgent(
            model = model,
            name = "Generic_QA_Agent",
            instruction = Instruction("Answer the user's questions"),
            tools = listOf(PreloadMemoryTool()),
            afterAgentCallbacks = listOf(AfterAgentCallback(::autoSaveSessionToMemoryCallback)),
        )
}
// --8<-- [end:auto_save_callback]
