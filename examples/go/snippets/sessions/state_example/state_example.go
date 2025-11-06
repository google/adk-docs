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
	"time"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"
	"google.golang.org/genai"
)

const (
	appName   = "state_example_app"
	userID    = "user1234"
	sessionID = "1234"
	modelID   = "gemini-2.0-flash" // Replace with a valid model name
)

// --8<-- [start:greeting]
//  1. GreetingAgent demonstrates using `OutputKey` to save an agent's
//     final text response directly into the session state.
func greetingAgentExample(sessionService session.Service) {
	fmt.Println("--- Running GreetingAgent (output_key) Example ---")
	ctx := context.Background()

	modelGreeting, err := gemini.NewModel(ctx, modelID, nil)
	if err != nil {
		log.Fatalf("Failed to create Gemini model for greeting agent: %v", err)
	}
	greetingAgent, err := llmagent.New(llmagent.Config{
		Name:        "Greeter",
		Model:       modelGreeting,
		Instruction: "Generate a short, friendly greeting.",
		OutputKey:   "last_greeting",
	})
	if err != nil {
		log.Fatalf("Failed to create greeting agent: %v", err)
	}

	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          agent.Agent(greetingAgent),
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatalf("Failed to create runner: %v", err)
	}

	// Run the agent
	userMessage := genai.NewContentFromText("Hello", "user")
	for event, err := range r.Run(ctx, userID, sessionID, userMessage, agent.RunConfig{}) {
		if err != nil {
			log.Printf("Agent Error: %v", err)
			continue
		}
		if isFinalResponse(event) {
			if event.LLMResponse.Content != nil {
				fmt.Printf("Agent responded with: %q\n", textParts(event.LLMResponse.Content))
			} else {
				fmt.Println("Agent responded.")
			}
		}
	}

	// Check the updated state
	resp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
	if err != nil {
		log.Fatalf("Failed to get session: %v", err)
	}
	lastGreeting, _ := resp.Session.State().Get("last_greeting")
	fmt.Printf("State after agent run: last_greeting = %q\n\n", lastGreeting)
}

// --8<-- [end:greeting]

// --8<-- [start:manual]
//  2. manualStateUpdateExample demonstrates creating an event with explicit
//     state changes (a "state_delta") to update multiple keys, including
//     those with user- and temp- prefixes.
func manualStateUpdateExample(sessionService session.Service) {
	fmt.Println("--- Running Manual State Update (EventActions) Example ---")
	ctx := context.Background()
	s, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
	if err != nil {
		log.Fatalf("Failed to get session: %v", err)
	}
	retrievedSession := s.Session

	// Define state changes
	loginCount, _ := retrievedSession.State().Get("user:login_count")
	newLoginCount := 1
	if lc, ok := loginCount.(int); ok {
		newLoginCount = lc + 1
	}

	stateChanges := map[string]any{
		"task_status":            "active",
		"user:login_count":       newLoginCount,
		"user:last_login_ts":     time.Now().Unix(),
		"temp:validation_needed": true,
	}

	// Create an event with the state changes
	systemEvent := session.NewEvent("inv_login_update")
	systemEvent.Author = "system"
	systemEvent.Actions.StateDelta = stateChanges

	// Append the event to update the state
	if err := sessionService.AppendEvent(ctx, retrievedSession, systemEvent); err != nil {
		log.Fatalf("Failed to append event: %v", err)
	}
	fmt.Println("`append_event` called with explicit state delta.")

	// Check the updated state
	updatedResp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
	if err != nil {
		log.Fatalf("Failed to get session: %v", err)
	}
	taskStatus, _ := updatedResp.Session.State().Get("task_status")
	loginCount, _ = updatedResp.Session.State().Get("user:login_count")
	lastLogin, _ := updatedResp.Session.State().Get("user:last_login_ts")
	temp, err := updatedResp.Session.State().Get("temp:validation_needed") // This should fail or be nil

	fmt.Printf("State after event: task_status=%q, user:login_count=%v, user:last_login_ts=%v\n", taskStatus, loginCount, lastLogin)
	if err != nil {
		fmt.Printf("As expected, temp state was not persisted: %v\n\n", err)
	} else {
		fmt.Printf("Unexpected temp state value: %v\n\n", temp)
	}
}

// --8<-- [end:manual]

// --8<-- [start:context]
//  3. contextStateUpdateExample demonstrates the recommended way to modify state
//     from within a tool function using the provided `tool.Context`.
func contextStateUpdateExample(sessionService session.Service) {
	fmt.Println("--- Running Context State Update (ToolContext) Example ---")
	ctx := context.Background()

	// Define the tool that modifies state
	updateActionCountTool, err := functiontool.New[struct{}, struct{}](
		functiontool.Config{Name: "update_action_count", Description: "Updates the user action count in the state."},
		func(tctx tool.Context, args struct{}) struct{} {
			actx, ok := tctx.(agent.CallbackContext)
			if !ok {
				log.Fatalf("tool.Context is not of type agent.CallbackContext")
			}
			s, err := actx.State().Get("user_action_count")
			if err != nil {
				log.Printf("could not get user_action_count: %v", err)
			}
			newCount := 1
			if c, ok := s.(int); ok {
				newCount = c + 1
			}
			if err := actx.State().Set("user_action_count", newCount); err != nil {
				log.Printf("could not set user_action_count: %v", err)
			}
			if err := actx.State().Set("temp:last_operation_status", "success from tool"); err != nil {
				log.Printf("could not set temp:last_operation_status: %v", err)
			}
			fmt.Println("Tool: Updated state via agent.CallbackContext.")
			return struct{}{}
		},
	)
	if err != nil {
		log.Fatalf("Failed to create tool: %v", err)
	}

	// Define an agent that uses the tool
	modelTool, err := gemini.NewModel(ctx, modelID, nil)
	if err != nil {
		log.Fatalf("Failed to create Gemini model for tool agent: %v", err)
	}
	toolAgent, err := llmagent.New(llmagent.Config{
		Name:        "ToolAgent",
		Model:       modelTool,
		Instruction: "Use the update_action_count tool.",
		Tools:       []tool.Tool{updateActionCountTool},
	})
	if err != nil {
		log.Fatalf("Failed to create tool agent: %v", err)
	}

	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          agent.Agent(toolAgent),
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatalf("Failed to create runner: %v", err)
	}

	// Run the agent to trigger the tool
	userMessage := genai.NewContentFromText("Please update the action count.", "user")
	for _, err := range r.Run(ctx, userID, sessionID, userMessage, agent.RunConfig{}) {
		if err != nil {
			log.Printf("Agent Error: %v", err)
		}
	}

	// Check the updated state
	resp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
	if err != nil {
		log.Fatalf("Failed to get session: %v", err)
	}
	actionCount, _ := resp.Session.State().Get("user_action_count")
	fmt.Printf("State after tool run: user_action_count = %v\n", actionCount)
}

// --8<-- [end:context]
func main() {
	ctx := context.Background()
	sessionService := session.InMemoryService()

	// Initialize session with some state
	_, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName:   appName,
		UserID:    userID,
		SessionID: sessionID,
		State: map[string]any{
			"user:login_count": 0,
			"task_status":      "idle",
		},
	})
	if err != nil {
		log.Fatalf("Failed to create session: %v", err)
	}

	s, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
	if err != nil {
		log.Fatalf("Failed to get session: %v", err)
	}
	taskStatus, _ := s.Session.State().Get("task_status")
	loginCount, _ := s.Session.State().Get("user:login_count")
	fmt.Printf("Initial state: task_status=%q, user:login_count=%v\n\n", taskStatus, loginCount)

	greetingAgentExample(sessionService)
	manualStateUpdateExample(sessionService)
	contextStateUpdateExample(sessionService)
}

// --- Helper Functions ---

func isFinalResponse(ev *session.Event) bool {
	if ev.Actions.SkipSummarization || len(ev.LongRunningToolIDs) > 0 {
		return true
	}
	if ev.LLMResponse.Content == nil {
		return true
	}
	return !hasFunctionCalls(&ev.LLMResponse) && !hasFunctionResponses(&ev.LLMResponse) && !ev.LLMResponse.Partial && !hasTrailingCodeExecutionResult(&ev.LLMResponse)
}

func hasFunctionCalls(resp *model.LLMResponse) bool {
	if resp == nil || resp.Content == nil {
		return false
	}
	for _, part := range resp.Content.Parts {
		if part.FunctionCall != nil {
			return true
		}
	}
	return false
}

func hasFunctionResponses(resp *model.LLMResponse) bool {
	if resp == nil || resp.Content == nil {
		return false
	}
	for _, part := range resp.Content.Parts {
		if part.FunctionResponse != nil {
			return true
		}
	}
	return false
}

func hasTrailingCodeExecutionResult(resp *model.LLMResponse) bool {
	if resp == nil || resp.Content == nil || len(resp.Content.Parts) == 0 {
		return false
	}
	lastPart := resp.Content.Parts[len(resp.Content.Parts)-1]
	return lastPart.CodeExecutionResult != nil
}

func textParts(c *genai.Content) (ret []string) {
	if c == nil {
		return nil
	}
	for _, p := range c.Parts {
		if p.Text != "" {
			ret = append(ret, p.Text)
		}
	}
	return ret
}
