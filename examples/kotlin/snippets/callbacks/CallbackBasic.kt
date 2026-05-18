package com.google.adk.kt.examples.callbacks

import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.callbacks.AfterAgentCallback
import com.google.adk.kt.callbacks.AfterModelCallback
import com.google.adk.kt.callbacks.AfterToolCallback
import com.google.adk.kt.callbacks.BeforeAgentCallback
import com.google.adk.kt.callbacks.BeforeModelCallback
import com.google.adk.kt.callbacks.BeforeToolCallback
import com.google.adk.kt.callbacks.CallbackChoice
import com.google.adk.kt.models.Gemini

fun main() {
    // --8<-- [start:callback_basic]
    val agent = LlmAgent(
        name = "callback_agent",
        model = Gemini(
            name = "gemini-flash-latest",
            apiKey = System.getenv("GOOGLE_API_KEY")
                ?: error("GOOGLE_API_KEY environment variable not set."),
        ),
        beforeAgentCallbacks = listOf(
            BeforeAgentCallback { context ->
                println("Before Agent Callback triggered")
                CallbackChoice.Continue(context.eventActions)
            }
        ),
        afterAgentCallbacks = listOf(
            AfterAgentCallback { context ->
                println("After Agent Callback triggered")
                CallbackChoice.Continue(Unit)
            }
        ),
        beforeModelCallbacks = listOf(
            BeforeModelCallback { context, request ->
                println("Before Model Callback triggered")
                CallbackChoice.Continue(request)
            }
        ),
        afterModelCallbacks = listOf(
            AfterModelCallback { context, response ->
                println("After Model Callback triggered")
                response
            }
        ),
        beforeToolCallbacks = listOf(
            BeforeToolCallback { context, tool, args ->
                println("Before Tool Callback triggered for ${tool.name}")
                CallbackChoice.Continue(args)
            }
        ),
        afterToolCallbacks = listOf(
            AfterToolCallback { context, tool, args, result ->
                println("After Tool Callback triggered for ${tool.name}")
                result
            }
        )
    )
    // --8<-- [end:callback_basic]
}
