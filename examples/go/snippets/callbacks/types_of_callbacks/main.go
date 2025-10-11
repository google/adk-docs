package main

import (
	"context"
	"fmt"
	"log"
	"strings"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/genai"
)

const (
	modelName = "gemini-2.5-flash"
)

// --8<-- [start:imports]
// The package and import block is included here.
// In the documentation, this snippet is reused for each example.
// --8<-- [end:imports]

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
		Name:        "AgentWithBeforeAgentCallback",
		BeforeAgent: []agent.BeforeAgentCallback{onBeforeAgent},
		Model:       geminiModel,
		Instruction: "You are a concise assistant.",
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	const appName = "BeforeAgentApp"
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
func onAfterAgent(ctx agent.CallbackContext, finalEvent *session.Event, runErr error) (*genai.Content, error) {
	agentName := ctx.AgentName()
	invocationID := ctx.InvocationID()
	state := ctx.State()

	log.Printf("\n[Callback] Exiting agent: %s (Inv: %s)", agentName, invocationID)
	log.Printf("[Callback] Current State: %v", state)

	if runErr != nil {
		log.Printf("[Callback] Agent run produced an error: %v. Passing through.", runErr)
		return nil, runErr
	}

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
		Name:       "AgentWithAfterAgentCallback",
		AfterAgent: []agent.AfterAgentCallback{onAfterAgent},
		Model:      geminiModel,
		Instruction: "You are a simple agent. Just say 'Processing complete!'",
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	const appName = "AfterAgentApp"
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
	for _, content := range req.Contents {
		for _, part := range content.Parts {
			if strings.Contains(part.Text, "BLOCK") {
				log.Println("[Callback] 'BLOCK' keyword found. Skipping LLM call.")
				return &model.LLMResponse{
					Content: &genai.Content{
						Parts: []*genai.Part{{Text: "LLM call was blocked by before_model_callback."}},
						Role:  "model",
					},
				},
				nil
			}
		}
	}
	return nil, nil
}

func runBeforeModelExample() {
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}

	llmCfg := llmagent.Config{
		Name:        "AgentWithBeforeModelCallback",
		Model:       geminiModel,
		BeforeModel: []llmagent.BeforeModelCallback{onBeforeModel},
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	const appName = "BeforeModelApp"
	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
	if err != nil {
		log.Fatalf("FATAL: Failed to create runner: %v", err)
	}

	log.Println("--- SCENARIO 1: Should proceed to LLM ---")
	runScenario(ctx, r, sessionService, appName, "session_normal", nil, "This is a safe prompt.")

	log.Println("\n--- SCENARIO 2: Should be blocked by callback ---")
	runScenario(ctx, r, sessionService, appName, "session_blocked", nil, "This prompt should be BLOCKED.")
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
	if censor, _ := ctx.State().Get("censor_response"); censor == true {
		log.Println("[Callback] 'censor_response' is true. Censoring response.")
		originalText := resp.Content.Parts[0].Text
		censoredText := strings.ReplaceAll(originalText, "blue", "[CENSORED]")
		resp.Content.Parts[0].Text = censoredText
		return resp, nil
	}
	return resp, nil
}

func runAfterModelExample() {
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}

	llmCfg := llmagent.Config{
		Name:       "AgentWithAfterModelCallback",
		Model:      geminiModel,
		AfterModel: []llmagent.AfterModelCallback{onAfterModel},
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	const appName = "AfterModelApp"
	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
	if err != nil {
		log.Fatalf("FATAL: Failed to create runner: %v", err)
	}

	log.Println("--- SCENARIO 1: Response should be censored ---")
	runScenario(ctx, r, sessionService, appName, "session_censor", map[string]any{"censor_response": true}, "Why is the sky blue?")

	log.Println("\n--- SCENARIO 2: Response should be normal ---")
	runScenario(ctx, r, sessionService, appName, "session_normal", map[string]any{"censor_response": false}, "Why is the sky blue?")
}
// --8<-- [end:after_model_example]

func main() {
	log.Println("--- Running BeforeAgent Example ---")
	runBeforeAgentExample()

	log.Println("\n\n--- Running AfterAgent Example ---")
	runAfterAgentExample()

	log.Println("\n\n--- Running BeforeModel Example ---")
	runBeforeModelExample()

	log.Println("\n\n--- Running AfterModel Example ---")
	runAfterModelExample()
}

// Generic helper to run a single scenario.
func runScenario(ctx context.Context, r *runner.Runner, sessionService session.Service, appName, sessionID string, initialState map[string]any, prompt string) {
	log.Printf("Running scenario for session: %s, initial state: %v", sessionID, initialState)
	sessionResp, err := sessionService.Create(ctx, &session.CreateRequest{AppName: appName, UserID: "test_user", SessionID: sessionID, State: initialState})
	if err != nil {
		log.Fatalf("FATAL: Failed to create session: %v", err)
	}

	input := genai.NewContentFromText(prompt, genai.RoleUser)
	events := r.Run(ctx, sessionResp.Session.UserID(), sessionResp.Session.ID(), input, &agent.RunConfig{})
	for event, err := range events {
		if err != nil {
			log.Printf("ERROR during agent execution: %v", err)
			return
		}
		
		// Print only the final output from the agent.
		if event.LLMResponse != nil && event.LLMResponse.Content != nil && len(event.LLMResponse.Content.Parts) > 0 {
			fmt.Printf("Final Output for %s: [%s] %s\n", sessionID, event.Author, event.LLMResponse.Content.Parts[0].Text)
		} else {
			log.Printf("Final response for %s received, but it has no content to display.", sessionID)
		}
	}
}
