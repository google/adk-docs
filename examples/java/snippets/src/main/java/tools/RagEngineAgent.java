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

package tools;

// --8<-- [start:full_code]
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.retrieval.VertexAiRagRetrieval;
import com.google.cloud.aiplatform.v1.RetrieveContextsRequest.VertexRagStore.RagResource;
import com.google.cloud.aiplatform.v1.VertexRagServiceClient;
import java.io.IOException;
import java.util.List;
import java.util.Objects;

public class RagEngineAgent {

  public static void main(String[] args) throws IOException {
    // Please fill in your own RAG corpus and Vertex AI parent location, e.g.
    // RAG_CORPUS: projects/123/locations/us-central1/ragCorpora/456
    String ragCorpus =
        Objects.requireNonNullElse(
            System.getenv("RAG_CORPUS"),
            "projects/PROJECT_ID/locations/LOCATION/ragCorpora/CORPUS_ID");
    String parent =
        Objects.requireNonNullElse(
            System.getenv("VERTEX_AI_PARENT"), "projects/PROJECT_ID/locations/LOCATION");

    try (VertexRagServiceClient vertexRagServiceClient = VertexRagServiceClient.create()) {
      VertexAiRagRetrieval askVertexRetrieval =
          VertexAiRagRetrieval.builder()
              .name("retrieve_rag_documentation")
              .description(
                  "Use this tool to retrieve documentation and reference materials for the"
                      + " question from the RAG corpus.")
              .vertexRagServiceClient(vertexRagServiceClient)
              .parent(parent)
              .ragResources(List.of(RagResource.newBuilder().setRagCorpus(ragCorpus).build()))
              .similarityTopK(10)
              .vectorDistanceThreshold(0.6)
              .build();

      LlmAgent rootAgent =
          LlmAgent.builder()
              .model("gemini-flash-latest")
              .name("ask_rag_agent")
              .instruction(
                  "You are an expert RAG documentation assistant. Use the"
                      + " retrieve_rag_documentation tool to fetch relevant documentation and"
                      + " reference materials, then answer the user's question based on them.")
              .tools(List.of(askVertexRetrieval))
              .build();
    }
  }
}
// --8<-- [end:full_code]
