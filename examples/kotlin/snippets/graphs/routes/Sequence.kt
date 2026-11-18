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

// A sequential route runs each node once, in the listed order. Each node's
// return value is delivered to the next node as its input.

// --8<-- [start:sequence]
import com.google.adk.kt.annotations.ExperimentalWorkflowApi
import com.google.adk.kt.workflow.Start
import com.google.adk.kt.workflow.node
import com.google.adk.kt.workflow.workflow

private val taskANode =
    node<String, String>("task_A_node") { _, nodeInput ->
        "Summary: ${nodeInput.trim()}"
    }

private val taskBNode =
    node<String, String>("task_B_node") { _, summary ->
        summary.uppercase()
    }

private val taskCNode =
    node<String, String>("task_C_node") { _, shouted ->
        "$shouted (done)"
    }

val sequentialWorkflow =
    workflow("sequential_workflow") {
        chain(Start, taskANode, taskBNode, taskCNode)
    }
// --8<-- [end:sequence]
