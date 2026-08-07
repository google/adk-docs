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

package integrations

// --8<-- [start:full_code]
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.tools.VertexAiRagRetrieval
import com.google.adk.kt.types.VertexRagStoreRagResource

/**
 * An agent that answers from a Vertex AI RAG corpus.
 *
 * Retrieval happens inside the model through the Gemini-native `vertexRagStore`
 * kind, so the tool never runs locally.
 */
val ragAgent =
    LlmAgent(
        name = "rag_agent",
        model = Gemini(name = "gemini-flash-latest"),
        instruction =
            Instruction(
                "Answer questions using the documents in the RAG corpus. " +
                    "If the corpus does not cover the question, say so.",
            ),
        tools =
            listOf(
                VertexAiRagRetrieval(
                    name = "retrieve_docs",
                    description = "Retrieve reference material from the Vertex AI RAG corpus.",
                    // One corpus, or specific files from one corpus.
                    ragResources =
                        listOf(
                            VertexRagStoreRagResource(
                                ragCorpus =
                                    "projects/PROJECT_ID/locations/LOCATION/" +
                                        "ragCorpora/CORPUS_ID",
                            ),
                        ),
                    similarityTopK = 3,
                    vectorDistanceThreshold = 0.5,
                ),
            ),
    )
// --8<-- [end:full_code]
