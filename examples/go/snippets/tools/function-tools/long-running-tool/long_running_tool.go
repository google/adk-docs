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
	Urgency string `json:"urgency"`
}

// CreateTicketResults defines the *initial* output of our long-running tool.
// In this simulation, the tool immediately returns, but in a real scenario,
// it would start a background task.
type CreateTicketResults struct {
	Status string `json:"status"`
}

// createTicketAsync simulates the *initiation* of a long-running ticket creation task.
func createTicketAsync(ctx tool.Context, args CreateTicketArgs) CreateTicketResults {
	log.Printf("TOOL_EXEC: 'create_ticket_long_running' called with urgency: %s (Call ID: %s)\n", args.Urgency, ctx.FunctionCallID())
	// This is the initial response. The actual ticket ID will be provided later.
	return CreateTicketResults{Status: "started"}
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
		for _, part := range event.LLMResponse.Content.Parts {
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

	// --- Turn 2: App provides the ticket_id after async processing. ---
	ticketID := "TICKET-ABC-123"
	willContinue := true // Signal that more updates will follow.
	ticketCreatedResponse := &genai.FunctionResponse{
		Name: "create_ticket_long_running",
		ID:   funcCallID,
		Response: map[string]any{
			"status":    "pending",
			"ticket_id": ticketID,
		},
		WillContinue: &willContinue,
	}
	appResponseWithTicketID := &genai.Content{
		Role:  string(genai.RoleUser),
		Parts: []*genai.Part{{FunctionResponse: ticketCreatedResponse}},
	}
	runTurn(ctx, r, session.Session.ID(), "Turn 2: App provides ticket_id", appResponseWithTicketID)
	fmt.Printf("ACTION: Sent ticket_id %s to agent.\n", ticketID)

	// --- Turn 3: App provides the final status of the ticket. ---
	willContinue = false // Signal that this is the final response.
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
	runTurn(ctx, r, session.Session.ID(), "Turn 3: App provides ticket status", appResponseWithStatus)
	fmt.Println("Long running function completed successfully.")
}

// printEventSummary provides a readable log of agent and LLM interactions.
func printEventSummary(event *session.Event, turnLabel string) {
	if event.LLMResponse != nil && event.LLMResponse.Content != nil {
		for _, part := range event.LLMResponse.Content.Parts {
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
}

// --8<-- [end:run_long_running_tool]
