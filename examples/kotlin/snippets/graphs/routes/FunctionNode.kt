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

// The simplest node type: a plain function wrapped as a FunctionNode. It takes
// text in, returns text out, and the framework hands that value to the next
// node as its input. No session-state writes needed.

// --8<-- [start:function-node]
import com.google.adk.kt.annotations.ExperimentalWorkflowApi
import com.google.adk.kt.workflow.Start
import com.google.adk.kt.workflow.node
import com.google.adk.kt.workflow.workflow

// The returned value becomes the node's output.
private val myFunctionNode =
    node<String, String>("my_function_node") { _, nodeInput ->
        val inputTextModified = nodeInput.uppercase()
        inputTextModified
    }

// The successor receives my_function_node's output as its typed input.
private val addSuffix =
    node<String, String>("add_suffix") { _, nodeInput ->
        "$nodeInput IS AWESOME!"
    }

val functionNodePipeline =
    workflow("function_node_pipeline") {
        chain(Start, myFunctionNode, addSuffix)
    }
// --8<-- [end:function-node]
