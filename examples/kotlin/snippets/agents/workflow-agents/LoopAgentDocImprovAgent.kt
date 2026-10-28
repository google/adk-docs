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

package com.google.adk.kt.examples.agents.workflowagents

// --8<-- [start:init]
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.agents.LlmAgent.IncludeContents
import com.google.adk.kt.agents.LoopAgent
import com.google.adk.kt.agents.SequentialAgent
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.callbacks.BeforeAgentCallback
import com.google.adk.kt.callbacks.CallbackChoice
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.tools.ToolContext

// --- Constants ---
const val GEMINI_MODEL = "gemini-2.5-flash"

// --- State Keys ---
const val STATE_CURRENT_DOC = "current_document"
const val STATE_CRITICISM = "criticism"

// Define the exact phrase the Critic should use to signal completion
const val COMPLETION_PHRASE = "No major issues found."

// --- Tool Definition ---
class LoopTools {
    /**
     * Call this function ONLY when the critique indicates no further changes are needed, signaling
     * the iterative process should end.
     */
    @Tool(name = "exit_loop")
    fun exitLoop(context: ToolContext): Map<String, String> {
        println("  [Tool Call] exit_loop triggered by ${context.agentName}")
        context.actions.escalate = true
        context.actions.skipSummarization = true
        // Return empty map as tools should typically return JSON-serializable output
        return emptyMap()
    }
}

// --- Before Agent Callback ---
// Ensure 'initial_topic' is set in state before pipeline starts.
val updateInitialTopicState =
    BeforeAgentCallback { context ->
        context.updateState(
            "initial_topic",
            context.state["initial_topic"] ?: "a robot developing unexpected emotions",
        )
        CallbackChoice.Continue(context.eventActions)
    }

// --- Agent Definitions ---
val model = Gemini(name = GEMINI_MODEL)

// STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
val initialWriterAgent =
    LlmAgent(
        name = "InitialWriterAgent",
        model = model,
        includeContents = IncludeContents.NONE,
        instruction =
            Instruction(
                """
                You are a Creative Writing Assistant tasked with starting a story.
                Write a *very basic* first draft of a short story (just 1-2 simple sentences).
                Keep it plain and minimal - do NOT add descriptive language yet.
                Topic: {initial_topic}

                Output *only* the story/document text. Do not add introductions or explanations.
                """.trimIndent(),
            ),
        description =
            "Writes the initial document draft based on the topic, aiming for some initial " +
                "substance.",
        outputKey = STATE_CURRENT_DOC,
    )

// STEP 2a: Critic Agent (Inside the Refinement Loop)
val criticAgentInLoop =
    LlmAgent(
        name = "CriticAgent",
        model = model,
        includeContents = IncludeContents.NONE,
        instruction =
            Instruction(
                """
                You are a Constructive Critic AI reviewing a short story draft.

                **Document to Review:**
                ```
                {current_document}
                ```

                **Completion Criteria (ALL must be met):**
                1. At least 4 sentences long
                2. Has a clear beginning, middle, and end
                3. Includes at least one descriptive detail (sensory or emotional)

                **Task:**
                Check the document against the criteria above.

                IF any criteria is NOT met, provide specific feedback on what to add or improve.
                Output *only* the critique text.

                IF ALL criteria are met, respond *exactly* with: "$COMPLETION_PHRASE"
                """.trimIndent(),
            ),
        description =
            "Reviews the current draft, providing critique if clear improvements are needed, " +
                "otherwise signals completion.",
        outputKey = STATE_CRITICISM,
    )

// STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
val refinerAgentInLoop =
    LlmAgent(
        name = "RefinerAgent",
        model = model,
        // Relies solely on state via placeholders
        includeContents = IncludeContents.NONE,
        instruction =
            Instruction(
                """
                You are a Creative Writing Assistant refining a document based on feedback OR exiting the process.
                **Current Document:**
                ```
                {current_document}
                ```
                **Critique/Suggestions:**
                {criticism}

                **Task:**
                Analyze the 'Critique/Suggestions'.
                IF the critique is *exactly* "$COMPLETION_PHRASE":
                You MUST call the 'exit_loop' function. Do not output any text.
                ELSE (the critique contains actionable feedback):
                Carefully apply the suggestions to improve the 'Current Document'. Output *only* the refined document text.

                Do not add explanations. Either output the refined document OR call the exit_loop function.
                """.trimIndent(),
            ),
        description =
            "Refines the document based on critique, or calls exit_loop if critique indicates " +
                "completion.",
        // Provide the exit_loop tool
        tools = LoopTools().generatedTools(),
        // Overwrites state['current_document'] with the refined version
        outputKey = STATE_CURRENT_DOC,
    )

// STEP 2: Refinement Loop Agent
val refinementLoop =
    LoopAgent(
        name = "RefinementLoop",
        // Agent order is crucial: Critique first, then Refine/Exit
        subAgents =
            listOf(
                criticAgentInLoop,
                refinerAgentInLoop,
            ),
        // Limit loops
        maxIterations = 5,
    )

// STEP 3: Overall Sequential Pipeline
val rootAgent =
    SequentialAgent(
        name = "IterativeWritingPipeline",
        subAgents =
            listOf(
                // Run first to create initial doc
                initialWriterAgent,
                // Then run the critique/refine loop
                refinementLoop,
            ),
        // set initial topic in state
        beforeAgentCallbacks = listOf(updateInitialTopicState),
        description =
            "Writes an initial document and then iteratively refines it with critique using an " +
                "exit tool.",
    )
// --8<-- [end:init]
