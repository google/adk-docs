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

import com.google.adk.kt.agents.ReadonlyContext
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.tools.BaseTool
import com.google.adk.kt.tools.ToolFilter
import com.google.adk.kt.tools.Toolset
import com.google.adk.kt.tools.isToolSelected

// --8<-- [start:init]

/** The individual tools, exposed by the @Tool annotation. */
class MathTools {
    @Tool
    fun addNumbers(
        @Param("The first number.") a: Int,
        @Param("The second number.") b: Int,
    ): Int = a + b

    @Tool
    fun subtractNumbers(
        @Param("The first number.") a: Int,
        @Param("The second number.") b: Int,
    ): Int = a - b
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
}

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
// --8<-- [end:init]
