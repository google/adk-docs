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

// --8<-- [start:full_code]

import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.tools.ToolContext
import com.google.adk.kt.types.Part

class DocAnalysisTools {
    /**
     * Analyzes a document held in the session's artifacts.
     *
     * Artifact access is suspending in Kotlin, so the tool is a `suspend fun`.
     * `searchMemory` is not available on the Kotlin ToolContext; to bring
     * long-term memory into a turn, add LoadMemoryTool or PreloadMemoryTool to
     * the agent instead.
     */
    @Tool
    suspend fun processDocument(
        @Param("The name of the document to analyze.") documentName: String,
        @Param("The query for the analysis.") analysisQuery: String,
        context: ToolContext,
    ): Map<String, String> {
        // 1. List all available artifacts.
        println("Tool: Available artifacts: ${context.listArtifacts()}")

        // 2. Load the requested artifact.
        println("Tool: Attempting to load artifact: $documentName")
        val documentPart = context.loadArtifact(documentName)
        if (documentPart == null) {
            println("Tool: Document '$documentName' not found.")
            return mapOf(
                "status" to "error",
                "message" to "Document '$documentName' not found.",
            )
        }

        val documentText = documentPart.text.orEmpty()
        println("Tool: Loaded '$documentName' (${documentText.length} chars).")

        // 3. Perform the analysis (placeholder).
        val analysisResult =
            "Analysis of '$documentName' regarding '$analysisQuery' " +
                "[Placeholder Analysis Result]"
        println("Tool: Performed analysis.")

        // 4. Save the analysis back as a new artifact. saveArtifact returns the
        // new version number and records the change in actions.artifactDelta.
        val newArtifactName = "analysis_$documentName"
        context.saveArtifact(newArtifactName, Part(text = analysisResult))

        return mapOf(
            "status" to "success",
            "analysis_artifact" to newArtifactName,
        )
    }
}
// --8<-- [end:full_code]
