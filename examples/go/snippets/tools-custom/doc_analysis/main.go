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
	"context"
	"fmt"
	"log"
	"os"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/artifact"
	"google.golang.org/adk/memory"
	"google.golang.org/adk/model"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"
	"google.golang.org/genai"
)

func saveStoryBytes(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
	// Get the report data from the session state.
	storyData, err := ctx.State().Get("story_bytes")
	if err != nil {
		log.Printf("No report data found in session state: %v", err)
		return nil, nil // No report to save, continue normally.
	}

	// Check if the report data is in the expected format.
	storyBytes, ok := storyData.([]byte)
	if !ok {
		log.Printf("Report data in session state was not in the expected byte format.")
		return nil, nil
	}

	// Create a new artifact with the report data.
	documentArtifact := &genai.Part{
		InlineData: &genai.Blob{
			MIMEType: "application/pdf",
			Data:     storyBytes,
		},
	}
	// Set the filename for the artifact.
	filename := "my_document.pdf"
	// Save the artifact to the artifact service.
	_, err = ctx.Artifacts().Save(ctx, filename, documentArtifact)
	if err != nil {
		log.Printf("An unexpected error occurred during Go artifact save: %v", err)
		// Depending on requirements, you might want to return an error to the user.
		return nil, nil
	}
	log.Printf("Successfully saved Go artifact '%s'.", filename)

	// Return nil to continue to the next callback or the model.
	return nil, nil
}

func main() {
	ctx := context.Background()
	model, err := gemini.NewModel(ctx, "gemini-2.0-flash", &genai.ClientConfig{})
	if err != nil {
		log.Fatal(err)
	}

	docAnalysisTool, err := functiontool.New(
		functiontool.Config{
			Name:        "process_document",
			Description: "Analyzes a document using context from memory.",
		},
		processDocument,
	)
	if err != nil {
		log.Fatal(err)
	}

	mainAgent, err := llmagent.New(llmagent.Config{
		Name:                 "main_agent",
		Model:                model,
		Instruction:          "You are an agent that can process documents.",
		Tools:                []tool.Tool{docAnalysisTool},
		BeforeModelCallbacks: []llmagent.BeforeModelCallback{saveStoryBytes},
	})
	if err != nil {
		log.Fatal(err)
	}

	sessionService := session.InMemoryService()
	artifactService := artifact.InMemoryService()
	memoryService := memory.InMemoryService()
	runner, err := runner.New(runner.Config{
		AppName:         "doc_analysis",
		Agent:           mainAgent,
		SessionService:  sessionService,
		ArtifactService: artifactService,
		MemoryService:   memoryService,
	})
	if err != nil {
		log.Fatal(err)
	}

	session1, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: "doc_analysis",
		UserID:  "user1234",
	})
	if err != nil {
		log.Fatal(err)
	}

	storyBytes, _ := os.ReadFile("story.pdf") // Load a sample PDF file
	initialState := map[string]any{
		"story_bytes": storyBytes,
	}

	session2, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: "doc_analysis",
		UserID:  "user1234",
		State:   initialState,
	})
	if err != nil {
		log.Fatal(err)
	}

	// First run to populate memory. The agent will respond, and the runner will
	// automatically add the interaction to the memory service.
	run(ctx, runner, session1.Session.ID(), "I am very interested in positive sentiment analysis.")
	// Second run that uses the tool to search the memory populated by the first run.
	run(ctx, runner, session2.Session.ID(), "process the document named 'my_document.pdf' and analyze it for 'sentiment'")
}

func run(ctx context.Context, r *runner.Runner, sessionID string, prompt string) {
	fmt.Printf("\n> %s\n", prompt)
	events := r.Run(
		ctx,
		"user1234",
		sessionID,
		genai.NewContentFromText(prompt, genai.RoleUser),
		agent.RunConfig{
			StreamingMode: agent.StreamingModeNone,
		},
	)
	for event, err := range events {
		if err != nil {
			log.Fatalf("ERROR during agent execution: %v", err)
		}

		if event.Content.Parts[0].Text != "" {
			fmt.Printf("Agent Response: %s\n", event.Content.Parts[0].Text)
		}
	}
}
