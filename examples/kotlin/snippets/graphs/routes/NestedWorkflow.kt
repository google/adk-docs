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

@file:OptIn(ExperimentalWorkflowApi::class)

package com.google.adk.kt.examples.graphs.routes

// A `Workflow` is itself a node, so you can use one inside another workflow's
// edges to encapsulate a reusable sub-process.

// --8<-- [start:nested-workflow]
import com.google.adk.kt.annotations.ExperimentalWorkflowApi
import com.google.adk.kt.workflow.Route
import com.google.adk.kt.workflow.Start
import com.google.adk.kt.workflow.node
import com.google.adk.kt.workflow.workflow

private val taskA1 =
    node<String, String>("task_A1") { _, nodeInput -> nodeInput.trim() }

private val router =
    node<String, String>("router") { context, text ->
        val route = if (text == text.uppercase()) "RUN_WORKFLOW_C" else "RUN_WORKFLOW_B"
        context.routes = listOf(Route.Tag(route))
        text
    }

/** Upper-cases the first letter of each word. */
private fun titleCase(text: String) =
    text.split(" ").joinToString(" ") { word -> word.replaceFirstChar { it.titlecase() } }

private val workflowB =
    workflow("workflow_B") {
        chain(
            Start,
            node<String, String>("b_title_case") { _, text -> titleCase(text) },
            node<String, String>("b_frame") { _, text -> "[B] $text" },
        )
    }

private val workflowC =
    workflow("workflow_C") {
        chain(
            Start,
            node<String, String>("c_lower_case") { _, text -> text.lowercase() },
            node<String, String>("c_frame") { _, text -> "[C] $text" },
        )
    }

val parentWorkflow =
    workflow("parent_workflow") {
        chain(Start, taskA1, router).route {
            "RUN_WORKFLOW_B" then workflowB
            "RUN_WORKFLOW_C" then workflowC
        }
    }
// --8<-- [end:nested-workflow]
