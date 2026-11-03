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

// A sequential graph workflow that alternates between model reasoning and plain
// code: an agent names a random city, a code function looks up the time there,
// a second agent reports it, and a final function appends a completion message.

// --8<-- [start:get-started]
@file:OptIn(ExperimentalWorkflowApi::class)

package com.google.adk.kt.examples.graphs.getstarted

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.ExperimentalWorkflowApi
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Role
import com.google.adk.kt.types.Schema
import com.google.adk.kt.types.Type
import com.google.adk.kt.workflow.Start
import com.google.adk.kt.workflow.emit
import com.google.adk.kt.workflow.node
import com.google.adk.kt.workflow.workflow

val cityGeneratorAgent =
    LlmAgent(
        name = "city_generator_agent",
        model = Gemini(name = "gemini-flash-latest"),
        instruction =
            Instruction(
                """Return the name of a random city.
                  Return only the name, nothing else.""",
            ),
    )

// The structured payload handed from the lookup node to the report agent.
val cityTimeSchema =
    Schema(
        type = Type.OBJECT,
        properties =
            mapOf(
                "time_info" to Schema(type = Type.STRING, description = "Time information."),
                "city" to Schema(type = Type.STRING, description = "City name."),
            ),
        required = listOf("time_info", "city"),
    )

// Simulate returning the current time in the specified city.
val lookupTimeFunction =
    node<String, Map<String, String>>(
        name = "lookup_time_function",
        outputSchema = cityTimeSchema,
    ) { _, nodeInput ->
        mapOf("time_info" to "10:10 AM", "city" to nodeInput.trim())
    }

// The lookup result arrives as this agent's input, as JSON text.
val cityReportAgent =
    LlmAgent(
        name = "city_report_agent",
        model = Gemini(name = "gemini-flash-latest"),
        inputSchema = cityTimeSchema,
        instruction =
            Instruction(
                """Output following line, using the time_info and city from the input:
                It is <time_info> in <city> right now.""",
            ),
    )

val completedMessageFunction =
    node<String, Unit>("completed_message_function") { _, nodeInput ->
        emit(Content.fromText(Role.MODEL, "$nodeInput\n WORKFLOW COMPLETED."))
    }

val rootAgent =
    workflow("root_agent") {
        chain(
            Start,
            cityGeneratorAgent,
            lookupTimeFunction,
            cityReportAgent,
            completedMessageFunction,
        )
    }
// --8<-- [end:get-started]
