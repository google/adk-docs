// Copyright 2025 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"fmt"

	"google.golang.org/adk/tool"
	"google.golang.org/genai"
)

type processDocumentArgs struct {
	DocumentName  string `json:"document_name" jsonschema:"The name of the document to be processed."`
	AnalysisQuery string `json:"analysis_query" jsonschema:"The query for the analysis."`
}

type processDocumentResult struct {
	Status           string `json:"status"`
	AnalysisArtifact string `json:"analysis_artifact,omitempty"`
	Version          int64  `json:"version,omitempty"`
	Message          string `json:"message,omitempty"`
}

func processDocument(ctx tool.Context, args processDocumentArgs) processDocumentResult {
	fmt.Printf("Tool: Attempting to load artifact: %s\n", args.DocumentName)

	// List all artifacts
	listResponse, err := ctx.Artifacts().List(ctx)
	if err != nil {
		return processDocumentResult{Status: "error", Message: "Failed to list artifacts."}
	}

	fmt.Println("Tool: Available artifacts:")
	for _, file := range listResponse.FileNames {
		fmt.Printf(" - %s\n", file)
	}

	documentPart, err := ctx.Artifacts().Load(ctx, args.DocumentName)
	if err != nil {
		return processDocumentResult{Status: "error", Message: fmt.Sprintf("Document '%s' not found.", args.DocumentName)}
	}

	fmt.Printf("Tool: Loaded document '%s' of size %d bytes.\n", args.DocumentName, len(documentPart.Part.InlineData.Data))

	// 3. Search memory for related context
	fmt.Printf("Tool: Searching memory for context related to: '%s'\n", args.AnalysisQuery)
	memoryResp, err := ctx.SearchMemory(ctx, args.AnalysisQuery)
	if err != nil {
		fmt.Printf("Tool: Error searching memory: %v\n", err)
	}
	memoryResultCount := 0
	if memoryResp != nil {
		memoryResultCount = len(memoryResp.Memories)
	}
	fmt.Printf("Tool: Found %d memory results.\n", memoryResultCount)

	analysisResult := fmt.Sprintf("Analysis of '%s' regarding '%s' using memory context: [Placeholder Analysis Result]", args.DocumentName, args.AnalysisQuery)
	fmt.Println("Tool: Performed analysis.")

	analysisPart := genai.NewPartFromText(analysisResult)
	newArtifactName := fmt.Sprintf("analysis_%s", args.DocumentName)
	version, err := ctx.Artifacts().Save(ctx, newArtifactName, analysisPart)
	if err != nil {
		return processDocumentResult{Status: "error", Message: "Failed to save artifact."}
	}
	fmt.Printf("Tool: Saved analysis result as '%s' version %d.\n", newArtifactName, version.Version)

	return processDocumentResult{
		Status:           "success",
		AnalysisArtifact: newArtifactName,
		Version:          version.Version,
	}
}
