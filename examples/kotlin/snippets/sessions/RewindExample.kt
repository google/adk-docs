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

package com.google.adk.kt.examples.sessions

import com.google.adk.kt.agents.BaseAgent
import com.google.adk.kt.events.Event
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.sessions.SessionKey
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Role
import kotlinx.coroutines.flow.toList

private const val APP_NAME = "rewind_app"
private const val USER_ID = "user123"

// --8<-- [start:rewind_session]
suspend fun rewindSession(rootAgent: BaseAgent) {
    val sessionService = InMemorySessionService()
    val runner =
        InMemoryRunner(agent = rootAgent, appName = APP_NAME, sessionService = sessionService)

    // Create a session. The service assigns the id, which is held on Session.key.
    val session = sessionService.createSession(SessionKey(APP_NAME, USER_ID, id = null))
    val sessionId = checkNotNull(session.key.id)

    // Call the agent
    callAgent(runner, sessionId, "set state color to red")
    // ... more agent calls ...
    val events = callAgent(runner, sessionId, "update state color to blue")

    // Get the invocation id of the request to undo
    val rewindInvocationId = events[1].invocationId ?: return

    // Rewind invocations (state color: red)
    runner.rewindAsync(
        userId = USER_ID,
        sessionId = sessionId,
        rewindBeforeInvocationId = rewindInvocationId,
    )
}

private suspend fun callAgent(
    runner: InMemoryRunner,
    sessionId: String,
    query: String,
): List<Event> =
    runner
        .runAsync(
            userId = USER_ID,
            sessionId = sessionId,
            newMessage = Content(role = Role.USER, parts = listOf(Part(text = query))),
        ).toList()
// --8<-- [end:rewind_session]
