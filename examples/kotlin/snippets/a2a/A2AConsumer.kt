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

package com.google.adk.kt.examples.a2a

import com.google.adk.kt.a2a.jvm.A2AAgent
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import kotlinx.coroutines.runBlocking

fun main() =
    runBlocking {
        // --8<-- [start:remote_agent]
        // A2AAgent is a suspending factory: it fetches the remote agent's card from
        // <url>/.well-known/agent-card.json and reads the name, description and
        // transport from it. The constructor of the returned agent is internal, so
        // this factory is the only way to build one.
        val primeAgent =
            A2AAgent(
                name = "prime_agent",
                agentCardUrl = "http://localhost:9090",
            )
        // --8<-- [end:remote_agent]

        // --8<-- [start:root_agent]
        // The remote agent is a BaseAgent, so it goes in subAgents like any local one.
        // ADK handles the A2A wire protocol from here.
        val rootAgent =
            LlmAgent(
                name = "root_agent",
                model = Gemini(name = "gemini-flash-latest"),
                instruction =
                    Instruction(
                        "Roll dice yourself, and delegate prime checks to prime_agent.",
                    ),
                subAgents = listOf(primeAgent),
            )
        // --8<-- [end:root_agent]

        println("Root agent ${rootAgent.name} delegates to ${primeAgent.name}")
    }
