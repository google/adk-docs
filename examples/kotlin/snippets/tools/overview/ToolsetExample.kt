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

package com.google.adk.kt.examples.tools.overview

// --8<-- [start:init]

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.agents.ReadonlyContext
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.tools.BaseTool
import com.google.adk.kt.tools.ToolContext
import com.google.adk.kt.tools.ToolFilter
import com.google.adk.kt.tools.Toolset
import com.google.adk.kt.tools.isToolSelected

/** The individual tools, exposed by the @Tool annotation. */
class MathTools {
    /**
     * Adds two integer numbers.
     */
    @Tool
    fun addNumbers(
        @Param("The first number.") a: Int,
        @Param("The second number.") b: Int,
        context: ToolContext,
    ): Map<String, Any> {
        // Example: recording something in the session state.
        context.actions.stateDelta["last_math_operation"] = "addition"
        return mapOf("status" to "success", "result" to a + b)
    }

    /**
     * Subtracts the second number from the first.
     */
    @Tool
    fun subtractNumbers(
        @Param("The first number.") a: Int,
        @Param("The second number.") b: Int,
    ): Map<String, Any> = mapOf("status" to "success", "result" to a - b)
}

/** An individual tool, defined outside any toolset. */
class GreetTools {
    /**
     * Greets the user.
     */
    @Tool
    fun greetUser(
        @Param("The name of the user to greet.") name: String,
    ): Map<String, String> {
        println("Tool: greetUser called with name=$name")
        return mapOf("greeting" to "Hello, $name!")
    }
}

/**
 * A toolset that narrows what it exposes with an optional [ToolFilter].
 *
 * A null filter selects every tool, so the filter is genuinely optional.
 */
class SimpleMathToolset(private val filter: ToolFilter? = null) : Toolset {
    private val tools = MathTools().generatedTools()

    override suspend fun getTools(readonlyContext: ReadonlyContext?): List<BaseTool> =
        tools.filter { filter.isToolSelected(it, readonlyContext) }

    /** Releases anything the toolset holds. There is nothing to release here. */
    override fun close() {}
}

/**
 * An agent using both an individual tool and a toolset. Kotlin keeps the two
 * apart: individual tools go in `tools`, toolsets in `toolsets`.
 */
val calculatorAgent =
    LlmAgent(
        name = "calculator_agent",
        model = Gemini(name = "gemini-flash-latest"),
        instruction =
            Instruction(
                "You are a helpful calculator and greeter. Use greetUser for " +
                    "greetings. Use addNumbers to add and subtractNumbers to " +
                    "subtract. Announce the state of 'last_math_operation' if it is set.",
            ),
        tools = GreetTools().generatedTools(),
        toolsets = listOf(SimpleMathToolset()),
    )
// --8<-- [end:init]

// --8<-- [start:filter]
// SimpleMathToolset, defined above, applies its optional ToolFilter inside
// getTools(). Passing one narrows what the same toolset exposes.

// Expose a fixed subset by name.
val addOnlyMath = SimpleMathToolset(ToolFilter.allowList("addNumbers"))

// Or decide per invocation. The predicate receives the ReadonlyContext, so the
// tool list can depend on session state, the user, or anything else on it.
val contextAwareMath =
    SimpleMathToolset(
        ToolFilter.Predicate { tool, context ->
            tool.name == "addNumbers" || context?.state?.get("enable_advanced_math") == true
        },
    )
// --8<-- [end:filter]
