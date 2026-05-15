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

package com.google.adk.samples.agents.llmauditor

import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Role
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    val runner = InMemoryRunner(agent = LlmAuditorAgent.rootAgent)

    print("You > ")
    val input = readlnOrNull() ?: return@runBlocking
    runner.runAsync(
        userId = "user",
        sessionId = "session",
        newMessage = Content(
            role = Role.USER,
            parts = listOf(Part(text = input)),
        ),
    ).collect { event ->
        val text = event.content?.parts?.firstOrNull()?.text
        if (event.turnComplete && !text.isNullOrBlank()) {
            println("\n${event.author} > $text")
        }
    }
}
