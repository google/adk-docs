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

	orderStatusTool, err := functiontool.New(
		functiontool.Config{
			Name:        "lookup_order_status",
			Description: "Fetches the current status of a customer's order using its ID.",
		},
		lookupOrderStatus,
	)
	if err != nil {
		log.Fatal(err)
	}

	mainAgent, err := llmagent.New(llmagent.Config{
		Name:        "main_agent",
		Model:       model,
		Instruction: "You are an agent that can lookup order status.",
		Tools:       []tool.Tool{orderStatusTool},
	})
	if err != nil {
		log.Fatal(err)
	}

	sessionService := session.InMemoryService()
	runner, err := runner.New(runner.Config{
		AppName:        "order_status",
		Agent:          mainAgent,
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatal(err)
	}

	session, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: "order_status",
		UserID:  "user1234",
	})
	if err != nil {
		log.Fatal(err)
	}

	run(ctx, runner, session.Session.ID(), "what is the status of order 12345?")
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
