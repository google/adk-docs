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

// A `JoinNode` is a fan-in barrier: it waits for EVERY predecessor to finish
// and then hands the next node a map keyed by predecessor node name.

// --8<-- [start:fan-out-join]
import com.google.adk.kt.annotations.ExperimentalWorkflowApi
import com.google.adk.kt.workflow.JoinNode
import com.google.adk.kt.workflow.Start
import com.google.adk.kt.workflow.node
import com.google.adk.kt.workflow.workflow

private val parallelTaskA =
    node<String, String>("parallel_task_A") { _, text -> text.uppercase() }

private val parallelTaskB =
    node<String, Int>("parallel_task_B") { _, text -> text.length }

private val parallelTaskC =
    node<String, String>("parallel_task_C") { _, text -> text.reversed() }

private val myJoinNode = JoinNode("my_join_node")

private val finalTaskD =
    node<Map<String, Any?>, String>("final_task_D") { _, results ->
        listOf(
            "Uppercase: ${results["parallel_task_A"]}",
            "Length:    ${results["parallel_task_B"]}",
            "Reversed:  ${results["parallel_task_C"]}",
        ).joinToString("\n")
    }

val fanOutWorkflow =
    workflow("fan_out_workflow") {
        Start.then(parallelTaskA, parallelTaskB, parallelTaskC)
            .joinTo(myJoinNode)
            .then(finalTaskD)
    }
// --8<-- [end:fan-out-join]
