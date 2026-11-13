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

package com.google.adk.kt.examples.tools.builtintools

// --8<-- [start:full_code]
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.sessions.SessionKey
import com.google.adk.kt.tools.GoogleSearchTool
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Part
import kotlinx.coroutines.runBlocking

private const val APP_NAME = "google_search_agent"
private const val USER_ID = "user1234"
private const val SESSION_ID = "1234"

val rootAgent =
    LlmAgent(
        name = "basic_search_agent",
        model = Gemini(name = "gemini-flash-latest"),
        description = "Agent to answer questions using Google Search.",
        instruction =
            Instruction(
                "I can answer your questions by searching the internet. Just ask me anything!",
            ),
        // GoogleSearchTool is a pre-built tool which allows the agent to perform Google searches.
        tools = listOf(GoogleSearchTool()),
    )

// Agent Interaction
suspend fun callAgent(query: String) {
    // Session and Runner
    val sessionService = InMemorySessionService()
    sessionService.createSession(SessionKey(APP_NAME, USER_ID, SESSION_ID))
    val runner = InMemoryRunner(rootAgent, APP_NAME, sessionService)

    val content = Content(role = "user", parts = listOf(Part(text = query)))
    runner.runAsync(
        userId = USER_ID,
        sessionId = SESSION_ID,
        newMessage = content,
    ).collect { event ->
        if (event.isFinalResponse) {
            val finalResponse = event.content?.parts?.firstOrNull()?.text
            println("Agent Response: $finalResponse")
        }
    }
}

fun main() =
    runBlocking {
        callAgent("what's the latest ai news?")
    }
// --8<-- [end:full_code]
