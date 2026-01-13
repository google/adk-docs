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
	"strings"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"
	"google.golang.org/genai"
)

type checkAndTransferArgs struct {
	Query string `json:"query" jsonschema:"The user's query to check for urgency."`
}

type checkAndTransferResult struct {
	Status string `json:"status"`
}

func checkAndTransfer(ctx tool.Context, args checkAndTransferArgs) (checkAndTransferResult, error) {
	if strings.Contains(strings.ToLower(args.Query), "urgent") {
		fmt.Println("Tool: Detected urgency, transferring to the support agent.")
		ctx.Actions().TransferToAgent = "support_agent"
		return checkAndTransferResult{Status: "Transferring to the support agent..."}, nil
	}
	return checkAndTransferResult{Status: fmt.Sprintf("Processed query: '%s'. No further action needed.", args.Query)}, nil
}

func main() {
	ctx := context.Background()
	model, err := gemini.NewModel(ctx, "gemini-2.0-flash", &genai.ClientConfig{})
	if err != nil {
		log.Fatal(err)
	}

	supportAgent, err := llmagent.New(llmagent.Config{
		Name:        "support_agent",
		Model:       model,
		Instruction: "You are the dedicated support agent. Mentioned you are a support handler and please help the user with their urgent issue.",
	})
	if err != nil {
		log.Fatal(err)
	}

	checkAndTransferTool, err := functiontool.New(
		functiontool.Config{
			Name:        "check_and_transfer",
			Description: "Checks if the query requires escalation and transfers to another agent if needed.",
		},
		checkAndTransfer,
	)
	if err != nil {
		log.Fatal(err)
	}

	mainAgent, err := llmagent.New(llmagent.Config{
		Name:        "main_agent",
		Model:       model,
		Instruction: "You are the first point of contact for customer support of an analytics tool. Answer general queries. If the user indicates urgency, use the 'check_and_transfer' tool.",
		Tools:       []tool.Tool{checkAndTransferTool},
		SubAgents:   []agent.Agent{supportAgent},
	})
	if err != nil {
		log.Fatal(err)
	}

	sessionService := session.InMemoryService()
	runner, err := runner.New(runner.Config{
		AppName:        "customer_support_agent",
		Agent:          mainAgent,
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatal(err)
	}

	session, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: "customer_support_agent",
		UserID:  "user1234",
	})
	if err != nil {
		log.Fatal(err)
	}

	run(ctx, runner, session.Session.ID(), "this is urgent, i cant login")
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
