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

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/genai"
)

const (
	appName   = "instruction_template_app"
	userID    = "user1234"
	sessionID = "5678"
	modelID   = "gemini-2.0-flash"
)

// --8<-- [start:key_template]
func main() {
	ctx := context.Background()
	sessionService := session.InMemoryService()

	// 1. Initialize a session with a 'topic' in its state.
	_, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName:   appName,
		UserID:    userID,
		SessionID: sessionID,
		State: map[string]any{
			"topic": "friendship",
		},
	})
	if err != nil {
		log.Fatalf("Failed to create session: %v", err)
	}

	// 2. Create an agent with an instruction that uses a {topic} placeholder.
	//    The ADK will automatically inject the value of "topic" from the
	//    session state into the instruction before calling the LLM.
	model, err := gemini.NewModel(ctx, modelID, nil)
	if err != nil {
		log.Fatalf("Failed to create Gemini model: %v", err)
	}
	storyGenerator, err := llmagent.New(llmagent.Config{
		Name:        "StoryGenerator",
		Model:       model,
		Instruction: "Write a short story about a cat, focusing on the theme: {topic}.",
	})
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          agent.Agent(storyGenerator),
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatalf("Failed to create runner: %v", err)
	}

	// --8<-- [end:key_template]

	// 3. Run the agent. The LLM will receive the dynamically generated instruction.
	fmt.Println("--- Running StoryGenerator (Instruction Templating) Example ---")
	userMessage := genai.NewContentFromText("Tell me a story.", "user")
	for event, err := range r.Run(ctx, userID, sessionID, userMessage, agent.RunConfig{}) {
		if err != nil {
			log.Printf("Agent Error: %v", err)
			continue
		}
		if event.Content != nil && len(event.Content.Parts) > 0 {
			for _, p := range event.Content.Parts {
				if p.Text != "" {
					fmt.Print(p.Text)
				}
			}
		}
	}
	fmt.Println("\n--- Example Complete ---")
}
