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

// A loop is a BACK-EDGE in the graph: a downstream node routes back to an
// earlier node, and the engine re-activates that node with a fresh lifecycle on
// each iteration. The loop exits when the critic picks the terminal branch.
//
//   START -> seed_draft -> critic --REVISE--> refine --+
//                            ^                         |
//                            +-------------------------+
//                          critic --DONE--> finalize

// --8<-- [start:loop-escalation]
import com.google.adk.kt.annotations.ExperimentalWorkflowApi
import com.google.adk.kt.workflow.Route
import com.google.adk.kt.workflow.Start
import com.google.adk.kt.workflow.node
import com.google.adk.kt.workflow.workflow

/** The critic is satisfied once the draft has at least this many bullets. */
private const val REQUIRED_BULLETS = 3

// The draft is its list of bullets; the topic is kept in session state.
private val seedDraft =
    node<String, List<String>>("seed_draft") { context, topic ->
        context.updateState("topic", topic.trim())
        listOf("${topic.trim()} — point 1")
    }

private val critic =
    node<List<String>, List<String>>("critic") { context, bullets ->
        val route = if (bullets.size >= REQUIRED_BULLETS) "DONE" else "REVISE"
        context.routes = listOf(Route.Tag(route))
        bullets
    }

private val refine =
    node<List<String>, List<String>>("refine") { context, bullets ->
        bullets + "${context.state["topic"]} — point ${bullets.size + 1}"
    }

private val finalize =
    node<List<String>, String>("finalize") { _, bullets ->
        "Approved after ${bullets.size} bullets:\n" +
            bullets.joinToString("\n") { "  • $it" }
    }

val loopWorkflow =
    workflow("loop_workflow") {
        chain(Start, seedDraft, critic).route {
            "REVISE" then refine
            "DONE" then finalize
        }
        refine.then(critic) // back-edge: loop back for another review
    }
// --8<-- [end:loop-escalation]
