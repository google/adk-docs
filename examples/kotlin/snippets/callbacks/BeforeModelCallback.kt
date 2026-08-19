package com.google.adk.kt.examples.callbacks

import com.google.adk.kt.callbacks.BeforeModelCallback
import com.google.adk.kt.callbacks.CallbackChoice
import com.google.adk.kt.models.LlmResponse
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Role

// --8<-- [start:before_model_callback]
val guardrailCallback =
    BeforeModelCallback { context, request ->
        val userQuery = request.contents.lastOrNull()?.parts?.firstOrNull()?.text ?: ""

        if (userQuery.contains("sensitive info", ignoreCase = true)) {
            println("Guardrail triggered: Sensitive information requested.")
            CallbackChoice.Break(
                LlmResponse(
                    content =
                        Content(
                            role = Role.MODEL,
                            parts =
                                listOf(
                                    Part(
                                        text = "I'm sorry, I cannot provide sensitive information.",
                                    ),
                                ),
                        ),
                ),
            )
        } else {
            CallbackChoice.Continue(request)
        }
    }
// --8<-- [end:before_model_callback]
