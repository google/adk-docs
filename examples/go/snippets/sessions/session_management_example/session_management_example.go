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

	"google.golang.org/adk/session"
)

// This example demonstrates session management in the Go ADK, covering:
// 1. Initializing different SessionService implementations.
// 2. Creating a session and examining its properties.

func main() {
	ctx := context.Background()

	// --- SessionService Implementations ---

	// --8<-- [start:in_memory_service]
	// 1. InMemorySessionService
	// Stores all session data directly in the application's memory.
	// All conversation data is lost if the application restarts.
	inMemoryService := session.InMemoryService()
	fmt.Println("Initialized InMemorySessionService.")
	// --8<-- [end:in_memory_service]

	// --8<-- [start:vertexai_service]
	// 2. VertexAiSessionService
	// Uses Google Cloud Vertex AI for persistent, scalable session management.
	// Requires a Google Cloud project and an Agent Engine ID.
	// Before running, ensure your environment is authenticated and variables are set:
	// export GOOGLE_API_KEY="your-express-mode-api-key"
	// export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
	// export GOOGLE_CLOUD_LOCATION="your-gcp-location"
	agentEngineID := "your-reasoning-engine-id" // Replace with your actual Agent Engine ID
	vertexService, err := session.VertexAIService(ctx, agentEngineID)
	if err != nil {
		log.Printf("Could not initialize VertexAiSessionService (this is expected if GOOGLE_API_KEY is not set): %v", err)
	} else {
		fmt.Println("Successfully initialized VertexAiSessionService.")
	}
	// --8<-- [end:vertexai_service]
	_ = vertexService // Avoid unused variable error if initialization fails.

	// --- Examining Session Properties ---
	// We'll use the InMemorySessionService for this demonstration.
	// --8<-- [start:examine_session]
	appName := "my_go_app"
	userID := "example_go_user"
	initialState := map[string]any{"initial_key": "initial_value"}

	// Create a session to examine its properties.
	createResp, err := inMemoryService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  userID,
		State:   initialState,
	})
	if err != nil {
		log.Fatalf("Failed to create session: %v", err)
	}
	exampleSession := createResp.Session

	fmt.Println("\n--- Examining Session Properties ---")
	fmt.Printf("ID (`ID()`):                %s\n", exampleSession.ID())
	fmt.Printf("Application Name (`AppName()`): %s\n", exampleSession.AppName())
	fmt.Printf("User ID (`UserID()`):         %s\n", exampleSession.UserID())

	// To access state, you get a state object and then call Get().
	stateObj := exampleSession.State()
	val, _ := stateObj.Get("initial_key")
	fmt.Printf("State (`State().Get()`):    initial_key = %v\n", val)

	// Events are initially empty.
	fmt.Printf("Events (`Events().Len()`):  %d\n", exampleSession.Events().Len())
	fmt.Printf("Last Update (`LastUpdateTime()`): %s\n", exampleSession.LastUpdateTime().Format("2006-01-02 15:04:05"))
	fmt.Println("---------------------------------")

	// Clean up the session.
	err = inMemoryService.Delete(ctx, &session.DeleteRequest{
		AppName:   exampleSession.AppName(),
		UserID:    exampleSession.UserID(),
		SessionID: exampleSession.ID(),
	})
	if err != nil {
		log.Fatalf("Failed to delete session: %v", err)
	}
	fmt.Println("Session deleted successfully.")
	// --8<-- [end:examine_session]
}
