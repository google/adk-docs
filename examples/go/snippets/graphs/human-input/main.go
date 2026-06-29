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

// Package main demonstrates Human-in-the-Loop (HITL) patterns in ADK Go.
//
// In ADK Go, human input is obtained through the tool-confirmation mechanism
// rather than graph-based RequestInput nodes. A tool can pause execution and
// request user approval in two ways:
//
//  1. Simple: set RequireConfirmation: true in functiontool.Config. The
//     framework automatically emits an "adk_request_confirmation" FunctionCall
//     event that the client must respond to.
//
//  2. Manual: call ctx.RequestConfirmation(hint, payload) inside the tool
//     function itself for full control over the hint message and any structured
//     payload sent to the client.
//
// The client receives a FunctionCall event named "adk_request_confirmation" and
// must respond with a FunctionResponse whose "confirmed" field is true or false.
package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/genai"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/llmagent"
	"google.golang.org/adk/v2/model/gemini"
	"google.golang.org/adk/v2/runner"
	"google.golang.org/adk/v2/session"
	"google.golang.org/adk/v2/tool"
	"google.golang.org/adk/v2/tool/functiontool"
)

const (
	appName   = "hitl_demo"
	userID    = "demo_user"
	modelName = "gemini-flash-latest"
)

// --8<-- [start:simple-hitl]
// DoubleNumberArgs holds the input for the doubleNumber tool.
type DoubleNumberArgs struct {
	Number int `json:"number" jsonschema:"description=The number to double."`
}

// DoubleNumberResults holds the output of the doubleNumber tool.
type DoubleNumberResults struct {
	Result int `json:"result"`
}

// doubleNumber is a tool that doubles the given number.
// Because RequireConfirmation is true, the framework automatically pauses
// execution and emits an "adk_request_confirmation" event to the client before
// running the tool. The client must reply with a FunctionResponse confirming
// or denying the action.
func doubleNumber(ctx agent.Context, args DoubleNumberArgs) (DoubleNumberResults, error) {
	return DoubleNumberResults{Result: args.Number * 2}, nil
}

// newSimpleHITLAgent creates an LLM agent with a tool that always requires
// user confirmation before it executes.
func newSimpleHITLAgent(ctx context.Context) (agent.Agent, error) {
	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("failed to create model: %w", err)
	}

	doubleNumberTool, err := functiontool.New(
		functiontool.Config{
			Name:                "double_number",
			Description:         "Doubles the given number. Requires user approval before running.",
			RequireConfirmation: true, // Pause and ask for human approval on every call.
		},
		doubleNumber,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create tool: %w", err)
	}

	return llmagent.New(llmagent.Config{
		Name:        "double_number_agent",
		Model:       model,
		Instruction: "You are a helpful assistant. When asked to double a number, use the double_number tool.",
		Tools:       []tool.Tool{doubleNumberTool},
	})
}

// --8<-- [end:simple-hitl]

// --8<-- [start:hitl-with-hint]
// BookFlightArgs holds the input for the bookFlight tool.
type BookFlightArgs struct {
	Origin      string `json:"origin"      jsonschema:"description=Departure airport code."`
	Destination string `json:"destination" jsonschema:"description=Arrival airport code."`
	Date        string `json:"date"        jsonschema:"description=Travel date in YYYY-MM-DD format."`
}

// BookFlightResults holds the outcome of the bookFlight tool.
type BookFlightResults struct {
	Status        string `json:"status"`
	ConfirmNumber string `json:"confirm_number,omitempty"`
}

// bookFlight is a tool that pauses for human approval before completing a
// booking. It calls ctx.RequestConfirmation with a descriptive hint message
// so that the client can display exactly what action is pending.
func bookFlight(ctx agent.Context, args BookFlightArgs) (BookFlightResults, error) {
	// Check whether the user has already responded to an earlier confirmation
	// request for this exact tool call.
	if confirmation := ctx.ToolConfirmation(); confirmation != nil {
		if !confirmation.Confirmed {
			return BookFlightResults{Status: "Booking cancelled by user."}, nil
		}
		// Confirmation received and approved — complete the booking.
		return BookFlightResults{
			Status:        "Booking confirmed.",
			ConfirmNumber: "FLT-20251031",
		}, nil
	}

	// No confirmation yet: compose a human-readable hint and pause.
	hint := fmt.Sprintf(
		"The agent wants to book a flight from %s to %s on %s. Do you approve?",
		args.Origin, args.Destination, args.Date,
	)
	if err := ctx.RequestConfirmation(hint, nil); err != nil {
		return BookFlightResults{}, fmt.Errorf("failed to request confirmation: %w", err)
	}
	// Returning here suspends the tool; the framework re-invokes it after the
	// client sends back a FunctionResponse for "adk_request_confirmation".
	return BookFlightResults{Status: "Awaiting user approval."}, nil
}

// newHITLWithHintAgent creates an LLM agent whose bookFlight tool manually
// requests confirmation with a descriptive hint.
func newHITLWithHintAgent(ctx context.Context) (agent.Agent, error) {
	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("failed to create model: %w", err)
	}

	bookFlightTool, err := functiontool.New(
		functiontool.Config{
			Name:        "book_flight",
			Description: "Books a flight between two airports on a given date.",
		},
		bookFlight,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create tool: %w", err)
	}

	return llmagent.New(llmagent.Config{
		Name:        "flight_booking_agent",
		Model:       model,
		Instruction: "You are a flight booking assistant. Help the user book flights.",
		Tools:       []tool.Tool{bookFlightTool},
	})
}

// --8<-- [end:hitl-with-hint]

// --8<-- [start:hitl-with-payload]
// ItineraryItem represents a single activity in a travel plan.
type ItineraryItem struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

// ReviewItineraryArgs holds the input for the reviewItinerary tool.
type ReviewItineraryArgs struct {
	Itinerary []ItineraryItem `json:"itinerary" jsonschema:"description=List of activities to review."`
}

// ReviewItineraryResults holds the outcome after the user responds.
type ReviewItineraryResults struct {
	Status       string `json:"status"`
	UserFeedback string `json:"user_feedback,omitempty"`
}

// reviewItinerary pauses for user feedback and sends a structured payload (the
// full itinerary) alongside the hint so the client can render it for the user.
func reviewItinerary(ctx agent.Context, args ReviewItineraryArgs) (ReviewItineraryResults, error) {
	if confirmation := ctx.ToolConfirmation(); confirmation != nil {
		if !confirmation.Confirmed {
			return ReviewItineraryResults{Status: "Itinerary rejected by user."}, nil
		}
		// Extract free-text feedback from the structured payload, if provided.
		feedback := ""
		if m, ok := confirmation.Payload.(map[string]any); ok {
			if f, ok := m["user_feedback"].(string); ok {
				feedback = f
			}
		}
		return ReviewItineraryResults{
			Status:       "Itinerary approved.",
			UserFeedback: feedback,
		}, nil
	}

	hint := fmt.Sprintf(
		"Here is your recommended itinerary (%d activities). Which items appeal to you?",
		len(args.Itinerary),
	)
	// Pass the full itinerary as the payload so the client can display it.
	if err := ctx.RequestConfirmation(hint, args.Itinerary); err != nil {
		return ReviewItineraryResults{}, fmt.Errorf("failed to request confirmation: %w", err)
	}
	return ReviewItineraryResults{Status: "Awaiting user feedback."}, nil
}

// newHITLWithPayloadAgent creates an LLM agent whose reviewItinerary tool sends
// a structured payload to the client alongside the confirmation prompt.
func newHITLWithPayloadAgent(ctx context.Context) (agent.Agent, error) {
	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("failed to create model: %w", err)
	}

	reviewTool, err := functiontool.New(
		functiontool.Config{
			Name:        "review_itinerary",
			Description: "Presents the proposed itinerary to the user for feedback.",
		},
		reviewItinerary,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create tool: %w", err)
	}

	return llmagent.New(llmagent.Config{
		Name:        "concierge_agent",
		Model:       model,
		Instruction: "You are a travel concierge. Build an itinerary and present it to the user for review.",
		Tools:       []tool.Tool{reviewTool},
	})
}

// --8<-- [end:hitl-with-payload]

func main() {
	ctx := context.Background()

	simpleAgent, err := newSimpleHITLAgent(ctx)
	if err != nil {
		log.Fatalf("Failed to create simple HITL agent: %v", err)
	}

	hintAgent, err := newHITLWithHintAgent(ctx)
	if err != nil {
		log.Fatalf("Failed to create hint HITL agent: %v", err)
	}

	payloadAgent, err := newHITLWithPayloadAgent(ctx)
	if err != nil {
		log.Fatalf("Failed to create payload HITL agent: %v", err)
	}

	sessionService := session.InMemoryService()
	sess, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  userID,
	})
	if err != nil {
		log.Fatalf("Failed to create session: %v", err)
	}

	for _, ag := range []agent.Agent{simpleAgent, hintAgent, payloadAgent} {
		r, err := runner.New(runner.Config{
			AppName:        appName,
			Agent:          ag,
			SessionService: sessionService,
		})
		if err != nil {
			log.Fatalf("Failed to create runner: %v", err)
		}

		userMsg := genai.NewContentFromText("Hello, please help me.", genai.RoleUser)
		for event, err := range r.Run(ctx, userID, sess.Session.ID(), userMsg, agent.RunConfig{
			StreamingMode: agent.StreamingModeNone,
		}) {
			if err != nil {
				log.Printf("Event error from %s: %v", ag.Name(), err)
				continue
			}
			if event.Content != nil {
				for _, p := range event.Content.Parts {
					if p.Text != "" {
						fmt.Printf("[%s]: %s\n", ag.Name(), p.Text)
					}
				}
			}
		}
	}
}
