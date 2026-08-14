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

package com.google.adk.kt.examples.plugins

import com.google.adk.kt.agents.CallbackContext
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.callbacks.CallbackChoice
import com.google.adk.kt.events.EventActions
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.models.LlmRequest
import com.google.adk.kt.models.LlmResponse
import com.google.adk.kt.plugins.Plugin
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.types.Content

// --8<-- [start:create_plugin]

/** A custom plugin that counts agent runs and LLM requests. */
class CountInvocationPlugin : Plugin {
    override val name = "count_invocation"

    var agentCount = 0
        private set

    var llmRequestCount = 0
        private set

    // Plugin declares one abstract member, `name`; every callback has a default,
    // so a plugin only overrides the ones it cares about.
    override suspend fun beforeAgent(
        context: CallbackContext,
    ): CallbackChoice<EventActions, Content> {
        agentCount++
        println("[Plugin] Agent run count: $agentCount")
        return CallbackChoice.Continue(EventActions())
    }

    override suspend fun beforeModel(
        context: CallbackContext,
        request: LlmRequest,
    ): CallbackChoice<LlmRequest, LlmResponse> {
        llmRequestCount++
        println("[Plugin] LLM request count: $llmRequestCount")
        return CallbackChoice.Continue(request)
    }
}
// --8<-- [end:create_plugin]

fun buildRunner(): InMemoryRunner {
    // --8<-- [start:register_plugin]
    val rootAgent =
        LlmAgent(
            name = "hello_world",
            model = Gemini(name = "gemini-flash-latest"),
            instruction = Instruction("Greet the user."),
        )

    // Since adk-kotlin 0.7.0 the agent-based InMemoryRunner constructor accepts
    // plugins directly; before that they had to be set on an App.
    val runner =
        InMemoryRunner(
            agent = rootAgent,
            appName = "test_app_with_plugin",
            plugins = listOf(CountInvocationPlugin()),
        )
    // --8<-- [end:register_plugin]

    return runner
}
