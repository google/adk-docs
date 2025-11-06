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
	"strings"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/artifact"
	"google.golang.org/adk/model"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/genai"
)

// This file contains snippets for the artifacts documentation.

// BeforeModelCallback saves any images from the user input before calling the model.
func BeforeModelCallback(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
	log.Println("[Callback] BeforeModelCallback triggered.")
	// Get the artifact manager from the context.
	artifacts := ctx.Artifacts()
	// Check if there are any contents in the request.
	if req.Contents != nil && len(req.Contents) > 0 {
		// Get the last content from the user.
		lastContent := req.Contents[len(req.Contents)-1]
		// Check if the last content is from the user.
		if lastContent.Role == genai.RoleUser {
			// Iterate over the parts of the content.
			for i, part := range lastContent.Parts {
				// Check if the part is an image.
				if part.InlineData != nil && strings.HasPrefix(part.InlineData.MIMEType, "image/") {
					// Create a unique filename for the image.
					fileName := fmt.Sprintf("user_image_%d.%s", i, strings.Split(part.InlineData.MIMEType, "/")[1])
					// Save the image as an artifact.
					if _, err := artifacts.Save(ctx, fileName, part); err != nil {
						log.Printf("[WARN] Failed to save user image: %v\n", err)
					} else {
						log.Printf("[INFO] Saved user image artifact: %s\n", fileName)
					}
				}
			}
		}
	}
	// Return nil to continue to the next callback or the model.
	return nil, nil // Continue to next callback or LLM call
}

// configureRunner configures the runner with an in-memory artifact service.
func configureRunner() {
	// --8<-- [start:configure-runner]
	// --8<-- [start:prerequisite]
	// Create a new context.
	ctx := context.Background()
	// Set the app name.
	const appName = "my_artifact_app"
	// Create a new Gemini model.
	model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	// Create a new LLM agent.
	myAgent, err := llmagent.New(llmagent.Config{
		Model:       model,
		Name:        "artifact_user_agent",
		Instruction: "You are an agent that describes images.",
		BeforeModelCallbacks: []llmagent.BeforeModelCallback{
			BeforeModelCallback,
		},
	})
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	// Create a new in-memory artifact service.
	artifactService := artifact.InMemoryService()
	// Create a new in-memory session service.
	sessionService := session.InMemoryService()

	// Create a new runner.
	r, err := runner.New(runner.Config{
		Agent:           myAgent,
		AppName:         appName,
		SessionService:  sessionService,
		ArtifactService: artifactService, // Provide the service instance here
	})
	if err != nil {
		log.Fatalf("Failed to create runner: %v", err)
	}
	log.Printf("Runner created successfully: %v", r)
	// --8<-- [end:prerequisite]
	// --8<-- [end:configure-runner]
}

// inMemoryServiceExample demonstrates how to set up an in-memory artifact service.
func inMemoryServiceExample() {
	// --8<-- [start:in-memory-service]
	// Simply instantiate the service
	artifactService := artifact.InMemoryService()
	log.Printf("InMemoryArtifactService (Go) instantiated: %T", artifactService)

	// Use the service in your runner
	// r, _ := runner.New(runner.Config{
	// 	Agent:           agent,
	// 	AppName:         "my_app",
	// 	SessionService:  sessionService,
	// 	ArtifactService: artifactService,
	// })

	// --8<-- [end:in-memory-service]
}

// --8<-- [start:loading-artifacts]
// loadArtifactsCallback is a BeforeModel callback that loads a specific artifact
// and adds its content to the LLM request.
func loadArtifactsCallback(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
	log.Println("[Callback] loadArtifactsCallback triggered.")
	// In a real app, you would parse the user's request to find a filename.
	// For this example, we'll hardcode a filename to demonstrate.
	const filenameToLoad = "generated_report.pdf"

	// Load the artifact from the artifact service.
	loadedPartResponse, err := ctx.Artifacts().Load(ctx, filenameToLoad)
	if err != nil {
		log.Printf("Callback could not load artifact '%s': %v", filenameToLoad, err)
		return nil, nil // File not found or error, continue to model.
	}

	loadedPart := loadedPartResponse.Part

	log.Printf("Callback successfully loaded artifact '%s'.", filenameToLoad)

	// Ensure there's at least one content in the request to append to.
	if len(req.Contents) == 0 {
		req.Contents = []*genai.Content{{Parts: []*genai.Part{
			genai.NewPartFromText("SYSTEM: The following file is provided for context:\n"),
		}}}
	}

	// Add the loaded artifact to the request for the model.
	lastContent := req.Contents[len(req.Contents)-1]
	lastContent.Parts = append(lastContent.Parts, loadedPart)
	log.Printf("Added artifact '%s' to LLM request.", filenameToLoad)

	// Return nil to continue to the next callback or the model.
	return nil, nil // Continue to next callback or LLM call
}

// --8<-- [end:loading-artifacts]

// representation demonstrates how to manually construct an artifact.
func representation() {
	// --8<-- [start:representation]
	// Create a byte slice with the image data.
	imageBytes, err := os.ReadFile("image.png")
	if err != nil {
		log.Fatalf("Failed to read image file: %v", err)
	}

	// Create a new artifact with the image data.
	imageArtifact := &genai.Part{
		InlineData: &genai.Blob{
			MIMEType: "image/png",
			Data:     imageBytes,
		},
	}
	log.Printf("Artifact MIME Type: %s", imageArtifact.InlineData.MIMEType)
	log.Printf("Artifact Data (first 8 bytes): %x...", imageArtifact.InlineData.Data[:8])
	// --8<-- [end:representation]
}

// artifactData demonstrates how to create an artifact from a file.
func artifactData() {
	// --8<-- [start:artifact-data]
	// Load imageBytes from a file
	imageBytes, err := os.ReadFile("image.png")
	if err != nil {
		log.Fatalf("Failed to read image file: %v", err)
	}

	// genai.NewPartFromBytes is a convenience function that is a shorthand for
	// creating a &genai.Part with the InlineData field populated.
	// Create a new artifact from the image data.
	imageArtifact := genai.NewPartFromBytes([]byte(imageBytes), "image/png")

	log.Printf("Artifact MIME Type: %s", imageArtifact.InlineData.MIMEType)
	// --8<-- [end:artifact-data]
}

// namespacing demonstrates the difference between session and user-scoped artifacts.
func namespacing() {
	// --8<-- [start:namespacing]
	// Note: Namespacing is only supported when using the GCS ArtifactService implementation.
	// A session-scoped artifact is only available within the current session.
	sessionReportFilename := "summary.txt"
	// A user-scoped artifact is available across all sessions for the current user.
	userConfigFilename := "user:settings.json"

	// When saving 'summary.txt' via ctx.Artifacts().Save,
	// it's tied to the current app_name, user_id, and session_id.
	// ctx.Artifacts().Save(sessionReportFilename, *artifact);

	// When saving 'user:settings.json' via ctx.Artifacts().Save,
	// the ArtifactService implementation should recognize the "user:" prefix
	// and scope it to app_name and user_id, making it accessible across sessions for that user.
	// ctx.Artifacts().Save(userConfigFilename, *artifact);
	// --8<-- [end:namespacing]

	log.Printf("Session filename: %s", sessionReportFilename)
	log.Printf("User filename: %s", userConfigFilename)
}

// --8<-- [start:saving-artifacts]
// saveReportCallback is a BeforeModel callback that saves a report from session state.
func saveReportCallback(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
	// Get the report data from the session state.
	reportData, err := ctx.State().Get("report_bytes")
	if err != nil {
		log.Printf("No report data found in session state: %v", err)
		return nil, nil // No report to save, continue normally.
	}

	// Check if the report data is in the expected format.
	reportBytes, ok := reportData.([]byte)
	if !ok {
		log.Printf("Report data in session state was not in the expected byte format.")
		return nil, nil
	}

	// Create a new artifact with the report data.
	reportArtifact := &genai.Part{
		InlineData: &genai.Blob{
			MIMEType: "application/pdf",
			Data:     reportBytes,
		},
	}
	// Set the filename for the artifact.
	filename := "generated_report.pdf"
	// Save the artifact to the artifact service.
	_, err = ctx.Artifacts().Save(ctx, filename, reportArtifact)
	if err != nil {
		log.Printf("An unexpected error occurred during Go artifact save: %v", err)
		// Depending on requirements, you might want to return an error to the user.
		return nil, nil
	}
	log.Printf("Successfully saved Go artifact '%s'.", filename)
	// Return nil to continue to the next callback or the model.
	return nil, nil
}

// --8<-- [end:saving-artifacts]

// --8<-- [start:listing-artifacts]
// listUserFilesCallback is a BeforeModel callback that lists available artifacts
// and adds the list as context to the LLM request.
func listUserFilesCallback(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
	log.Println("[Callback] listUserFilesCallback triggered.")
	// List the available artifacts from the artifact service.
	listResponse, err := ctx.Artifacts().List(ctx)
	if err != nil {
		log.Printf("An unexpected error occurred during Go artifact list: %v", err)
		return nil, nil // Continue, but log the error.
	}

	availableFiles := listResponse.FileNames

	log.Printf("Found %d available files.", len(availableFiles))

	// If there are available files, add them to the LLM request.
	if len(availableFiles) > 0 {
		var fileListStr strings.Builder
		fileListStr.WriteString("SYSTEM: The following files are available:\n")
		for _, fname := range availableFiles {
			fileListStr.WriteString(fmt.Sprintf("- %s\n", fname))
		}
		// Prepend this information to the user's request for the model.
		if len(req.Contents) > 0 {
			lastContent := req.Contents[len(req.Contents)-1]
			if len(lastContent.Parts) > 0 {
				fileListStr.WriteString("\n") // Add a newline for separation.
				lastContent.Parts[0] = genai.NewPartFromText(fileListStr.String() + lastContent.Parts[0].Text)
				log.Println("Added file list to LLM request context.")
			}
		}
		log.Printf("Available files:\n%s", fileListStr.String())
	} else {
		log.Println("No available files found to list.")
	}

	// Return nil to continue to the next callback or the model.
	return nil, nil // Continue to next callback or LLM call
}

// --8<-- [end:listing-artifacts]

func main() {
	log.Println("--- Running  Snippets ---")

	// Call each standalone snippet function.
	log.Println("\n--- representation ---")
	representation()

	log.Println("\n--- artifactData ---")
	artifactData()

	log.Println("\n--- namespacing ---")
	namespacing()

	log.Println("\n--- configureRunner (demonstrates BeforeModelCallback for saving) ---")
	configureRunner()

	log.Println("\n--- inMemoryServiceExample ---")
	inMemoryServiceExample()

	log.Println("\n--- Running Agent with Multiple Callbacks ---")
	// 1. Set up services
	ctx := context.Background()
	artifactService := artifact.InMemoryService()
	sessionService := session.InMemoryService()

	// 2. Set up the agent with multiple callbacks
	model, _ := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
	reportingAgent, _ := llmagent.New(llmagent.Config{
		Model:       model,
		Name:        "reporting_agent",
		Instruction: "You are a reporting agent. You can see available files and their contents if they are loaded for you. Summarize any provided files.",
		BeforeModelCallbacks: []llmagent.BeforeModelCallback{
			saveReportCallback,    // Saves report from state
			listUserFilesCallback, // Lists available files and adds to prompt
			loadArtifactsCallback, // Loads a specific file and adds to prompt
		},
	})

	// 3. Create a session with some initial state to trigger `saveReportCallback`
	reportBytes, _ := os.ReadFile("story.pdf") // Load a sample PDF file
	initialState := map[string]any{
		"report_bytes": reportBytes,
	}
	userID := "test-user"
	session, _ := sessionService.Create(ctx, &session.CreateRequest{
		AppName:   "my_app",
		UserID:    userID,
		SessionID: "test-session-callbacks",
		State:     initialState,
	})

	// 4. Create and run the runner
	r, _ := runner.New(runner.Config{
		Agent:           reportingAgent,
		AppName:         "my_app",
		SessionService:  sessionService,
		ArtifactService: artifactService,
	})

	log.Println("\n--- Agent Run 1: Triggering callbacks ---")
	log.Println("This run will trigger `saveReportCallback` (from session state), `listUserFilesCallback` (will see the newly saved file), and `loadArtifactsCallback` (will load it).")
	userInput := &genai.Content{Parts: []*genai.Part{genai.NewPartFromText("Please summarize the report for me.")}}
	for event, err := range r.Run(ctx, session.Session.UserID(), session.Session.ID(), userInput, agent.RunConfig{
		StreamingMode: agent.StreamingModeSSE,
	}) {
		if err != nil {
			log.Printf("AGENT ERROR: %v\n", err)
		} else if event != nil && event.Content != nil {
			for _, p := range event.Content.Parts {
				fmt.Print(string(p.Text))
			}
		}
	}
	fmt.Println()

	log.Println("\n--- Verifying artifacts after run ---")
	// We can list artifacts directly from the service to see what the agent did.
	listReq := &artifact.ListRequest{
		AppName:   "my_app",
		UserID:    userID,
		SessionID: "test-session-callbacks",
	}
	files, err := artifactService.List(ctx, listReq)
	if err != nil {
		log.Fatalf("Failed to list artifacts from service: %v", err)
	}
	log.Printf("Artifacts in service: %v", files)
}
