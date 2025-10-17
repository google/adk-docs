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
	"encoding/json"
	"fmt"
	"log"
	"strings"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/genai"
)

const (
	appName   = "go_safety_example_app"
	userID    = "go_safety_user"
	sessionID = "go_safety_session"
	modelID   = "gemini-2.0-flash"
)

// --8<-- [start:policy_setup]
// conceptualSetup demonstrates how policy data might be set in the session state.
// In a real ADK app, this would be part of the application logic before running an agent.
func conceptualSetup(s session.Session) {
	policy := map[string]any{
		"select_only": true,
		"tables":      []string{"mytable1", "mytable2"},
	}

	// Storing policy where the tool can access it via ToolContext later.
	s.State().Set("query_tool_policy", policy)
	s.State().Set("session_user_id", "user123") // For callback validation.
	fmt.Println("Conceptual Setup: Policy and session_user_id have been set in the session state.")
}

// --8<-- [end:policy_setup]

// --8<-- [start:in_tool_guardrail]
// Hypothetical function to simulate parsing a SQL query.
func explainQuery(query string) []string {
	if strings.Contains(strings.ToLower(query), "mytable1") {
		return []string{"mytable1"}
	}
	if strings.Contains(strings.ToLower(query), "unauthorized_table") {
		return []string{"unauthorized_table"}
	}
	return []string{}
}

// Helper function to check if a is a subset of b.
func isSubset(a, b []string) bool {
	set := make(map[string]bool)
	for _, item := range b {
		set[item] = true
	}
	for _, item := range a {
		if _, found := set[item]; !found {
			return false
		}
	}
	return true
}

type queryResult struct {
	Status  string   `json:"status"`
	Results []string `json:"results,omitempty"`
	Error   string   `json:"error,omitempty"`
}

type queryArgs struct {
	Query       string `json:"query"`
	UserIDParam string `json:"user_id_param"`
}

// query demonstrates in-tool guardrails by checking a policy from the context.
func query(tctx tool.Context, args queryArgs) queryResult {
	// In the Go ADK, state is accessed directly from the tool.Context using the State() method.
	// This is the functional equivalent of `tool_context.invocation_context.session.state`
	// in the Python examples.
	policyVal, err := tctx.State().Get("query_tool_policy")
	if err != nil {
		return queryResult{Status: "error", Error: "Internal error: query_tool_policy not found in state."}
	}
	policy, _ := policyVal.(map[string]any)
	actualTables := explainQuery(args.Query)

	// --- Policy Enforcement ---
	if tablesVal, ok := policy["tables"]; ok {
		if tables, ok := tablesVal.([]string); ok {
			if !isSubset(actualTables, tables) {
				allowed := strings.Join(tables, ", ")
				if allowed == "" {
					allowed = "(None defined)"
				}
				errMsg := fmt.Sprintf("Query targets unauthorized tables. Allowed: %s", allowed)
				fmt.Printf("Tool Guardrail: %s\n", errMsg)
				return queryResult{Status: "error", Error: errMsg}
			}
		}
	}

	if selectOnly, _ := policy["select_only"].(bool); selectOnly {
		if !strings.HasPrefix(strings.ToUpper(strings.TrimSpace(args.Query)), "SELECT") {
			errMsg := "Policy restricts queries to SELECT statements only."
			fmt.Printf("Tool Guardrail: %s\n", errMsg)
			return queryResult{Status: "error", Error: errMsg}
		}
	}
	// --- End Policy Enforcement ---

	fmt.Printf("Executing validated query (hypothetical): %s\n", args.Query)
	return queryResult{Status: "success", Results: []string{"result1", "result2"}}
}

// --8<-- [end:in_tool_guardrail]

// --8<-- [start:callback_guardrail]
// validateToolParams is a BeforeModelCallback that inspects the outgoing LLM
// request for tool calls and validates their parameters against session state.
func validateToolParams(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
	fmt.Println("Callback triggered before model call.")

	// Iterate through the content to find function calls
	for _, content := range req.Contents {
		for _, part := range content.Parts {
			fc := part.FunctionCall
			if fc == nil || fc.Name != "database_query" {
				continue
			}

			fmt.Printf("Callback: Intercepted call to '%s' with args: %v\n", fc.Name, fc.Args)

			// Example validation: Check if a required user ID from state matches an arg
			expectedUserID, err := ctx.State().Get("session_user_id")
			if err != nil {
				return nil, fmt.Errorf("internal error: session_user_id not found in state")
			}

			actualUserIDInArgs, _ := fc.Args["user_id_param"].(string)

			if actualUserIDInArgs != expectedUserID {
				fmt.Println("Callback Validation Failed: User ID mismatch!")
				// By returning a response here, we prevent the model call and the tool execution.
				// The content of this response will be passed back to the agent's main loop.
				errorContent := genai.NewContentFromText("Tool call blocked by security callback: User ID mismatch.", "model")
				return &model.LLMResponse{Content: errorContent}, nil
			}
			fmt.Println("Callback validation passed.")
		}
	}

	// Return nil, nil to allow the model call to proceed.
	return nil, nil
}

// --8<-- [end:callback_guardrail]

func main() {
	fmt.Println("This example demonstrates safety guardrails by directly invoking the tool and callback functions.")

	// --- Setup a mock session and state ---
	mockSession := session.NewMock()
	conceptualSetup(mockSession)

	// --- Scenario 1: Test the in-tool guardrail ---
	fmt.Println("\n--- Testing In-Tool Guardrail ---")
	mockToolCtx := tool.NewMock(mockSession)

	// Test Case 1.1: Valid query
	fmt.Println("\n[Test Case 1.1: Valid Query]")
	validArgs := queryArgs{Query: "SELECT * FROM mytable1", UserIDParam: "user123"}
	result1 := query(mockToolCtx, validArgs)
	fmt.Printf("Tool Result: %+v\n", result1)

	// Test Case 1.2: Unauthorized table
	fmt.Println("\n[Test Case 1.2: Unauthorized Table]")
	unauthTblArgs := queryArgs{Query: "SELECT * FROM unauthorized_table", UserIDParam: "user123"}
	result2 := query(mockToolCtx, unauthTblArgs)
	fmt.Printf("Tool Result: %+v\n", result2)

	// Test Case 1.3: Non-SELECT query
	fmt.Println("\n[Test Case 1.3: Non-SELECT Query]")
	nonSelectArgs := queryArgs{Query: "DELETE FROM mytable1", UserIDParam: "user123"}
	result3 := query(mockToolCtx, nonSelectArgs)
	fmt.Printf("Tool Result: %+v\n", result3)

	// --- Scenario 2: Test the BeforeModel callback guardrail ---
	fmt.Println("\n\n--- Testing Callback Guardrail ---")
	mockCallbackCtx := agent.NewMock(mockSession)

	// Test Case 2.1: Valid user ID in tool args
	fmt.Println("\n[Test Case 2.1: Valid User ID]")
	validCall := &genai.FunctionCall{
		Name: "database_query",
		Args: map[string]any{"user_id_param": "user123"},
	}
	req1 := &model.LLMRequest{Contents: []*genai.Content{{Parts: []genai.Part{validCall}}}}
	resp1, err1 := validateToolParams(mockCallbackCtx, req1)
	if err1 != nil {
		log.Fatalf("Callback Error: %v", err1)
	}
	if resp1 != nil {
		fmt.Printf("Callback Result: Blocked with message: %s\n", textParts(resp1.Content)[0])
	} else {
		fmt.Println("Callback Result: Allowed")
	}

	// Test Case 2.2: Invalid user ID in tool args
	fmt.Println("\n[Test Case 2.2: Invalid User ID]")
	invalidCall := &genai.FunctionCall{
		Name: "database_query",
		Args: map[string]any{"user_id_param": "user456"},
	}
	req2 := &model.LLMRequest{Contents: []*genai.Content{{Parts: []genai.Part{invalidCall}}}}
	resp2, err2 := validateToolParams(mockCallbackCtx, req2)
	if err2 != nil {
		log.Fatalf("Callback Error: %v", err2)
	}
	if resp2 != nil {
		fmt.Printf("Callback Result: Blocked with message: %s\n", textParts(resp2.Content)[0])
	} else {
		fmt.Println("Callback Result: Allowed")
	}
}


// --- Mock Implementations for Demonstration ---

// mockState allows direct manipulation of a map for testing.
type mockState struct {
	data map[string]any
}

func (m *mockState) Get(key string) (any, error) {
	val, ok := m.data[key]
	if !ok {
		return nil, fmt.Errorf("state key not found: %s", key)
	}
	return val, nil
}

func (m *mockState) Set(key string, val any) error {
	m.data[key] = val
	return nil
}

func (m *mockState) All() iter.Seq2[string, any] {
	return func(yield func(string, any) bool) {
		for k, v := range m.data {
			if !yield(k, v) {
				return
			}
		}
	}
}

// mockSession provides a mock session.Session for testing.
type mockSession struct {
	state agent.State
}

func (m *mockSession) ID() string                { return "mock-session-id" }
func (m *mockSession) AppName() string           { return "mock-app" }
func (m *mockSession) UserID() string            { return "mock-user" }
func (m *mockSession) State() agent.State        { return m.state }
func (m *mockSession) Events() session.Events    { return nil } // Not needed for this test
func (m *mockSession) LastUpdateTime() time.Time { return time.Now() }

// NewMock creates a new mock session for testing.
func (s *session.Session) NewMock() session.Session {
	return &mockSession{state: &mockState{data: make(map[string]any)}}
}

// mockCallbackContext provides a mock agent.CallbackContext for testing.
type mockCallbackContext struct {
	session session.Session
}

func (m *mockCallbackContext) InvocationID() string         { return "mock-inv-id" }
func (m *mockCallbackContext) Agent() agent.Agent           { return nil }
func (m *mockCallbackContext) Session() session.Session     { return m.session }
func (m *mockCallbackContext) State() agent.State           { return m.session.State() }
func (m *mockCallbackContext) Artifacts() agent.Artifacts   { return nil }
func (m *mockCallbackContext) Memory() agent.Memory         { return nil }
func (m *mockCallbackContext) UserContent() *genai.Content  { return nil }
func (m *mockCallbackContext) Branch() string               { return "" }
func (m *mockCallbackContext) RunConfig() *agent.RunConfig  { return nil }

// NewMock creates a new mock callback context for testing.
func (a *agent.Agent) NewMock(s session.Session) agent.CallbackContext {
	return &mockCallbackContext{session: s}
}

// mockToolContext provides a mock tool.Context for testing.
type mockToolContext struct {
	session session.Session
}

func (m *mockToolContext) InvocationContext() agent.InvocationContext { return nil } // Not needed for this test
func (m *mockToolContext) FunctionCallID() string                     { return "mock-fc-id" }
func (m *mockToolContext) Actions() *session.EventActions             { return &session.EventActions{} }
func (m *mockToolContext) SearchMemory(ctx context.Context, query string) ([]memory.Entry, error) { return nil, nil }
func (m *mockToolContext) State() agent.State                         { return m.session.State() }

// NewMock creates a new mock tool context for testing.
func (t *tool.Tool) NewMock(s session.Session) tool.Context {
	return &mockToolContext{session: s}
}
