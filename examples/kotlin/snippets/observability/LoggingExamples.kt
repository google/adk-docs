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

package com.google.adk.kt.examples.observability

import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.apps.App
import com.google.adk.kt.plugins.LoggingPlugin
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.telemetry.TelemetryConfig

/** Examples for logging setup in ADK Kotlin. */
suspend fun loggingExamples(agent: LlmAgent) {
    // --8<-- [start:capture_content]
    // Enable full prompt and response logging
    TelemetryConfig.captureMessageContent = true
    // --8<-- [end:capture_content]

    // --8<-- [start:logging_plugin]
    // Use the LoggingPlugin for structured activity logging to the console
    val runner =
        InMemoryRunner(
            App(appName = agent.name, rootAgent = agent, plugins = listOf(LoggingPlugin())),
        )
    // --8<-- [end:logging_plugin]
}
