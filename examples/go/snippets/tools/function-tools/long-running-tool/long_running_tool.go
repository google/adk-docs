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
	"sync/atomic"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"

	"google.golang.org/genai"
)

// --8<-- [start:create_long_running_tool]
// CreateTicketArgs defines the arguments for our long-running tool.
type CreateTicketArgs struct {
	Urgency string `json:"urgency" jsonschema:"The urgency level of the ticket."`
}

// CreateTicketResults defines the *initial* output of our long-running tool.
type CreateTicketResults struct {
	Status   string `json:"status"`
	TicketId string `json:"ticket_id"`
}

// createTicketAsync simulates the *initiation* of a long-running ticket creation task.
func createTicketAsync(ctx tool.Context, args CreateTicketArgs) CreateTicketResults {
	log.Printf("TOOL_EXEC: 'create_ticket_long_running' called with urgency: %s (Call ID: %s)\n", args.Urgency, ctx.FunctionCallID())

	// "Generate" a ticket ID and return it in the initial response.
	ticketID := "TICKET-ABC-123"
	log.Printf("ACTION: Generated Ticket ID: %s for Call ID: %s\n", ticketID, ctx.FunctionCallID())

	// In a real application, you would save the association between the
	// FunctionCallID and the ticketID to handle the async response later.
	return CreateTicketResults{
		Status:   "started",
		TicketId: ticketID,
	}
}

func createTicketAgent(ctx context.Context) (agent.Agent, error) {
	ticketTool, err := functiontool.New(
		functiontool.Config{
			Name:        "create_ticket_long_running",
			Description: "Creates a new support ticket with a specified urgency level.",
		},
		createTicketAsync,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create long running tool: %w", err)
	}

	model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("failed to create model: %v", err)
	}

	return llmagent.New(llmagent.Config{
		Name:        "ticket_agent",
		Model:       model,
		Instruction: "You are a helpful assistant for creating support tickets. Provide the status of the ticket at each interaction.",
		Tools:       []tool.Tool{ticketTool},
	})
}

// --8<-- [end:create_long_running_tool]

const (
	userID  = "example_user_id"
	appName = "example_app"
)

// --8<-- [start:run_long_running_tool]
// runTurn executes a single turn with the agent and returns the captured function call ID.
func runTurn(ctx context.Context, r *runner.Runner, sessionID, turnLabel string, content *genai.Content) string {
	var funcCallID atomic.Value // Safely store the found ID.

	fmt.Printf("\n--- %s ---\n", turnLabel)
	for event, err := range r.Run(ctx, userID, sessionID, content, agent.RunConfig{
		StreamingMode: agent.StreamingModeNone,
	}) {
		if err != nil {
			fmt.Printf("\nAGENT_ERROR: %v\n", err)
			continue
		}
		// Print a summary of the event for clarity.
		printEventSummary(event, turnLabel)

		// Capture the function call ID from the event.
		for _, part := range event.Content.Parts {
			if fc := part.FunctionCall; fc != nil {
				if fc.Name == "create_ticket_long_running" {
					funcCallID.Store(fc.ID)
				}
			}
		}
	}

	if id, ok := funcCallID.Load().(string); ok {
		return id
	}
	return ""
}

func main() {
	ctx := context.Background()
	ticketAgent, err := createTicketAgent(ctx)
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	// Setup the runner and session.
	sessionService := session.InMemoryService()
	session, err := sessionService.Create(ctx, &session.CreateRequest{AppName: appName, UserID: userID})
	if err != nil {
		log.Fatalf("Failed to create session: %v", err)
	}
	r, err := runner.New(runner.Config{AppName: appName, Agent: ticketAgent, SessionService: sessionService})
	if err != nil {
		log.Fatalf("Failed to create runner: %v", err)
	}

	// --- Turn 1: User requests to create a ticket. ---
	initialUserMessage := genai.NewContentFromText("Create a high urgency ticket for me.", genai.RoleUser)
	funcCallID := runTurn(ctx, r, session.Session.ID(), "Turn 1: User Request", initialUserMessage)
	if funcCallID == "" {
		log.Fatal("ERROR: Tool 'create_ticket_long_running' not called in Turn 1.")
	}
	fmt.Printf("ACTION: Captured FunctionCall ID: %s\n", funcCallID)

	// --- Turn 2: App provides the final status of the ticket. ---
	// In a real application, the ticketID would be retrieved from a database
	// using the funcCallID. For this example, we'll use the same ID.
	ticketID := "TICKET-ABC-123"
	willContinue := false // Signal that this is the final response.
	ticketStatusResponse := &genai.FunctionResponse{
		Name: "create_ticket_long_running",
		ID:   funcCallID,
		Response: map[string]any{
			"status":    "approved",
			"ticket_id": ticketID,
		},
		WillContinue: &willContinue,
	}
	appResponseWithStatus := &genai.Content{
		Role:  string(genai.RoleUser),
		Parts: []*genai.Part{{FunctionResponse: ticketStatusResponse}},
	}
	runTurn(ctx, r, session.Session.ID(), "Turn 2: App provides ticket status", appResponseWithStatus)
	fmt.Println("Long running function completed successfully.")
}

// printEventSummary provides a readable log of agent and LLM interactions.
func printEventSummary(event *session.Event, turnLabel string) {
	for _, part := range event.Content.Parts {
		// Check for a text part.
		if part.Text != "" {
			fmt.Printf("[%s][%s_TEXT]: %s\n", turnLabel, event.Author, part.Text)
		}
		// Check for a function call part.
		if fc := part.FunctionCall; fc != nil {
			fmt.Printf("[%s][%s_CALL]: %s(%v) ID: %s\n", turnLabel, event.Author, fc.Name, fc.Args, fc.ID)
		}
	}
}

// --8<-- [end:run_long_running_tool]
