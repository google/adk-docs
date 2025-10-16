package main

import (
	"context"
	"fmt"
	"iter"
	"log"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/genai"
)

// --- Conceptual Snippets for adk-docs/docs/context/index.md ---
const (
	modelName = "gemini-2.5-flash"
	appName   = "context_doc_app"
	userID    = "test_user_123"
)

// Generic helper to run a single scenario.
func runScenario(ctx context.Context, r *runner.Runner, sessionService session.Service, appName, sessionID string, initialState map[string]any, prompt string) {
	log.Printf("Running scenario for session: %s, initial state: %v", sessionID, initialState)
	sessionResp, err := sessionService.Create(ctx, &session.CreateRequest{AppName: appName, UserID: userID, SessionID: sessionID, State: initialState})
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
	baseAgent, err := agent.New(agent.Config{
		Name:        "MyAgent",
		Description: "An example agent.",
		Run:         a.Run, // Pass the Run method of our struct.
	})
	if err != nil {
		return nil, err
	}

	return baseAgent, nil
}


func runMyAgent() {
	ctx := context.Background()

	testAgent, err := NewMyAgent()
	if err != nil {
		log.Fatalf("FATAL: Failed to create agent: %v", err)
	}

	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
	if err != nil {
		log.Fatalf("FATAL: Failed to create runner: %v", err)
	}

	runScenario(ctx, r, sessionService, appName, "session", nil, "Hello, world!")
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

func runBeforeAgentCallbackCheck() {
	ctx := context.Background()
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("FATAL: Failed to create model: %v", err)
	}

	// 3. Register the callback in the agent configuration.
	llmCfg := llmagent.Config{
		Name:        "agent",
		BeforeModel: []llmagent.BeforeModelCallback{myBeforeModelCb},
		Model:       geminiModel,
		Instruction: "You are an assistant.",
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

	runScenario(ctx, r, sessionService, appName, "session", nil, "Hello, world!")
}

// --8<-- [end:callback_context_callback]

// --8<-- [start:tool_context_tool]
// Pseudocode: Tool function receiving ToolContext
type searchExternalAPIArgs struct {
	Query string
}

type searchExternalAPIResults struct {
	Result string
	Status string
}

func searchExternalAPI(tc tool.Context, input searchExternalAPIArgs) searchExternalAPIResults {
	apiKey, err := tc.State().Get("api_key")
	if err != nil || apiKey == "" {
		// In a real scenario, you would define and request credentials here.
		// This is a conceptual placeholder.
		return searchExternalAPIResults{Status: "Auth Required"}
	}

	// Use the API key...
	fmt.Printf("Tool executing for query '%s' using API key. Invocation: %s\n", input.Query, tc.InvocationID())

	// Optionally search memory or list artifacts
	// relevantDocs, _ := tc.SearchMemory(tc, "info related to %s", input.Query))
	// availableFiles, _ := tc.Artifacts().List()

	return searchExternalAPIResults{Result: fmt.Sprintf("Data for %s fetched.", input.Query)}
}

// --8<-- [end:tool_context_tool]

func runSearchExternalAPIExample() {
	myTool, err := tool.NewFunctionTool(
		tool.FunctionToolConfig{
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
func myTool(tc tool.Context, input toolArgs) toolResults {
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
	return toolResults{}
}

// --8<-- [end:accessing_state_tool]

func runMyToolExample() {
	myToolTool, err := tool.NewFunctionTool(
		tool.FunctionToolConfig{
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
func myCallback(ctx agent.CallbackContext, event *session.Event, err error) (*genai.Content, error) {
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
		Name:         "callbackAgent",
		AfterAgent:   []agent.AfterAgentCallback{myCallback},
		Model:        geminiModel,
		Instruction:  "You are an assistant that does nothing.",
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

	// Scenario 1: Run without the state key.
	log.Println("Scenario 1: State key is NOT present.")
	runScenario(ctx, r, sessionService, appName, "callback_session_1", nil, "Trigger callback")

	// Scenario 2: Run with the state key.
	log.Println("Scenario 2: State key IS present.")
	initialState := map[string]any{"temp:last_api_result": "Success from previous step"}
	runScenario(ctx, r, sessionService, appName, "callback_session_2", initialState, "Trigger callback again")
}

// --8<-- [start:accessing_ids]
// Pseudocode: In any context (ToolContext shown)
type logToolUsageArgs struct{}
type logToolUsageResult struct {
	Status string
}

func logToolUsage(tc tool.Context, args logToolUsageArgs) logToolUsageResult {
	agentName := tc.AgentName()
	invID := tc.InvocationID()
	funcCallID := tc.FunctionCallID()

	fmt.Printf("Log: Invocation=%s, Agent=%s, FunctionCallID=%s - Tool Executed.\n", invID, agentName, funcCallID)
	return logToolUsageResult{Status: "Logged successfully"}
}

// --8<-- [end:accessing_ids]

func runAccessIdsExample() {
	log.Println("\n--- Running Accessing IDs Example ---")
	ctx := context.Background()

	// 1. Create the tool.
	loggingTool, err := tool.NewFunctionTool(
		tool.FunctionToolConfig{
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

	// 3. Set up runner and session.
	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
	if err != nil {
		log.Fatalf("FATAL: Failed to create runner: %v", err)
	}

	// 4. Run a scenario that will trigger the tool.
	runScenario(ctx, r, sessionService, appName, "ids_session", nil, "Please log the current usage.")
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
		Name:        "agent",
		BeforeAgent: []agent.BeforeAgentCallback{checkInitialIntent},
		Model:       geminiModel,
		Instruction: "You are an assistant.",
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

	runScenario(ctx, r, sessionService, appName, "session", nil, "Hello, world!")
}


// --8<-- [start:passing_data_tool1]
// Pseudocode: Tool 1 - Fetches user ID
type getUserProfileResult struct {
	ProfileStatus string `json:"profile_status"`
}

func getUserProfile(tc tool.Context) (*getUserProfileResult, error) {
	userID := "user-12345" // Simulate fetching ID
	// Save the ID to state for the next tool
	if err := tc.State().Set("temp:current_user_id", userID); err != nil {
		return nil, err
	}
	return &getUserProfileResult{ProfileStatus: "ID generated"}, nil
}

// --8<-- [end:passing_data_tool1]

// --8<-- [start:passing_data_tool2]
// Pseudocode: Tool 2 - Uses user ID from state
type getUserOrdersResult struct {
	Orders []string `json:"orders,omitempty"`
	Error  string   `json:"error,omitempty"`
}

func getUserOrders(tc tool.Context) (*getUserOrdersResult, error) {
	userID, err := tc.State().Get("temp:current_user_id")
	if err != nil {
		return &getUserOrdersResult{Error: "User ID not found in state"}, nil
	}

	fmt.Printf("Fetching orders for user ID: %v\n", userID)
	// ... logic to fetch orders using user_id ...
	return &getUserOrdersResult{Orders: []string{"order123", "order456"}}, nil
}

// --8<-- [end:passing_data_tool2]

// --8<-- [start:updating_preferences]
// Pseudocode: Tool or Callback identifies a preference
type setUserPreferenceArgs struct {
	Preference string `json:"preference"`
	Value      string `json:"value"`
}

func setUserPreference(tc tool.Context, args setUserPreferenceArgs) (map[string]string, error) {
	// Use 'user:' prefix for user-level state (if using a persistent SessionService)
	stateKey := fmt.Sprintf("user:%s", args.Preference)
	if err := tc.State().Set(stateKey, args.Value); err != nil {
		return nil, err
	}
	fmt.Printf("Set user preference '%s' to '%s'\n", args.Preference, args.Value)
	return map[string]string{"status": "Preference updated"}, nil
}

// --8<-- [end:updating_preferences]

// --8<-- [start:artifacts_save_ref]
// Pseudocode: In a callback or initial tool
func saveDocumentReference(ctx agent.CallbackContext, filePath string) error {
	// Assume filePath is something like "gs://my-bucket/docs/report.pdf"
	// Create a Part containing the path/URI text
	artifactPart := genai.NewPartFromText(filePath)
	err := ctx.Artifacts().Save("document_to_summarize.txt", *artifactPart)
	if err != nil {
		fmt.Printf("Error saving artifact: %v\n", err)
		return err
	}
	fmt.Printf("Saved document reference '%s' as artifact\n", filePath)
	// Store the filename in state if needed by other tools
	return ctx.State().Set("temp:doc_artifact_name", "document_to_summarize.txt")
}

// --8<-- [end:artifacts_save_ref]

// --8<-- [start:artifacts_summarize]
// Pseudocode: In the Summarizer tool function
func summarizeDocumentTool(tc tool.Context) (map[string]string, error) {
	artifactName, err := tc.State().Get("temp:doc_artifact_name")
	if err != nil {
		return map[string]string{"error": "Document artifact name not found in state."}, nil
	}

	// 1. Load the artifact part containing the path/URI
	artifactPart, err := tc.Artifacts().Load(artifactName.(string))
	if err != nil {
		return nil, err
	}

	if artifactPart.Text == "" {
		return map[string]string{"error": "Could not load artifact or artifact has no text path."}, nil
	}
	filePath := artifactPart.Text
	fmt.Printf("Loaded document reference: %s\n", filePath)

	// 2. Read the actual document content (outside ADK context)
	// In a real implementation, you would use a GCS client or local file reader.
	documentContent := "This is the fake content of the document at " + filePath
	_ = documentContent // Avoid unused variable error.

	// 3. Summarize the content
	summary := "Summary of content from " + filePath // Placeholder

	return map[string]string{"summary": summary}, nil
}

// --8<-- [end:artifacts_summarize]

// --8<-- [start:artifacts_list]
// Pseudocode: In a tool function
func checkAvailableDocs(tc tool.Context) (map[string][]string, error) {
	artifactKeys, err := tc.Artifacts().List()
	if err != nil {
		return nil, err
	}
	fmt.Printf("Available artifacts: %v\n", artifactKeys)
	return map[string][]string{"available_docs": artifactKeys}, nil
}

// --8<-- [end:artifacts_list]

// This main function is for compilation purposes and does not run the snippets.
func main() {
	runInitialIntentCheck()
	runMyAgent()
	runBeforeAgentCallbackCheck()
	runSearchExternalAPIExample()
	runMyToolExample()
	runMyCallbackExample()
	runAccessIdsExample()
}
