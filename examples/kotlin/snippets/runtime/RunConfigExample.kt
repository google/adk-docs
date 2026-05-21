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

package com.google.adk.kt.examples.runtime

import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.agents.ResumabilityConfig
import com.google.adk.kt.agents.RunConfig
import com.google.adk.kt.agents.StreamingMode
import com.google.adk.kt.annotations.ExperimentalResumabilityFeature
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Role
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.runBlocking

// --8<-- [start:basic_usage]
val config =
    RunConfig(
        streamingMode = StreamingMode.SSE,
    )

// Pass it to runner.runAsync
// runner.runAsync(..., runConfig = config)
// --8<-- [end:basic_usage]

// --8<-- [start:full_example]
fun runWithConfig(runner: InMemoryRunner) =
    runBlocking {
        val config =
            RunConfig(
                streamingMode = StreamingMode.SSE,
                customMetadata = mapOf("priority" to "high"),
            )

        runner
            .runAsync(
                userId = "user123",
                sessionId = "session456",
                newMessage = Content.fromText(Role.USER, "Hello!"),
                runConfig = config,
            ).collect { event ->
                // handle events
            }
    }
// --8<-- [end:full_example]

// --8<-- [start:custom_metadata]
val metadataConfig =
    RunConfig(
        customMetadata = mapOf("user_tier" to "premium"),
    )
// --8<-- [end:custom_metadata]

// --8<-- [start:streaming_config]
val streamingConfig =
    RunConfig(
        streamingMode = StreamingMode.SSE,
    )
// --8<-- [end:streaming_config]

private val rootAgent =
    LlmAgent(name = "my_agent", model = Gemini(name = "gemini-flash-latest"))

// --8<-- [start:resumability_config]
@OptIn(ExperimentalResumabilityFeature::class)
val runner =
    InMemoryRunner(
        agent = rootAgent,
        appName = "my_resumable_agent",
        sessionService = InMemorySessionService(),
        resumabilityConfig = ResumabilityConfig(isResumable = true),
    )
// --8<-- [end:resumability_config]

// --8<-- [start:resume_usage]
fun resumeAgent(runner: InMemoryRunner) =
    runBlocking {
        runner
            .runAsync(
                userId = "user123",
                sessionId = "session456",
                invocationId = "previous-invocation-id",
            ).collect { event ->
                // resume execution from previous state
            }
    }
// --8<-- [end:resume_usage]
