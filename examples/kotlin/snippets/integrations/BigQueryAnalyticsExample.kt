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

package com.google.adk.kt.examples.integrations

// --8<-- [start:quickstart]
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.apps.App
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin
import com.google.adk.kt.plugins.agentanalytics.BigQueryLoggerConfig

val analyticsAgent =
    LlmAgent(
        name = "my_agent",
        model = Gemini(name = "gemini-flash-latest"),
        instruction = Instruction("You are a helpful assistant."),
    )

/**
 * Wraps [analyticsAgent] in an [App] whose invocations are logged to BigQuery.
 *
 * The plugin creates the day-partitioned table on first use, so the credentials
 * in scope need permission to create a table in the dataset, not only to insert
 * rows. Without explicit `credentials`, application default credentials are used.
 *
 * Logging failures never fail the turn: a table that cannot be created, or a row
 * that cannot be inserted, is logged and the invocation carries on.
 */
fun analyticsApp(
    projectId: String,
    datasetId: String,
    datasetLocation: String,
): App {
    val plugin =
        BigQueryAgentAnalyticsPlugin(
            config =
                BigQueryLoggerConfig(
                    projectId = projectId,
                    datasetId = datasetId,
                    // Defaults to "US"; pass your dataset's location instead.
                    location = datasetLocation,
                ),
        )

    return App(
        appName = "my_agent",
        rootAgent = analyticsAgent,
        plugins = listOf(plugin),
    )
}
// --8<-- [end:quickstart]
