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
	"google.golang.org/adk/util/instructionutil"
	"google.golang.org/genai"
)

const (
	appName   = "instruction_provider_app"
	userID    = "user5678"
	sessionID = "91011"
	modelID   = "gemini-2.0-flash"
)

// --8<-- [start:bypass_state_injection]

//  1. This InstructionProvider returns a static string.
//     Because it's a provider function, the ADK will not attempt to inject
//     state, and the instruction will be passed to the model as-is,
//     preserving the literal braces.
func staticInstructionProvider(ctx agent.ReadonlyContext) (string, error) {
	return "This is an instruction with {{literal_braces}} that will not be replaced.", nil
}

// --8<-- [end:bypass_state_injection]

// --8<-- [start:manual_state_injection]

//  2. This InstructionProvider demonstrates how to manually inject state
//     while also preserving literal braces. It uses the instructionutil helper.
func dynamicInstructionProvider(ctx agent.ReadonlyContext) (string, error) {
	template := "This is a {adjective} instruction with {{literal_braces}}."
	// This will inject the 'adjective' state variable but leave the literal braces.
	return instructionutil.InjectSessionState(ctx, template)
}

// --8<-- [end:manual_state_injection]

func main() {
	ctx := context.Background()
	sessionService := session.InMemoryService()

	// Initialize a session with state for the dynamic provider.
	_, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName:   appName,
		UserID:    userID,
		SessionID: sessionID,
		State: map[string]any{
			"adjective": "dynamic",
		},
	})
	if err != nil {
		log.Fatalf("Failed to create session: %v", err)
	}

	// ---
	// Example with Static Provider
	// ---
	fmt.Println("--- Running Agent with Static InstructionProvider ---")
	modelStatic, err := gemini.NewModel(ctx, modelID, nil)
	if err != nil {
		log.Fatalf("Failed to create Gemini model for static agent: %v", err)
	}
	staticAgent, err := llmagent.New(llmagent.Config{
		Name:                "StaticTemplateAgent",
		Model:               modelStatic,
		InstructionProvider: staticInstructionProvider,
	})
	if err != nil {
		log.Fatalf("Failed to create static agent: %v", err)
	}
	runAgent(ctx, sessionService, staticAgent, "Explain your instructions.")

	// ---
	// Example with Dynamic Provider
	// ---
	fmt.Println("\n--- Running Agent with Dynamic InstructionProvider ---")
	modelDynamic, err := gemini.NewModel(ctx, modelID, nil)
	if err != nil {
		log.Fatalf("Failed to create Gemini model for dynamic agent: %v", err)
	}
	dynamicAgent, err := llmagent.New(llmagent.Config{
		Name:                "DynamicTemplateAgent",
		Model:               modelDynamic,
		InstructionProvider: dynamicInstructionProvider,
	})
	if err != nil {
		log.Fatalf("Failed to create dynamic agent: %v", err)
	}
	runAgent(ctx, sessionService, dynamicAgent, "Explain your instructions.")
}

// Helper function to run an agent and print its response.
func runAgent(ctx context.Context, ss session.Service, a agent.Agent, prompt string) {
	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          a,
		SessionService: ss,
	})
	if err != nil {
		log.Fatalf("Failed to create runner: %v", err)
	}

	userMessage := genai.NewContentFromText(prompt, "user")
	for event, err := range r.Run(ctx, userID, sessionID, userMessage, agent.RunConfig{}) {
		if err != nil {
			log.Printf("Agent Error: %v", err)
			continue
		}
		if event.LLMResponse.Content != nil && len(event.LLMResponse.Content.Parts) > 0 {
			for _, p := range event.LLMResponse.Content.Parts {
				if p.Text != "" {
					fmt.Print(p.Text)
				}
			}
		}
	}
	fmt.Println()
}
