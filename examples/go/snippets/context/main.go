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
	"bufio"
	"context"
	"fmt"
	"iter"
	"log"
	"os"
	"strings"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/artifact"
	"google.golang.org/adk/model"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"
	"google.golang.org/genai"
)

// --- Conceptual Snippets for adk-docs/docs/context/index.md ---
const (
	modelName = "gemini-2.5-flash"
	appName   = "context_doc_app"
	userID    = "test_user_123"
)

// Generic helper to run a single scenario.
func runScenario(ctx context.Context, agentToRun agent.Agent, sessionID string, initialState map[string]any, prompt string) {
	log.Printf("Running scenario for session: %s, initial state: %v", sessionID, initialState)

	sessionService := session.InMemoryService()
	artifactService := artifact.InMemoryService()
	rcfg := runner.Config{
		AppName:         appName,
		Agent:           agentToRun,
		SessionService:  sessionService,
		ArtifactService: artifactService,
	}

	r, err := runner.New(rcfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create runner: %v", err)
	}

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

func conceptualRunnerExample(ctx context.Context, myAgent agent.Agent) {
	// --8<-- [start:conceptual_runner_example]
	sessionService := session.InMemoryService()

	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          myAgent,
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatalf("Failed to create runner: %v", err)
	}

	s, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  userID,
	})
	if err != nil {
		log.Fatalf("FATAL: Failed to create session: %v", err)
	}

	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("\nYou > ")
		if !scanner.Scan() {
			break
		}
		userInput := scanner.Text()
		if strings.EqualFold(userInput, "quit") {
			break
		}
		userMsg := genai.NewContentFromText(userInput, genai.RoleUser)
		events := r.Run(ctx, s.Session.UserID(), s.Session.ID(), userMsg, agent.RunConfig{
			StreamingMode: agent.StreamingModeNone,
		})
		fmt.Print("\nAgent > ")
		for event, err := range events {
			if err != nil {
				log.Printf("ERROR during agent execution: %v", err)
				break
			}
			fmt.Print(event.Content.Parts[0].Text)
		}
	}
	// --8<-- [end:conceptual_runner_example]
}

func runConceptualExample() {
	ctx := context.Background()
	// 2. Create an agent with the tool.
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}
	llmCfg := llmagent.Config{
		Name:        "agent",
		Model:       geminiModel,
		Instruction: "You are an assistant",
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	conceptualRunnerExample(ctx, testAgent)
}

// --8<-- [start:invocation_context_agent]
// Pseudocode: Agent implementation receiving InvocationContext
type MyAgent struct {
}

func (a *MyAgent) Run(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
	return func(yield func(*session.Event, error) bool) {
		// Direct access example
		agentName := ctx.Agent().Name()
		sessionID := ctx.Session().ID()
		fmt.Printf("Agent %s running in session %s for invocation %s\n", agentName, sessionID, ctx.InvocationID())
		// ... agent logic using ctx ...
		yield(&session.Event{Author: agentName}, nil)
	}
}

// --8<-- [end:invocation_context_agent]

// NewMyAgent creates a new MyAgent.
func NewMyAgent() (agent.Agent, error) {
	a := &MyAgent{}
	// Use agent.New to construct the base agent functionality.
	return agent.New(agent.Config{
		Name:        "MyAgent",
		Description: "An example agent.",
		Run:         a.Run, // Pass the Run method of our struct.
	})
}

func runMyAgent() {
	ctx := context.Background()

	testAgent, err := NewMyAgent()
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	runScenario(ctx, testAgent, "session", nil, "Hello, world!")
}

// --8<-- [start:readonly_context_instruction]
// Pseudocode: Instruction provider receiving ReadonlyContext
func myInstructionProvider(ctx agent.ReadonlyContext) (string, error) {
	// Read-only access example
	userTier, err := ctx.ReadonlyState().Get("user_tier")
	if err != nil {
		userTier = "standard" // Default value
	}
	// ctx.ReadonlyState() has no Set method since State() is read-only.
	return fmt.Sprintf("Process the request for a %v user.", userTier), nil
}

// --8<-- [end:readonly_context_instruction]

// --8<-- [start:callback_context_callback]
// Pseudocode: Callback receiving CallbackContext
func myBeforeModelCb(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
	// Read/Write state example
	callCount, err := ctx.State().Get("model_calls")
	if err != nil {
		callCount = 0 // Default value
	}
	newCount := callCount.(int) + 1
	if err := ctx.State().Set("model_calls", newCount); err != nil {
		return nil, err
	}

	// Optionally load an artifact
	// configPart, err := ctx.Artifacts().Load("model_config.json")
	fmt.Printf("Preparing model call #%d for invocation %s\n", newCount, ctx.InvocationID())
	return nil, nil // Allow model call to proceed
}

// --8<-- [end:callback_context_callback]

func runBeforeAgentCallbackCheck() {
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}

	// 3. Register the callback in the agent configuration.
	llmCfg := llmagent.Config{
		Name:                 "agent",
		BeforeModelCallbacks: []llmagent.BeforeModelCallback{myBeforeModelCb},
		Model:                geminiModel,
		Instruction:          "You are an assistant.",
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	runScenario(ctx, testAgent, "session", nil, "Hello, world!")
}

// --8<-- [start:tool_context_tool]
// Pseudocode: Tool function receiving ToolContext
type searchExternalAPIArgs struct {
	Query string `json:"query" jsonschema:"The query to search for."`
}

func searchExternalAPI(tc tool.Context, input searchExternalAPIArgs) (string, error) {
	apiKey, err := tc.State().Get("api_key")
	if err != nil || apiKey == "" {
		// In a real scenario, you would define and request credentials here.
		// This is a conceptual placeholder.
		return "", fmt.Errorf("auth required")
	}

	// Use the API key...
	fmt.Printf("Tool executing for query '%s' using API key. Invocation: %s\n", input.Query, tc.InvocationID())

	// Optionally search memory or list artifacts
	// relevantDocs, _ := tc.SearchMemory(tc, "info related to %s", input.Query))
	// availableFiles, _ := tc.Artifacts().List()

	return fmt.Sprintf("Data for %s fetched.", input.Query), nil
}

// --8<-- [end:tool_context_tool]

func runSearchExternalAPIExample() {
	myTool, err := functiontool.New(
		functiontool.Config{
			Name:        "search_external_api",
			Description: "Searches an external API using a query string.",
		},
		searchExternalAPI)

	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Tool created: %s\n", myTool.Name())
}

// --8<-- [start:accessing_state_tool]
// Pseudocode: In a Tool function
type toolArgs struct {
	// Define tool-specific arguments here
}

type toolResults struct {
	// Define tool-specific results here
}

// Example tool function demonstrating state access
func myTool(tc tool.Context, input toolArgs) (toolResults, error) {
	userPref, err := tc.State().Get("user_display_preference")
	if err != nil {
		userPref = "default_mode"
	}
	apiEndpoint, _ := tc.State().Get("app:api_endpoint") // Read app-level state

	if userPref == "dark_mode" {
		// ... apply dark mode logic ...
	}
	fmt.Printf("Using API endpoint: %v\n", apiEndpoint)
	// ... rest of tool logic ...
	return toolResults{}, nil
}

// --8<-- [end:accessing_state_tool]

func runMyToolExample() {
	myToolTool, err := functiontool.New(
		functiontool.Config{
			Name:        "my_tool",
			Description: "A tool for doing something.",
		},
		myTool)

	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("Tool created: %s\n", myToolTool.Name())
}

// --8<-- [start:accessing_state_callback]
// Pseudocode: In a Callback function
func myCallback(ctx agent.CallbackContext) (*genai.Content, error) {
	lastToolResult, err := ctx.State().Get("temp:last_api_result") // Read temporary state
	if err == nil {
		fmt.Printf("Found temporary result from last tool: %v\n", lastToolResult)
	} else {
		fmt.Println("No temporary result found.")
	}
	// ... callback logic ...
	return nil, nil
}

// --8<-- [end:accessing_state_callback]

func runMyCallbackExample() {
	log.Println("\n--- Running Accessing State (Callback) Example ---")
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}

	// Register myCallback as an AfterAgentCallback.
	llmCfg := llmagent.Config{
		Name:                "callbackAgent",
		AfterAgentCallbacks: []agent.AfterAgentCallback{myCallback},
		Model:               geminiModel,
		Instruction:         "You are an assistant that does nothing.",
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	// Scenario 1: Run without the state key.
	log.Println("Scenario 1: State key is NOT present.")
	runScenario(ctx, testAgent, "callback_session_1", nil, "Trigger callback")

	// Scenario 2: Run with the state key.
	log.Println("Scenario 2: State key IS present.")
	initialState := map[string]any{"temp:last_api_result": "Success from previous step"}
	runScenario(ctx, testAgent, "callback_session_2", initialState, "Trigger callback again")
}

// --8<-- [start:accessing_ids]
// Pseudocode: In any context (ToolContext shown)
type logToolUsageArgs struct{}
type logToolUsageResult struct {
	Status string `json:"status"`
}

func logToolUsage(tc tool.Context, args logToolUsageArgs) (logToolUsageResult, error) {
	agentName := tc.AgentName()
	invID := tc.InvocationID()
	funcCallID := tc.FunctionCallID()

	fmt.Printf("Log: Invocation=%s, Agent=%s, FunctionCallID=%s - Tool Executed.\n", invID, agentName, funcCallID)
	return logToolUsageResult{Status: "Logged successfully"}, nil
}

// --8<-- [end:accessing_ids]

func runAccessIdsExample() {
	log.Println("\n--- Running Accessing IDs Example ---")
	ctx := context.Background()

	// 1. Create the tool.
	loggingTool, err := functiontool.New(
		functiontool.Config{
			Name:        "log_tool_usage",
			Description: "Logs the invocation and agent details.",
		},
		logToolUsage,
	)
	if err != nil {
		log.Fatalf("FATAL: Failed to create tool: %v", err)
	}

	// 2. Create an agent with the tool.
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}
	llmCfg := llmagent.Config{
		Name:        "idAgent",
		Model:       geminiModel,
		Instruction: "You are an assistant that uses the logging tool.",
		Tools:       []tool.Tool{loggingTool},
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	// 3. Run a scenario that will trigger the tool.
	runScenario(ctx, testAgent, "ids_session", nil, "Please log the current usage.")
}

// --8<-- [start:accessing_user_content_agent]
// Pseudocode: In a Callback
func checkInitialIntent(ctx agent.CallbackContext) (*genai.Content, error) {
	initialText := "N/A"
	userContent := ctx.UserContent()
	if userContent != nil && len(userContent.Parts) > 0 {
		// The API for Part content has changed from a type assertion to direct field access.
		if text := userContent.Parts[0].Text; text != "" {
			initialText = text
		} else {
			initialText = "Non-text input"
		}
	}
	fmt.Printf("This invocation started with user input: '%s'\n", initialText)
	return nil, nil // No modification to the content
}

// --8<-- [end:accessing_user_content_agent]

func runInitialIntentCheck() {
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}

	// 3. Register the callback in the agent configuration.
	llmCfg := llmagent.Config{
		Name:                 "agent",
		BeforeAgentCallbacks: []agent.BeforeAgentCallback{checkInitialIntent},
		Model:                geminiModel,
		Instruction:          "You are an assistant.",
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	runScenario(ctx, testAgent, "session", nil, "Hello, world!")
}

// --8<-- [start:accessing_initial_user_input]
// Pseudocode: In a Callback
func logInitialUserInput(ctx agent.CallbackContext) (*genai.Content, error) {
	userContent := ctx.UserContent()
	if userContent != nil && len(userContent.Parts) > 0 {
		if text := userContent.Parts[0].Text; text != "" {
			fmt.Printf("User's initial input for this turn: '%s'\n", text)
		}
	}
	return nil, nil // No modification
}

// --8<-- [end:accessing_initial_user_input]

func runAccessingInitialUserInputExample() {
	log.Println("\n--- Running Accessing Initial User Input Example ---")
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}

	llmCfg := llmagent.Config{
		Name:                 "userInputLoggerAgent",
		BeforeAgentCallbacks: []agent.BeforeAgentCallback{logInitialUserInput},
		Model:                geminiModel,
		Instruction:          "You are an assistant.",
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	runScenario(ctx, testAgent, "user_input_session", nil, "What is the weather in London?")
}

// --8<-- [start:passing_data_tool1]
// Pseudocode: Tool 1 - Fetches user ID
type GetUserProfileArgs struct {
}

func getUserProfile(tc tool.Context, input GetUserProfileArgs) (string, error) {
	// A random user ID for demonstration purposes
	userID := "random_user_456"

	// Save the ID to state for the next tool
	if err := tc.State().Set("temp:current_user_id", userID); err != nil {
		return "", fmt.Errorf("failed to set user ID in state: %w", err)
	}
	return "ID generated", nil
}

// --8<-- [end:passing_data_tool1]

// --8<-- [start:passing_data_tool2]
// Pseudocode: Tool 2 - Uses user ID from state
type GetUserOrdersArgs struct {
}

type getUserOrdersResult struct {
	Orders []string `json:"orders"`
}

func getUserOrders(tc tool.Context, input GetUserOrdersArgs) (*getUserOrdersResult, error) {
	userID, err := tc.State().Get("temp:current_user_id")
	if err != nil {
		return &getUserOrdersResult{}, fmt.Errorf("user ID not found in state")
	}

	fmt.Printf("Fetching orders for user ID: %v\n", userID)
	// ... logic to fetch orders using user_id ...
	return &getUserOrdersResult{Orders: []string{"order123", "order456"}}, nil
}

// --8<-- [end:passing_data_tool2]

func runPassingDataExample() {
	log.Println("\n--- Running Passing Data Between Tools Example ---")
	ctx := context.Background()

	// 1. Create the tools.
	getUserProfileTool, err := functiontool.New(
		functiontool.Config{
			Name:        "get_user_profile",
			Description: "Gets the profile for a user.",
		},
		getUserProfile,
	)
	if err != nil {
		log.Fatalf("FATAL: Failed to create getUserProfile tool: %v", err)
	}
	getUserOrdersTool, err := functiontool.New(
		functiontool.Config{
			Name:        "get_user_orders",
			Description: "Gets the orders for a user.",
		},
		getUserOrders,
	)
	if err != nil {
		log.Fatalf("FATAL: Failed to create getUserOrders tool: %v", err)
	}

	// 2. Create an agent with the tools.
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}
	llmCfg := llmagent.Config{
		Name:        "dataPassingAgent",
		Model:       geminiModel,
		Instruction: "You are an assistant that first gets the user profile, then gets their orders.",
		Tools:       []tool.Tool{getUserProfileTool, getUserOrdersTool},
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	// 3. Set up runner and session.
	initialState := map[string]any{
		"temp:current_user_id": userID,
	}

	// 4. Run a scenario that will trigger the tools.
	runScenario(ctx, testAgent, "passing_data_session", initialState, "Get my orders.")
}

// --8<-- [start:updating_preferences]
// Pseudocode: Tool or Callback identifies a preference
type setUserPreferenceArgs struct {
	Preference string `json:"preference" jsonschema:"The name of the preference to set."`
	Value      string `json:"value" jsonschema:"The value to set for the preference."`
}

type setUserPreferenceResult struct {
	Status string `json:"status"`
}

func setUserPreference(tc tool.Context, args setUserPreferenceArgs) (setUserPreferenceResult, error) {
	// Use 'user:' prefix for user-level state (if using a persistent SessionService)
	stateKey := fmt.Sprintf("user:%s", args.Preference)
	if err := tc.State().Set(stateKey, args.Value); err != nil {
		return setUserPreferenceResult{}, fmt.Errorf("failed to set preference in state: %w", err)
	}
	fmt.Printf("Set user preference '%s' to '%s'\n", args.Preference, args.Value)
	return setUserPreferenceResult{Status: "Preference updated"}, nil
}

// --8<-- [end:updating_preferences]

func runUpdatingPreferencesExample() {
	log.Println("\n--- Running Updating Preferences Example ---")
	ctx := context.Background()

	// 1. Create the tool.
	setPrefTool, err := functiontool.New(
		functiontool.Config{
			Name:        "set_user_preference",
			Description: "Sets a user's preference in the system.",
		},
		setUserPreference,
	)
	if err != nil {
		log.Fatalf("FATAL: Failed to create setPrefTool: %v", err)
	}

	// 2. Create an agent with the tool.
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}
	llmCfg := llmagent.Config{
		Name:        "preferenceAgent",
		Model:       geminiModel,
		Instruction: "You are an assistant that helps users set their preferences.",
		Tools:       []tool.Tool{setPrefTool},
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	// 3. Run a scenario that will trigger the tool.
	runScenario(ctx, testAgent, "preferences_session", nil, "Please set my theme preference to dark_mode.")
}

// --8<-- [start:artifacts_summarize]
// Pseudocode: In the Summarizer tool function
type summarizeDocumentArgs struct{}

type summarizeDocumentResult struct {
	Summary string `json:"summary"`
}

func summarizeDocumentTool(tc tool.Context, input summarizeDocumentArgs) (summarizeDocumentResult, error) {
	artifactName, err := tc.State().Get("temp:doc_artifact_name")
	if err != nil {
		return summarizeDocumentResult{}, fmt.Errorf("No document artifact name found in state")
	}

	// 1. Load the artifact part containing the path/URI
	artifactPart, err := tc.Artifacts().Load(tc, artifactName.(string))
	if err != nil {
		return summarizeDocumentResult{}, err
	}

	if artifactPart.Part.Text == "" {
		return summarizeDocumentResult{}, fmt.Errorf("Could not load artifact or artifact has no text path.")
	}
	filePath := artifactPart.Part.Text
	fmt.Printf("Loaded document reference: %s\n", filePath)

	// 2. Read the actual document content (outside ADK context)
	// In a real implementation, you would use a GCS client or local file reader.
	documentContent := "This is the fake content of the document at " + filePath
	_ = documentContent // Avoid unused variable error.

	// 3. Summarize the content
	summary := "Summary of content from " + filePath // Placeholder

	return summarizeDocumentResult{Summary: summary}, nil
}

// --8<-- [end:artifacts_summarize]

// --8<-- [start:artifacts_list]
// Pseudocode: In a tool function
type checkAvailableDocsArgs struct{}

type checkAvailableDocsResult struct {
	AvailableDocs []string `json:"available_docs"`
}

func checkAvailableDocs(tc tool.Context, args checkAvailableDocsArgs) (checkAvailableDocsResult, error) {
	artifactKeys, err := tc.Artifacts().List(tc)
	if err != nil {
		return checkAvailableDocsResult{}, err
	}
	fmt.Printf("Available artifacts: %v\n", artifactKeys)
	return checkAvailableDocsResult{AvailableDocs: artifactKeys.FileNames}, nil
}

// --8<-- [end:artifacts_list]

// --8<-- [start:artifacts_save_ref]
// Adapt the saveDocumentReference callback into a tool for this example.
type saveDocRefArgs struct {
	FilePath string `json:"file_path" jsonschema:"The path to the file to save."`
}

type saveDocRefResult struct {
	Status string `json:"status"`
}

func saveDocRef(tc tool.Context, args saveDocRefArgs) (saveDocRefResult, error) {
	artifactPart := genai.NewPartFromText(args.FilePath)
	_, err := tc.Artifacts().Save(tc, "document_to_summarize.txt", artifactPart)
	if err != nil {
		return saveDocRefResult{}, err
	}
	fmt.Printf("Saved document reference '%s' as artifact\n", args.FilePath)
	if err := tc.State().Set("temp:doc_artifact_name", "document_to_summarize.txt"); err != nil {
		return saveDocRefResult{}, fmt.Errorf("failed to set artifact name in state")
	}
	return saveDocRefResult{"Reference saved"}, nil
}

// --8<-- [end:artifacts_save_ref]

func runArtifactsExample() {
	log.Println("\n--- Running Artifacts Example ---")
	ctx := context.Background()

	// 1. Create the tools.
	saveRefTool, err := functiontool.New(
		functiontool.Config{
			Name:        "save_document_reference",
			Description: "Saves a reference to a document path as an artifact.",
		},
		saveDocRef,
	)
	if err != nil {
		log.Fatalf("FATAL: Failed to create saveRefTool: %v", err)
	}
	summarizeTool, err := functiontool.New(
		functiontool.Config{
			Name:        "summarize_document",
			Description: "Summarizes the document stored in artifacts.",
		},
		summarizeDocumentTool,
	)
	if err != nil {
		log.Fatalf("FATAL: Failed to create summarizeTool: %v", err)
	}

	// 2. Create an agent with the tools.
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}
	llmCfg := llmagent.Config{
		Name:        "artifactAgent",
		Model:       geminiModel,
		Instruction: "First save the document reference, then summarize it.",
		Tools:       []tool.Tool{saveRefTool, summarizeTool},
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	// 3. Run a scenario that will trigger the tools.
	runScenario(ctx, testAgent, "artifacts_session", nil, "Save the doc at 'gs://my-bucket/report.pdf' and then summarize it.")
}

func runCheckAvailableDocsExample() {
	log.Println("\n--- Running Check Available Docs Example ---")
	ctx := context.Background()

	// 1. Create the tool.
	checkDocsTool, err := functiontool.New(
		functiontool.Config{
			Name:        "check_available_docs",
			Description: "Checks for available documents in artifacts.",
		},
		checkAvailableDocs,
	)
	if err != nil {
		log.Fatalf("FATAL: Failed to create checkDocsTool: %v", err)
	}

	// 2. Create an agent with the tool.
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}
	llmCfg := llmagent.Config{
		Name:        "docCheckerAgent",
		Model:       geminiModel,
		Instruction: "You are an assistant that can check for available documents.",
		Tools:       []tool.Tool{checkDocsTool},
	}
	testAgent, err := llmagent.New(llmCfg)
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	// 3. Run a scenario that will trigger the tool.
	runScenario(ctx, testAgent, "check_docs_session", nil, "Are there any documents available?")
}

// This main function is for compilation purposes and does not run the snippets.
func main() {
	runInitialIntentCheck()
	runMyAgent()
	runBeforeAgentCallbackCheck()
	runSearchExternalAPIExample()
	runMyToolExample()
	runMyCallbackExample()
	runAccessIdsExample()
	runAccessingInitialUserInputExample()
	runPassingDataExample()
	runArtifactsExample()
	runUpdatingPreferencesExample()
	runCheckAvailableDocsExample()
}
