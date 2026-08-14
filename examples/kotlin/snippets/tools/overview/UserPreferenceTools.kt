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

import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.tools.ToolContext

// --8<-- [start:example]
class UserPreferenceTools {
    /**
     * Updates a user-specific preference.
     */
    @Tool
    fun updateUserPreference(
        @Param("The name of the preference to update.") preference: String,
        @Param("The value to set the preference to.") value: String,
        context: ToolContext,
    ): Map<String, String> {
        // One key per preference, so each write stands on its own. The "user:"
        // prefix scopes the value to this user across all their sessions.
        val userPrefsKey = "user:preferences:$preference"

        // Read through the readonly view of the context.
        val previous = context.context.state[userPrefsKey] as? String

        // Kotlin has no mutable `state` on ToolContext. Writing through
        // actions.stateDelta is what puts the change on the resulting event, which
        // is the same effect as assigning to `tool_context.state` in Python.
        context.actions.stateDelta[userPrefsKey] = value

        println("Tool: Updated user preference '$preference' from '$previous' to '$value'")
        return mapOf("status" to "success", "updated_preference" to preference)
    }
}

// In an agent:
//   LlmAgent(..., tools = UserPreferenceTools().generatedTools())
//
// When the LLM calls updateUserPreference(preference = "theme", value = "dark"),
// the delta is written to the session state and travels on the resulting tool
// response event as actions.stateDelta.
// --8<-- [end:example]
