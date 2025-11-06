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
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"
	"google.golang.org/genai"
)

func main() {
	ctx := context.Background()
	model, err := gemini.NewModel(ctx, "gemini-2.0-flash", &genai.ClientConfig{})
	if err != nil {
		log.Fatal(err)
	}

	userPreferenceTool, err := functiontool.New(
		functiontool.Config{
			Name:        "update_user_preference",
			Description: "Updates a user-specific preference.",
		},
		updateUserPreference,
	)
	if err != nil {
		log.Fatal(err)
	}

	mainAgent, err := llmagent.New(llmagent.Config{
		Name:        "main_agent",
		Model:       model,
		Instruction: "You are an agent that can update user preferences. When a user asks to set a preference, identify the preference key and the desired value. For example, in 'set my theme to dark', the key is 'theme' and the value is 'dark'. Then, call the 'update_user_preference' tool with these values.",
		Tools:       []tool.Tool{userPreferenceTool},
	})
	if err != nil {
		log.Fatal(err)
	}

	sessionService := session.InMemoryService()
	runner, err := runner.New(runner.Config{
		AppName:        "user_preference",
		Agent:          mainAgent,
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatal(err)
	}

	session, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: "user_preference",
		UserID:  "user1234",
	})
	if err != nil {
		log.Fatal(err)
	}

	run(ctx, runner, session.Session.ID(), "set my theme to dark")
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
