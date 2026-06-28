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

// --8<-- [start:imports]
package main

import (
	"context"
	"fmt"
	"log"
	"strings"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/genai"
)

// --8<-- [end:imports]

const (
	modelName = "gemini-2.5-flash"
)

// --8<-- [start:callback_basic]
// onBeforeModel is a callback function that gets triggered before an LLM call.
func onBeforeModel(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
	log.Println("--- onBeforeModel Callback Triggered ---")
	log.Printf("Model Request to be sent: %v\n", req)
	// Returning nil allows the default LLM call to proceed.
	return nil, nil
}

func runBasicExample() {
	const (
		appName = "CallbackBasicApp"
		userID  = "test_user_123"
	)
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	// Register the callback function in the agent configuration.
	agentCfg := llmagent.Config{
		Name:                 "SimpleAgent",
		Model:                geminiModel,
		BeforeModelCallbacks: []llmagent.BeforeModelCallback{onBeforeModel},
	}
	simpleAgent, err := llmagent.New(agentCfg)
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          simpleAgent,
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatalf("Failed to create runner: %v", err)
	}
	// --8<-- [end:callback_basic]

	session, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  userID,
	})
	if err != nil {
		log.Fatalf("Failed to create session: %v", err)
	}

	input := genai.NewContentFromText("Why is the sky blue?", genai.RoleUser)
	log.Println("--- Running Agent ---")
	events := r.Run(ctx, userID, session.Session.ID(), input, agent.RunConfig{
		StreamingMode: agent.StreamingModeNone,
	})

	for event, err := range events {
		if err != nil {
			log.Fatalf("Error during agent execution: %v", err)
		}
		for _, p := range event.Content.Parts {
			fmt.Printf("Final Response: %s\n", p.Text)
		}
	}
	log.Println("--- Agent Run Finished ---")
}

// --8<-- [start:guardrail_init]
// onBeforeModelGuardrail is a callback that inspects the LLM request.
// If it contains a forbidden topic, it blocks the request and returns a
// predefined response. Otherwise, it allows the request to proceed.
func onBeforeModelGuardrail(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
	log.Println("--- onBeforeModelGuardrail Callback Triggered ---")

	// Inspect the request content for forbidden topics.
	for _, content := range req.Contents {
		for _, part := range content.Parts {
			if strings.Contains(part.Text, "finance") {
				log.Println("Forbidden topic 'finance' detected. Blocking LLM call.")
				// By returning a non-nil response, we override the default behavior
				// and prevent the actual LLM call.
				return &model.LLMResponse{
					Content: &genai.Content{
						Parts: []*genai.Part{{Text: "I'm sorry, but I cannot discuss financial topics."}},
						Role:  "model",
					},
				}, nil
			}
		}
	}

	log.Println("No forbidden topics found. Allowing LLM call to proceed.")
	// Returning nil allows the default LLM call to proceed.
	return nil, nil
}

func runGuardrailExample() {
	const (
		appName = "GuardrailApp"
		userID  = "test_user_456"
	)
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	agentCfg := llmagent.Config{
		Name:                 "ChatAgent",
		Model:                geminiModel,
		BeforeModelCallbacks: []llmagent.BeforeModelCallback{onBeforeModelGuardrail},
	}
	chatAgent, err := llmagent.New(agentCfg)
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          chatAgent,
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatalf("Failed to create runner: %v", err)
	}
	// --8<-- [end:guardrail_init]

	// --- Run with a safe prompt ---
	runAndPrint(ctx, r, sessionService, appName, "Tell me a fun fact about the Roman Empire.")

	// --- Run with a forbidden prompt ---
	runAndPrint(ctx, r, sessionService, appName, "What is the best way to manage my finance portfolio?")
}

func runAndPrint(ctx context.Context, r *runner.Runner, sessionService session.Service, appName, prompt string) {
	session, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  "test_user", // UserID can be generic here for the helper
	})
	if err != nil {
		log.Fatalf("Failed to create session: %v", err)
	}

	input := genai.NewContentFromText(prompt, genai.RoleUser)
	log.Printf("\n--- Running Agent with prompt: %q ---\n", prompt)
	events := r.Run(ctx, session.Session.UserID(), session.Session.ID(), input, agent.RunConfig{
		StreamingMode: agent.StreamingModeNone,
	})

	for event, err := range events {
		if err != nil {
			log.Fatalf("Error during agent execution: %v", err)
		}
		for _, p := range event.Content.Parts {
			fmt.Printf("Final Response: %s\n", p.Text)
		}
	}
	log.Println("--- Agent Run Finished ---")
}

func main() {
	fmt.Println("--- Running Basic Callback Example ---")
	runBasicExample()
	fmt.Println("\n\n--- Running Guardrail Callback Example ---")
	runGuardrailExample()
}
