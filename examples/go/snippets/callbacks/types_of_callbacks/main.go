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
	"regexp"
	"strings"

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

// --8<-- [end:imports]

const (
	modelName = "gemini-2.5-flash"
	userID    = "user_1"
	appName   = "CallbackExamplesApp"
)

// --8<-- [start:before_agent_example]
// 1. Define the Callback Function
func onBeforeAgent(ctx agent.CallbackContext) (*genai.Content, error) {
	agentName := ctx.AgentName()
	log.Printf("[Callback] Entering agent: %s", agentName)
	if skip, _ := ctx.State().Get("skip_llm_agent"); skip == true {
		log.Printf("[Callback] State condition met: Skipping agent %s", agentName)
		return genai.NewContentFromText(
				fmt.Sprintf("Agent %s skipped by before_agent_callback.", agentName),
				genai.RoleModel,
			),
			nil
	}
	log.Printf("[Callback] State condition not met: Running agent %s", agentName)
	return nil, nil
}

// 2. Define a function to set up and run the agent with the callback.
func runBeforeAgentExample() {
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}

	// 3. Register the callback in the agent configuration.
	llmCfg := llmagent.Config{
		Name:                 "AgentWithBeforeAgentCallback",
		BeforeAgentCallbacks: []agent.BeforeAgentCallback{onBeforeAgent},
		Model:                geminiModel,
		Instruction:          "You are a concise assistant.",
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
	if err != nil {
		log.Fatalf("FATAL: Failed to create runner: %v", err)
	}

	// 4. Run scenarios to demonstrate the callback's behavior.
	log.Println("--- SCENARIO 1: Agent should run normally ---")
	runScenario(ctx, r, sessionService, appName, "session_normal", nil, "Hello, world!")

	log.Println("\n--- SCENARIO 2: Agent should be skipped ---")
	runScenario(ctx, r, sessionService, appName, "session_skip", map[string]any{"skip_llm_agent": true}, "This should be skipped.")
}

// --8<-- [end:before_agent_example]

// --8<-- [start:after_agent_example]
func onAfterAgent(ctx agent.CallbackContext) (*genai.Content, error) {
	agentName := ctx.AgentName()
	invocationID := ctx.InvocationID()
	state := ctx.State()

	log.Printf("\n[Callback] Exiting agent: %s (Inv: %s)", agentName, invocationID)
	log.Printf("[Callback] Current State: %v", state)

	if addNote, _ := state.Get("add_concluding_note"); addNote == true {
		log.Printf("[Callback] State condition 'add_concluding_note=True' met: Replacing agent %s's output.", agentName)
		return genai.NewContentFromText(
			"Concluding note added by after_agent_callback, replacing original output.",
			genai.RoleModel,
		), nil
	}

	log.Printf("[Callback] State condition not met: Using agent %s's original output.", agentName)
	return nil, nil
}

func runAfterAgentExample() {
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}

	llmCfg := llmagent.Config{
		Name:                "AgentWithAfterAgentCallback",
		AfterAgentCallbacks: []agent.AfterAgentCallback{onAfterAgent},
		Model:               geminiModel,
		Instruction:         "You are a simple agent. Just say 'Processing complete!'",
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
	if err != nil {
		log.Fatalf("FATAL: Failed to create runner: %v", err)
	}

	log.Println("--- SCENARIO 1: Should use original output ---")
	runScenario(ctx, r, sessionService, appName, "session_normal", nil, "Process this.")

	log.Println("\n--- SCENARIO 2: Should replace output ---")
	runScenario(ctx, r, sessionService, appName, "session_modify", map[string]any{"add_concluding_note": true}, "Process and add note.")
}

// --8<-- [end:after_agent_example]

// --8<-- [start:before_model_example]
func onBeforeModel(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
	log.Printf("[Callback] BeforeModel triggered for agent %q.", ctx.AgentName())

	// Modification Example: Add a prefix to the system instruction.
	if req.Config.SystemInstruction != nil {
		prefix := "[Modified by Callback] "
		// This is a simplified example; production code might need deeper checks.
		if len(req.Config.SystemInstruction.Parts) > 0 {
			req.Config.SystemInstruction.Parts[0].Text = prefix + req.Config.SystemInstruction.Parts[0].Text
		} else {
			req.Config.SystemInstruction.Parts = append(req.Config.SystemInstruction.Parts, &genai.Part{Text: prefix})
		}
		log.Printf("[Callback] Modified system instruction.")
	}

	// Skip Example: Check for "BLOCK" in the user's prompt.
	for _, content := range req.Contents {
		for _, part := range content.Parts {
			if strings.Contains(strings.ToUpper(part.Text), "BLOCK") {
				log.Println("[Callback] 'BLOCK' keyword found. Skipping LLM call.")
				return &model.LLMResponse{
					Content: &genai.Content{
						Parts: []*genai.Part{{Text: "LLM call was blocked by before_model_callback."}},
						Role:  "model",
					},
				}, nil
			}
		}
	}

	log.Println("[Callback] Proceeding with LLM call.")
	return nil, nil
}

func runBeforeModelExample() {
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}

	llmCfg := llmagent.Config{
		Name:                 "AgentWithBeforeModelCallback",
		Model:                geminiModel,
		BeforeModelCallbacks: []llmagent.BeforeModelCallback{onBeforeModel},
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
	if err != nil {
		log.Fatalf("FATAL: Failed to create runner: %v", err)
	}

	log.Println("--- SCENARIO 1: Should proceed to LLM ---")
	runScenario(ctx, r, sessionService, appName, "session_normal", nil, "Tell me a fun fact.")

	log.Println("\n--- SCENARIO 2: Should be blocked by callback ---")
	runScenario(ctx, r, sessionService, appName, "session_blocked", nil, "write a joke on BLOCK")
}

// --8<-- [end:before_model_example]

// --8<-- [start:after_model_example]
func onAfterModel(ctx agent.CallbackContext, resp *model.LLMResponse, respErr error) (*model.LLMResponse, error) {
	log.Printf("[Callback] AfterModel triggered for agent %q.", ctx.AgentName())
	if respErr != nil {
		log.Printf("[Callback] Model returned an error: %v. Passing it through.", respErr)
		return nil, respErr
	}
	if resp == nil || resp.Content == nil || len(resp.Content.Parts) == 0 {
		log.Println("[Callback] Response is nil or has no parts, nothing to process.")
		return nil, nil
	}
	// Check for function calls and pass them through without modification.
	if resp.Content.Parts[0].FunctionCall != nil {
		log.Println("[Callback] Response is a function call. No modification.")
		return nil, nil
	}

	originalText := resp.Content.Parts[0].Text

	// Use a case-insensitive regex with word boundaries to find "joke".
	re := regexp.MustCompile(`(?i)\bjoke\b`)
	if !re.MatchString(originalText) {
		log.Println("[Callback] 'joke' not found. Passing original response through.")
		return nil, nil
	}

	log.Println("[Callback] 'joke' found. Modifying response.")
	// Use a replacer function to handle capitalization.
	modifiedText := re.ReplaceAllStringFunc(originalText, func(s string) string {
		if strings.ToUpper(s) == "JOKE" {
			if s == "Joke" {
				return "Funny story"
			}
			return "funny story"
		}
		return s // Should not be reached with this regex, but it's safe.
	})

	resp.Content.Parts[0].Text = modifiedText
	return resp, nil
}

func runAfterModelExample() {
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}

	llmCfg := llmagent.Config{
		Name:                "AgentWithAfterModelCallback",
		Model:               geminiModel,
		AfterModelCallbacks: []llmagent.AfterModelCallback{onAfterModel},
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
	if err != nil {
		log.Fatalf("FATAL: Failed to create runner: %v", err)
	}

	log.Println("--- SCENARIO 1: Response should be modified ---")
	runScenario(ctx, r, sessionService, appName, "session_modify", nil, `Give me a paragraph about different styles of jokes.`)
}

// --8<-- [end:after_model_example]

// --8<-- [start:tool_defs]
// GetCapitalCityArgs defines the arguments for the getCapitalCity tool.
type GetCapitalCityArgs struct {
	Country string `json:"country" jsonschema:"The country to get the capital of."`
}

// getCapitalCity is a tool that returns the capital of a given country.
func getCapitalCity(ctx tool.Context, args *GetCapitalCityArgs) string {
	capitals := map[string]string{
		"canada":        "Ottawa",
		"france":        "Paris",
		"germany":       "Berlin",
		"united states": "Washington, D.C.",
	}
	capital, ok := capitals[strings.ToLower(args.Country)]
	if !ok {
		return "<Unknown>"
	}
	return capital
}

// --8<-- [end:tool_defs]

// --8<-- [start:before_tool_example]
func onBeforeTool(ctx tool.Context, t tool.Tool, args map[string]any) (map[string]any, error) {
	log.Printf("[Callback] BeforeTool triggered for tool %q in agent %q.", t.Name(), ctx.AgentName())
	log.Printf("[Callback] Original args: %v", args)

	if t.Name() == "getCapitalCity" {
		if country, ok := args["country"].(string); ok {
			if strings.ToLower(country) == "canada" {
				log.Println("[Callback] Detected 'Canada'. Modifying args to 'France'.")
				args["country"] = "France"
				return args, nil // Proceed with modified args
			} else if strings.ToUpper(country) == "BLOCK" {
				log.Println("[Callback] Detected 'BLOCK'. Skipping tool execution.")
				// Skip tool and return a custom result.
				return map[string]any{"result": "Tool execution was blocked by before_tool_callback."}, nil
			}
		}
	}
	log.Println("[Callback] Proceeding with original or previously modified args.")
	return nil, nil // Proceed with original args
}

func runBeforeToolExample() {
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}
	capitalTool, err := functiontool.New[*GetCapitalCityArgs, string](functiontool.Config{
		Name:        "getCapitalCity",
		Description: "Retrieves the capital city of a given country.",
	}, getCapitalCity)
	if err != nil {
		log.Fatalf("FATAL: Failed to create function tool: %v", err)
	}

	llmCfg := llmagent.Config{
		Name:                "AgentWithBeforeToolCallback",
		Model:               geminiModel,
		Tools:               []tool.Tool{capitalTool},
		BeforeToolCallbacks: []llmagent.BeforeToolCallback{onBeforeTool},
		Instruction:         "You are an agent that can find capital cities. Use the getCapitalCity tool.",
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}
	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
	if err != nil {
		log.Fatalf("FATAL: Failed to create runner: %v", err)
	}

	log.Println("--- SCENARIO 1: Args should be modified ---")
	runScenario(ctx, r, sessionService, appName, "session_tool_modify", nil, "What is the capital of Canada?")

	log.Println("--- SCENARIO 2: Tool call should be blocked ---")
	runScenario(ctx, r, sessionService, appName, "session_tool_block", nil, "capital of BLOCK")
}

// --8<-- [end:before_tool_example]

// --8<-- [start:after_tool_example]
func onAfterTool(ctx tool.Context, t tool.Tool, args map[string]any, result map[string]any, err error) (map[string]any, error) {
	log.Printf("[Callback] AfterTool triggered for tool %q in agent %q.", t.Name(), ctx.AgentName())
	log.Printf("[Callback] Original result: %v", result)

	if err != nil {
		log.Printf("[Callback] Tool run produced an error: %v. Passing through.", err)
		return nil, err
	}

	if t.Name() == "getCapitalCity" {
		if originalResult, ok := result["result"].(string); ok && originalResult == "Washington, D.C." {
			log.Println("[Callback] Detected 'Washington, D.C.'. Modifying tool response.")
			modifiedResult := make(map[string]any)
			for k, v := range result {
				modifiedResult[k] = v
			}
			modifiedResult["result"] = fmt.Sprintf("%s (Note: This is the capital of the USA).", originalResult)
			modifiedResult["note_added_by_callback"] = true
			return modifiedResult, nil
		}
	}

	log.Println("[Callback] Passing original tool response through.")
	return nil, nil
}

func runAfterToolExample() {
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}
	capitalTool, err := functiontool.New[*GetCapitalCityArgs, string](functiontool.Config{
		Name:        "getCapitalCity",
		Description: "Retrieves the capital city of a given country.",
	}, getCapitalCity)
	if err != nil {
		log.Fatalf("FATAL: Failed to create function tool: %v", err)
	}

	llmCfg := llmagent.Config{
		Name:               "AgentWithAfterToolCallback",
		Model:              geminiModel,
		Tools:              []tool.Tool{capitalTool},
		AfterToolCallbacks: []llmagent.AfterToolCallback{onAfterTool},
		Instruction:        "You are an agent that finds capital cities. Use the getCapitalCity tool.",
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}
	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
	if err != nil {
		log.Fatalf("FATAL: Failed to create runner: %v", err)
	}

	log.Println("--- SCENARIO 1: Result should be modified ---")
	runScenario(ctx, r, sessionService, appName, "session_tool_after_modify", nil, "capital of united states")
}

// --8<-- [end:after_tool_example]

func main() {
	log.Println("--- Running BeforeAgent Example ---")
	runBeforeAgentExample()

	log.Println("\n\n--- Running AfterAgent Example ---")
	runAfterAgentExample()

	log.Println("\n\n--- Running BeforeModel Example ---")
	runBeforeModelExample()

	log.Println("\n\n--- Running AfterModel Example ---")
	runAfterModelExample()

	log.Println("\n\n--- Running BeforeTool Example ---")
	runBeforeToolExample()

	log.Println("\n\n--- Running AfterTool Example ---")
	runAfterToolExample()
}

// Generic helper to run a single scenario.
func runScenario(ctx context.Context, r *runner.Runner, sessionService session.Service, appName, sessionID string, initialState map[string]any, prompt string) {
	log.Printf("Running scenario for session: %s, initial state: %v", sessionID, initialState)
	sessionResp, err := sessionService.Create(ctx, &session.CreateRequest{AppName: appName, UserID: userID, SessionID: sessionID, State: initialState})
	if err != nil {
		log.Fatalf("FATAL: Failed to create session: %v", err)
	}

	input := genai.NewContentFromText(prompt, genai.RoleUser)
	events := r.Run(ctx, sessionResp.Session.UserID(), sessionResp.Session.ID(), input, agent.RunConfig{})
	for event, err := range events {
		if err != nil {
			log.Printf("ERROR during agent execution: %v", err)
			return
		}

		// Print only the final output from the agent.
		if event != nil && event.Content != nil && len(event.Content.Parts) > 0 {
			fmt.Printf("Final Output for %s: [%s] %s\n", sessionID, event.Author, event.LLMResponse.Content.Parts[0].Text)
		} else {
			log.Printf("Final response for %s received, but it has no content to display.", sessionID)
		}
	}
}
