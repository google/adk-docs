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

// A prompt-based agent turned into a graph: one agent classifies the message,
// a router node emits the categories as routes, and the graph dispatches to the
// matching handler(s). Because the classifier may return more than one
// category, the router emits a list of routes, and every matching branch runs.

// --8<-- [start:process-pipeline]
@file:OptIn(ExperimentalWorkflowApi::class)

package com.google.adk.kt.examples.graphs.processpipeline

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.ExperimentalWorkflowApi
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Role
import com.google.adk.kt.workflow.Route
import com.google.adk.kt.workflow.Start
import com.google.adk.kt.workflow.emit
import com.google.adk.kt.workflow.node
import com.google.adk.kt.workflow.workflow

val processMessage =
    LlmAgent(
        name = "process_message",
        model = Gemini(name = "gemini-flash-latest"),
        instruction =
            Instruction(
                """
                Classify user message into either "BUG", "CUSTOMER_SUPPORT",
                or "LOGISTICS". If you think a message applies to more than one category,
                reply with a comma separated list of categories.
                """.trimIndent(),
            ),
    )

val router =
    node<String, Unit>("router") { context, nodeInput ->
        context.routes = nodeInput.split(",").map { Route.Tag(it.trim()) }
    }

val response1Bug =
    node<Any?, Unit>("response_1_bug") { _, _ ->
        emit(Content.fromText(Role.MODEL, "Handling bug..."))
    }

val response2Support =
    node<Any?, Unit>("response_2_support") { _, _ ->
        emit(Content.fromText(Role.MODEL, "Handling customer support..."))
    }

val response3Logistics =
    node<Any?, Unit>("response_3_logistics") { _, _ ->
        emit(Content.fromText(Role.MODEL, "Handling logistics..."))
    }

val rootAgent =
    workflow("routing_workflow") {
        chain(Start, processMessage, router)
        router.route {
            "BUG" then response1Bug
            "CUSTOMER_SUPPORT" then response2Support
            "LOGISTICS" then response3Logistics
        }
    }
// --8<-- [end:process-pipeline]
