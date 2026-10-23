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

package com.google.adk.kt.examples.tools.overview

// --8<-- [start:full_code]

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.sessions.SessionKey
import com.google.adk.kt.tools.ToolContext
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Role
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking

private const val APP_NAME = "customer_support_agent"
private const val USER_ID = "user1234"
private const val SESSION_ID = "1234"

class EscalationTools {
    /**
     * Checks if the query requires escalation and transfers to another agent if needed.
     */
    @Tool
    fun checkAndTransfer(
        @Param("The user query to triage.") query: String,
        context: ToolContext,
    ): String =
        if ("urgent" in query.lowercase()) {
            println("Tool: Detected urgency, transferring to the support agent.")
            // Setting transferToAgent on the actions hands control to the named
            // agent once this tool returns.
            context.actions.transferToAgent = "support_agent"
            "Transferring to the support agent..."
        } else {
            "Processed query: '$query'. No further action needed."
        }
}

fun main() =
    runBlocking {
        val supportAgent =
            LlmAgent(
                name = "support_agent",
                model = Gemini(name = "gemini-flash-latest"),
                instruction =
                    Instruction(
                        "You are the dedicated support agent. Mention that you are a " +
                            "support handler and help the user with their urgent issue.",
                    ),
            )

        val mainAgent =
            LlmAgent(
                name = "main_agent",
                model = Gemini(name = "gemini-flash-latest"),
                instruction =
                    Instruction(
                        "You are the first point of contact for customer support of an " +
                            "analytics tool. Answer general queries. If the user indicates " +
                            "urgency, use the checkAndTransfer tool.",
                    ),
                tools = EscalationTools().generatedTools(),
                subAgents = listOf(supportAgent),
            )

        val sessionService = InMemorySessionService()
        val runner =
            InMemoryRunner(
                agent = mainAgent,
                appName = APP_NAME,
                sessionService = sessionService,
            )
        sessionService.createSession(
            SessionKey(APP_NAME, USER_ID, SESSION_ID),
        )

        val query = "this is urgent, i cant login"
        val userContent = Content(role = Role.USER, parts = listOf(Part(text = query)))

        val events =
            runner.runAsync(
                userId = USER_ID,
                sessionId = SESSION_ID,
                newMessage = userContent,
            ).toList()

        for (event in events) {
            if (event.isFinalResponse) {
                println("Agent Response: ${event.content?.parts?.firstOrNull()?.text}")
            }
        }
    }
// --8<-- [end:full_code]
