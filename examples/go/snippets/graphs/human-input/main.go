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

// Package main demonstrates Human-in-the-Loop (HITL) patterns in ADK Go v2.
//
// NOTE: This file requires google.golang.org/adk/v2, available in ADK Go
// v2.0.0 and later.
//
// # Graph HITL (primary pattern for /graphs/ pages)
//
// In ADK Go v2, the primary way to add a human input node to a graph-based
// workflow is workflow.NewEmittingFunctionNode with workflow.ResumeOrRequestInput.
// This is the direct Go equivalent of the Python RequestInput node:
//
//   - On the first pass the node emits a session.RequestInput event
//     (surfaced via Event.RequestedInput) and returns ErrNodeInterrupted,
//     pausing the workflow.
//   - The workflow resumes after the client sends a reply. The node is
//     re-invoked from the top (RerunOnResume defaults to &true on dynamic
//     nodes; set it explicitly on EmittingFunctionNode), and
//     workflow.ResumeOrRequestInput returns the human's reply payload.
//
// # Tool-confirmation (secondary pattern, LLM-agent feature)
//
// Tool-confirmation (RequireConfirmation / ctx.RequestConfirmation) is a
// separate LLM-agent mechanism for yes/no approval prompts before a tool
// executes. It is not graph-node based.
package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/genai"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/llmagent"
	"google.golang.org/adk/v2/agent/workflowagent"
	"google.golang.org/adk/v2/model/gemini"
	"google.golang.org/adk/v2/session"
	"google.golang.org/adk/v2/tool"
	"google.golang.org/adk/v2/tool/functiontool"
	"google.golang.org/adk/v2/workflow"
)

const (
	appName   = "hitl_demo"
	userID    = "demo_user"
	modelName = "gemini-flash-latest"
)

// --8<-- [start:graph-hitl-get-started]
// newGraphHITLWorkflow demonstrates a graph HITL node using
// workflow.NewEmittingFunctionNode and workflow.ResumeOrRequestInput.
//
// This is the Go equivalent of the Python RequestInput node:
//
//	def step1():  # Human input step
//	    yield RequestInput(message="Enter a number:")
//
//	def step2(node_input):
//	    return node_input * 2
//
//	root_agent = Workflow(
//	    name="root_agent",
//	    edges=[('START', step1, step2)],
//	)
//
// On the first pass, step1Node emits a RequestInput event and pauses the
// workflow (ErrNodeInterrupted). After the human replies, the node is re-run
// and ResumeOrRequestInput returns the reply, which flows as typed input to
// step2Node via event.Output.
func newGraphHITLWorkflow() (agent.Agent, error) {
	rerun := true

	// step1Node: pauses for human input on the first pass, returns the
	// human's reply on resume. workflow.ResumeOrRequestInput handles both
	// phases — no manual re-entry bookkeeping needed.
	step1Node := workflow.NewEmittingFunctionNode[any, string]("step1",
		func(ctx agent.Context, _ any, emit func(*session.Event) error) (string, error) {
			reply, err := workflow.ResumeOrRequestInput(ctx, emit, session.RequestInput{
				InterruptID: "enter_number",
				Message:     "Enter a number:",
			})
			if err != nil {
				// ErrNodeInterrupted on first pass — workflow pauses here.
				return "", err
			}
			// On resume, reply is the human's text response.
			number, _ := reply.(string)
			return number, nil
		},
		workflow.NodeConfig{RerunOnResume: &rerun},
	)

	// step2Node: receives the human's input as its typed string input via
	// event.Output and doubles the number.
	step2Node := workflow.NewFunctionNode("step2",
		func(_ agent.Context, input string) (string, error) {
			return fmt.Sprintf("You entered: %s (doubled: %s%s)", input, input, input), nil
		},
		workflow.NodeConfig{},
	)

	return workflowagent.New(workflowagent.Config{
		Name:        "root_agent",
		Description: "Pauses for a number from the user, then doubles it.",
		Edges:       workflow.Chain(workflow.Start, step1Node, step2Node),
	})
}

// --8<-- [end:graph-hitl-get-started]

// --8<-- [start:graph-hitl-with-payload]
// ItineraryItem represents a single activity in a travel plan.
type ItineraryItem struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

// newItineraryReviewWorkflow demonstrates a graph HITL node that sends a
// structured payload alongside the input prompt so the client can render
// additional context for the user. This mirrors Python's:
//
//	async def get_user_feedback(node_input: ActivitiesList):
//	    yield RequestInput(
//	        message="Which items appeal to you?",
//	        payload=node_input,
//	        response_schema=UserFeedback,
//	    )
func newItineraryReviewWorkflow() (agent.Agent, error) {
	rerun := true

	// buildItineraryNode: generates an itinerary and passes it to the HITL
	// node as its typed output via event.Output.
	buildItineraryNode := workflow.NewFunctionNode("build_itinerary",
		func(_ agent.Context, _ any) ([]ItineraryItem, error) {
			return []ItineraryItem{
				{Name: "Eiffel Tower", Description: "Iconic iron lattice tower."},
				{Name: "Louvre Museum", Description: "World's largest art museum."},
				{Name: "Seine River Cruise", Description: "Scenic boat tour of Paris."},
			}, nil
		},
		workflow.NodeConfig{},
	)

	// reviewNode: sends the itinerary as payload alongside the prompt so the
	// client can display it. On resume, the human's selection is returned.
	reviewNode := workflow.NewEmittingFunctionNode[[]ItineraryItem, string]("get_user_feedback",
		func(ctx agent.Context, itinerary []ItineraryItem, emit func(*session.Event) error) (string, error) {
			reply, err := workflow.ResumeOrRequestInput(ctx, emit, session.RequestInput{
				InterruptID: "itinerary_review",
				Message:     fmt.Sprintf("Here is your recommended itinerary (%d activities). Which items appeal to you?", len(itinerary)),
				Payload:     itinerary, // structured payload rendered by the client
			})
			if err != nil {
				// ErrNodeInterrupted on first pass — workflow pauses here.
				return "", err
			}
			feedback, _ := reply.(string)
			return feedback, nil
		},
		workflow.NodeConfig{RerunOnResume: &rerun},
	)

	// finalNode: receives the user's feedback and produces a confirmation.
	finalNode := workflow.NewFunctionNode("finalize",
		func(_ agent.Context, feedback string) (string, error) {
			return fmt.Sprintf("Itinerary finalised with your feedback: %q", feedback), nil
		},
		workflow.NodeConfig{},
	)

	return workflowagent.New(workflowagent.Config{
		Name:        "concierge_workflow",
		Description: "Builds an itinerary, asks the user for feedback, then finalises.",
		Edges:       workflow.Chain(workflow.Start, buildItineraryNode, reviewNode, finalNode),
	})
}

// --8<-- [end:graph-hitl-with-payload]

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
func doubleNumber(_ agent.Context, args DoubleNumberArgs) (DoubleNumberResults, error) {
	return DoubleNumberResults{Result: args.Number * 2}, nil
}

// newSimpleHITLAgent creates an LLM agent with a tool that always requires
// user confirmation before it executes (tool-confirmation pattern).
func newSimpleHITLAgent(ctx context.Context) (agent.Agent, error) {
	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("failed to create model: %w", err)
	}

	doubleNumberTool, err := functiontool.New(
		functiontool.Config{
			Name:                "double_number",
			Description:         "Doubles the given number. Requires user approval before running.",
			RequireConfirmation: true,
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
// booking (tool-confirmation pattern with a custom hint message).
func bookFlight(ctx agent.Context, args BookFlightArgs) (BookFlightResults, error) {
	if confirmation := ctx.ToolConfirmation(); confirmation != nil {
		if !confirmation.Confirmed {
			return BookFlightResults{Status: "Booking cancelled by user."}, nil
		}
		return BookFlightResults{
			Status:        "Booking confirmed.",
			ConfirmNumber: "FLT-20251031",
		}, nil
	}

	hint := fmt.Sprintf(
		"The agent wants to book a flight from %s to %s on %s. Do you approve?",
		args.Origin, args.Destination, args.Date,
	)
	if err := ctx.RequestConfirmation(hint, nil); err != nil {
		return BookFlightResults{}, fmt.Errorf("failed to request confirmation: %w", err)
	}
	return BookFlightResults{Status: "Awaiting user approval."}, nil
}

// newHITLWithHintAgent creates an LLM agent whose bookFlight tool manually
// requests confirmation with a descriptive hint (tool-confirmation pattern).
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

func main() {
	graphAgent, err := newGraphHITLWorkflow()
	if err != nil {
		log.Fatalf("Failed to create graph HITL workflow: %v", err)
	}
	log.Printf("Created graph HITL workflow: %s", graphAgent.Name())

	itineraryAgent, err := newItineraryReviewWorkflow()
	if err != nil {
		log.Fatalf("Failed to create itinerary review workflow: %v", err)
	}
	log.Printf("Created itinerary review workflow: %s", itineraryAgent.Name())

	ctx := context.Background()
	simpleAgent, err := newSimpleHITLAgent(ctx)
	if err != nil {
		log.Fatalf("Failed to create simple HITL agent: %v", err)
	}
	log.Printf("Created simple HITL agent: %s", simpleAgent.Name())

	hintAgent, err := newHITLWithHintAgent(ctx)
	if err != nil {
		log.Fatalf("Failed to create hint HITL agent: %v", err)
	}
	log.Printf("Created hint HITL agent: %s", hintAgent.Name())
}
