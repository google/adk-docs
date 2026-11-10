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

package com.google.adk.kt.examples.context

import com.google.adk.kt.agents.BaseAgent
import com.google.adk.kt.agents.CallbackContext
import com.google.adk.kt.agents.InvocationContext
import com.google.adk.kt.agents.ReadonlyContext
import com.google.adk.kt.artifacts.ArtifactService
import com.google.adk.kt.callbacks.CallbackChoice
import com.google.adk.kt.events.Event
import com.google.adk.kt.models.LlmRequest
import com.google.adk.kt.models.LlmResponse
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.SessionService
import com.google.adk.kt.tools.ToolContext
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Role
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.io.File
import java.io.FileNotFoundException
import java.util.UUID

suspend fun runWithContext(
    myRootAgent: BaseAgent,
    mySessionService: SessionService,
    myArtifactService: ArtifactService,
    userMessage: Content,
) {
    // --8<-- [start:conceptual_runner_example]
    // How the framework provides context
    // 1. You initialize a Runner with your agent and services
    val runner =
        InMemoryRunner(
            agent = myRootAgent,
            appName = "my_app",
            sessionService = mySessionService,
            artifactService = myArtifactService,
        )

    // 2. You call runAsync with the user input
    // Note: runAsync returns a Flow of Events.
    // The framework internally creates an InvocationContext and passes it
    // implicitly to your agent code, callbacks, and tools.
    runner
        .runAsync(
            userId = "user123",
            sessionId = "session456",
            newMessage = userMessage,
        ).collect { event ->
            println(event.contentText())
        }

    // As a developer, you work with the context objects provided in method arguments.
    // --8<-- [end:conceptual_runner_example]
}

// --8<-- [start:invocation_context_agent]
// Agent implementation receiving InvocationContext
class MyAgent(
    name: String,
) : BaseAgent(name = name) {
    override fun runAsyncImpl(context: InvocationContext): Flow<Event> =
        flow {
            // Direct access example
            val agentName = context.agent.name
            val sessionId = context.session.key.id
            println(
                "Agent $agentName running in session $sessionId " +
                    "for invocation ${context.invocationId}",
            )
            // ... agent logic using context ...
            // emit(...) // ... event ...
        }
}
// --8<-- [end:invocation_context_agent]

// --8<-- [start:readonly_context_instruction]
// Example: Instruction provider receiving ReadonlyContext
fun myInstructionProvider(context: ReadonlyContext): Content {
    // Read-only access example
    // The state property is a read-only Map snapshot of the session state
    val userTier = context.state["user_tier"] as? String ?: "standard"
    // context.state["new_key"] = "value" // Does not compile: Map has no set operator
    return Content(parts = listOf(Part(text = "Process the request for a $userTier user.")))
}
// --8<-- [end:readonly_context_instruction]

// --8<-- [start:callback_context_callback]
// Example: Callback receiving CallbackContext
suspend fun myBeforeModelCb(
    context: CallbackContext,
    request: LlmRequest,
): CallbackChoice<LlmRequest, LlmResponse> {
    // Read/Write state example
    val callCount = context.state["model_calls"] as? Int ?: 0
    context.updateState("model_calls", callCount + 1) // Modify state (tracks delta)

    // Optionally load an artifact
    // val configPart = context.loadArtifact("model_config.json")
    println("Preparing model call #${callCount + 1} for invocation ${context.invocationId}")
    return CallbackChoice.Continue(request) // Allow model call to proceed
}
// --8<-- [end:callback_context_callback]

// --8<-- [start:tool_context_tool]
// Example: Tool function receiving ToolContext
// Assume this function is wrapped by a FunctionTool
fun searchExternalApi(
    query: String,
    toolContext: ToolContext,
): Map<String, Any> {
    val apiKey = toolContext.state["api_key"] as? String
    if (apiKey.isNullOrEmpty()) {
        return mapOf("status" to "Auth Required")
    }

    // Use the API key...
    println(
        "Tool executing for query '$query' using API key. " +
            "Invocation: ${toolContext.invocationId}",
    )

    // Optionally search memory or list artifacts
    // val relevantDocs = toolContext.memoryService?.searchMemory(
    //     toolContext.session.key.appName, toolContext.userId, "info related to $query")
    // val availableFiles = toolContext.listArtifacts()

    return mapOf("result" to "Data for $query fetched.")
}
// --8<-- [end:tool_context_tool]

// --8<-- [start:accessing_state_tool]
// Example: In a Tool function
fun myTool(toolContext: ToolContext) {
    val userPref = toolContext.state["user_display_preference"] as? String ?: "default_mode"
    val apiEndpoint = toolContext.state["app:api_endpoint"] // Read app-level state

    if (userPref == "dark_mode") {
        // ... apply dark mode logic ...
    }
    println("Using API endpoint: $apiEndpoint")
    // ... rest of tool logic ...
}
// --8<-- [end:accessing_state_tool]

// --8<-- [start:accessing_state_callback]
// Example: In a Callback function
fun myCallback(context: CallbackContext) {
    val lastToolResult = context.state["temp:last_api_result"] // Read temporary state
    if (lastToolResult != null) {
        println("Found temporary result from last tool: $lastToolResult")
    }
    // ... callback logic ...
}
// --8<-- [end:accessing_state_callback]

// --8<-- [start:accessing_ids]
// Example: In any context (ToolContext shown)
fun logToolUsage(toolContext: ToolContext) {
    val agentName = toolContext.agentName
    val invId = toolContext.invocationId
    val funcCallId = toolContext.functionCallId ?: "N/A" // Set only during a tool call

    println("Log: Invocation=$invId, Agent=$agentName, FunctionCallID=$funcCallId - Tool Executed.")
}
// --8<-- [end:accessing_ids]

// --8<-- [start:accessing_initial_user_input]
// Example: In a Callback
fun checkInitialIntent(context: CallbackContext) {
    var initialText = "N/A"
    val parts = context.userContent?.parts
    if (!parts.isNullOrEmpty()) {
        initialText = parts[0].text ?: "Non-text input"
    }

    println("This invocation started with user input: '$initialText'")
}

// Example: In an Agent's runAsyncImpl
// override fun runAsyncImpl(context: InvocationContext): Flow<Event> = flow {
//     val initialText = context.userContent?.parts?.firstOrNull()?.text
//     if (initialText != null) {
//         println("Agent logic remembering initial query: $initialText")
//     }
//     ...
// }
// --8<-- [end:accessing_initial_user_input]

// --8<-- [start:passing_data_tool1]
// Example: Tool 1 - Fetches user ID
fun getUserProfile(toolContext: ToolContext): Map<String, Any> {
    val userId = UUID.randomUUID().toString() // Simulate fetching ID
    // Save the ID to state for the next tool
    toolContext.updateState("temp:current_user_id", userId)
    return mapOf("profile_status" to "ID generated")
}
// --8<-- [end:passing_data_tool1]

// --8<-- [start:passing_data_tool2]
// Example: Tool 2 - Uses user ID from state
fun getUserOrders(toolContext: ToolContext): Map<String, Any> {
    val userId =
        toolContext.state["temp:current_user_id"] as? String
            ?: return mapOf("error" to "User ID not found in state")

    println("Fetching orders for user ID: $userId")
    // ... logic to fetch orders using userId ...
    return mapOf("orders" to listOf("order123", "order456"))
}
// --8<-- [end:passing_data_tool2]

// --8<-- [start:updating_preferences]
// Example: Tool or Callback identifies a preference
fun setUserPreference(
    // Or CallbackContext
    toolContext: ToolContext,
    preference: String,
    value: String,
): Map<String, Any> {
    // Use 'user:' prefix for user-level state (if using a persistent SessionService)
    val stateKey = "user:$preference"
    toolContext.updateState(stateKey, value)
    println("Set user preference '$preference' to '$value'")
    return mapOf("status" to "Preference updated")
}
// --8<-- [end:updating_preferences]

// --8<-- [start:artifacts_save_ref]
// Example: In a callback or initial tool
suspend fun saveDocumentReference(
    // Or ToolContext
    context: CallbackContext,
    filePath: String,
) {
    // Assume filePath is something like "gs://my-bucket/docs/report.pdf" or "/local/path/to/report.pdf"
    try {
        // Create a Part containing the path/URI text
        val artifactPart = Part(text = filePath)
        val version = context.saveArtifact("document_to_summarize.txt", artifactPart)
        println("Saved document reference '$filePath' as artifact version $version")
        // Store the filename in state if needed by other tools
        context.updateState("temp:doc_artifact_name", "document_to_summarize.txt")
    } catch (e: IllegalStateException) {
        println("Error saving artifact: ${e.message}") // E.g., Artifact service not configured
    } catch (e: Exception) {
        println("Unexpected error saving artifact reference: $e")
    }
}

// Example usage:
// saveDocumentReference(context, "gs://my-bucket/docs/report.pdf")
// --8<-- [end:artifacts_save_ref]

// --8<-- [start:artifacts_summarize]
// Example: In the Summarizer tool function
// Assume a GCS client library is available
// Assume a summarizeText function exists
suspend fun summarizeDocumentTool(toolContext: ToolContext): Map<String, Any> {
    val artifactName =
        toolContext.state["temp:doc_artifact_name"] as? String
            ?: return mapOf("error" to "Document artifact name not found in state.")

    // 1. Load the artifact part containing the path/URI
    // Returns null if no artifact service is configured or the artifact is not found
    val artifactPart = toolContext.loadArtifact(artifactName)
    val filePath =
        artifactPart?.text
            ?: return mapOf(
                "error" to "Could not load artifact or artifact has no text path: $artifactName",
            )
    println("Loaded document reference: $filePath")

    try {
        // 2. Read the actual document content (outside ADK context)
        var documentContent = ""
        if (filePath.startsWith("gs://")) {
            // Example: Use GCS client library to download/read
            // Replace with actual GCS reading logic
        } else if (filePath.startsWith("/")) {
            // Example: Use local file system
            documentContent = File(filePath).readText(Charsets.UTF_8)
        } else {
            return mapOf("error" to "Unsupported file path scheme: $filePath")
        }

        // 3. Summarize the content
        if (documentContent.isEmpty()) {
            return mapOf("error" to "Failed to read document content.")
        }

        // val summary = summarizeText(documentContent) // Call your summarization logic
        val summary = "Summary of content from $filePath" // Placeholder

        return mapOf("summary" to summary)
    } catch (e: FileNotFoundException) {
        return mapOf("error" to "Local file not found: $filePath")
    }
}
// --8<-- [end:artifacts_summarize]

// --8<-- [start:artifacts_list]
// Example: In a tool function
suspend fun checkAvailableDocs(toolContext: ToolContext): Map<String, Any> {
    // Returns an empty list if no artifact service is configured
    val artifactKeys = toolContext.listArtifacts()
    println("Available artifacts: $artifactKeys")
    return mapOf("available_docs" to artifactKeys)
}
// --8<-- [end:artifacts_list]

// --8<-- [start:memory_search]
// Example: Tool using memory search
suspend fun findRelatedInfo(
    toolContext: ToolContext,
    topic: String,
): Map<String, String> {
    val memoryService =
        toolContext.memoryService
            ?: return mapOf("error" to "Memory service error: not configured")
    return try {
        val searchResults =
            memoryService.searchMemory(
                appName = toolContext.session.key.appName,
                userId = toolContext.userId,
                query = "Information about $topic",
            )
        if (searchResults.memories.isNotEmpty()) {
            println("Found ${searchResults.memories.size} memory results for '$topic'")
            // Process searchResults.memories (which are MemoryEntry objects)
            val topEntry = searchResults.memories[0]
            val topResultText = topEntry.content.parts.firstNotNullOfOrNull { it.text } ?: ""
            mapOf("memory_snippet" to topResultText)
        } else {
            mapOf("message" to "No relevant memories found.")
        }
    } catch (e: Exception) {
        mapOf("error" to "Unexpected error searching memory: $e")
    }
}
// --8<-- [end:memory_search]

// --8<-- [start:advanced_invocation_context]
// Example: Inside agent's runAsyncImpl
class MyControllingAgent(
    name: String,
) : BaseAgent(name = name) {
    override fun runAsyncImpl(context: InvocationContext): Flow<Event> =
        flow {
            // Example: Check if a specific service is available
            if (context.memoryService == null) {
                println("Memory service is not available for this invocation.")
                // Potentially change agent behavior
            }

            // Example: Early termination based on some condition
            if (context.session.state["critical_error_flag"] == true) {
                println("Critical error detected, ending invocation.")
                context.isEndOfInvocation = true // Signal framework to stop processing
                emit(
                    Event(
                        author = name,
                        invocationId = context.invocationId,
                        content =
                            Content(
                                role = Role.MODEL,
                                parts = listOf(Part(text = "Stopping due to critical error.")),
                            ),
                    ),
                )
                return@flow // Stop this agent's execution
            }

            // ... Normal agent processing ...
            // emit(...) // ... event ...
        }
}
// --8<-- [end:advanced_invocation_context]
