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

// Branching is a node that selects a route, plus a routing map from each route
// value to the node that handles it. A branch target can be anything node-like:
// `taskBNode` here is an `LlmAgent`, `taskCNode` a function node.

// --8<-- [start:branches]
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.ExperimentalWorkflowApi
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.workflow.Route
import com.google.adk.kt.workflow.Start
import com.google.adk.kt.workflow.node
import com.google.adk.kt.workflow.workflow

private val taskANode =
    node<String, String>("task_A_node") { _, nodeInput -> nodeInput.trim() }

/** Stands in for an application-specific branch condition. */
private fun condition(nodeInput: String) = nodeInput.any { it.isDigit() }

/** Routes to task B or C based on nodeInput. */
private val router =
    node<String, String>("router") { context, nodeInput ->
        val route = if (condition(nodeInput)) "RUN_TASK_C" else "RUN_TASK_B"
        context.routes = listOf(Route.Tag(route))
        nodeInput
    }

private val taskBNode =
    LlmAgent(
        name = "task_B_agent",
        model = Gemini(name = "gemini-flash-latest"),
        instruction = Instruction("Answer the user in a single short sentence."),
    )

private val taskCNode =
    node<Any?, String>("task_C_node") { _, _ -> "Task C completed" }

val routingWorkflow =
    workflow("routing_workflow") {
        chain(Start, taskANode, router).route {
            // "route value" then nodeToRun
            "RUN_TASK_B" then taskBNode
            "RUN_TASK_C" then taskCNode
        }
    }
// --8<-- [end:branches]
