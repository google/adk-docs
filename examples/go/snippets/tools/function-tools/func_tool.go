package main

import (
	"context"
	"fmt"
	"log"
	"strings"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/llm/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/sessionservice"
	"google.golang.org/adk/tool"

	"google.golang.org/genai"
)

// mockStockPrices provides a simple in-memory database of stock prices
// to simulate a real-world stock data API. This allows the example to
// demonstrate tool functionality without making external network calls.
var mockStockPrices = map[string]float64{
	"GOOG": 600.6,
	"AAPL": 123.4,
	"MSFT": 234.5,
}

// getStockPriceArgs defines the schema for the arguments passed to the getStockPrice tool.
// Using a struct is the recommended approach in the Go ADK as it provides strong
// typing and clear validation for the expected inputs.
type getStockPriceArgs struct {
	Symbol string
}

// getStockPrice is a tool that retrieves the stock price for a given ticker symbol
// from the mockStockPrices map. It demonstrates how a function can be used as a
// tool by an agent. If the symbol is found, it returns a map containing the
// symbol and its price. Otherwise, it returns an error message.
func getStockPrice(ctx context.Context, input getStockPriceArgs) map[string]any {
	symbolUpper := strings.ToUpper(input.Symbol)
	if price, ok := mockStockPrices[symbolUpper]; ok {
		fmt.Printf("Tool: Found price for %s: %f\n", input.Symbol, price)
		return map[string]any{"symbol": input.Symbol, "price": price}
	}
	return map[string]any{"symbol": input.Symbol, "error": "No data found for symbol"}
}

// createStockAgent initializes and configures an LlmAgent.
// This agent is equipped with the getStockPrice tool and is instructed
// on how to respond to user queries about stock prices. It uses the
// Gemini model to understand user intent and decide when to use its tools.
func createStockAgent(ctx context.Context) (agent.Agent, error) {
	stockPriceTool, err := tool.NewFunctionTool(
		tool.FunctionToolConfig{
			Name:        "get_stock_price",
			Description: "Retrieves the current stock price for a given symbol.",
		},
		getStockPrice)
	if err != nil {
		return nil, err
	}

	model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})

	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}


	return llmagent.New(llmagent.Config{
		Name: "stock_agent",
		Model: model,
		Instruction: "You are an agent who retrieves stock prices. If a ticker symbol is provided, fetch the current price. If only a company name is given, first perform a Google search to find the correct ticker symbol before retrieving the stock price. If the provided ticker symbol is invalid or data cannot be retrieved, inform the user that the stock price could not be found.",
		Description: "This agent specializes in retrieving real-time stock prices. Given a stock ticker symbol (e.g., AAPL, GOOG, MSFT) or the stock name, use the tools and reliable data sources to provide the most up-to-date price.",
		Tools: []tool.Tool{
			stockPriceTool,
		},
	})
}

// userID and appName are constants used to identify the user and application
// throughout the session. These values are important for logging, tracking,
// and managing state across different agent interactions.
const (
	userID  = "example_user_id"
	appName = "example_app"
)

// callAgent orchestrates the execution of the agent for a given prompt.
// It sets up the necessary services, creates a session, and uses a runner
// to manage the agent's lifecycle. It streams the agent's responses and
// prints them to the console, handling any potential errors during the run.
func callAgent(ctx context.Context, agent agent.Agent, prompt string) {

	sessionService := sessionservice.Mem()

	// Create a new session for the agent interactions.
	session, err := sessionService.Create(ctx, &sessionservice.CreateRequest{
		AppName: appName,
		UserID:  userID,
	})
	if err != nil {
		log.Fatalf("Failed to create the session service: %v", err)
	}

	config := &runner.Config{
		AppName:        appName,
		Agent:          agent,
		SessionService: sessionService,
	}

	// Create the runner to manage the agent execution.
	r, err := runner.New(config)

	if err != nil {
		log.Fatalf("Failed to create the runner: %v", err)
	}

	sessionID := session.Session.ID().SessionID

	userMsg := &genai.Content{
		Parts: []*genai.Part{
			genai.NewPartFromText(prompt),
		},
		Role: string(genai.RoleUser),
	}

	for event, err := range r.Run(ctx, userID, sessionID, userMsg, &runner.RunConfig{
		StreamingMode: runner.StreamingModeSSE,
	}) {
		if err != nil {
			fmt.Printf("\nAGENT_ERROR: %v\n", err)
		} else {
			for _, p := range event.LLMResponse.Content.Parts {
				fmt.Print(p.Text)
			}
		}
	}
}

// RunAgentSimulation serves as the entry point for this example.
// It creates the stock agent and then simulates a series of user interactions
// by sending different prompts to the agent. This function showcases how the
// agent responds to various queries, including both successful and unsuccessful
// attempts to retrieve stock prices.
func RunAgentSimulation() {
	// Create the stock agent
	agent, err := createStockAgent(context.Background())
	if err != nil {
		panic(err)
	}

	fmt.Println("Agent created:", agent.Name())

	prompts := []string{
		"stock price of GOOG",
		"What's the price of MSFT?",
		"Can you find the stock price for an unknown company XYZ?",
	}

	// Simulate running the agent with different prompts
	for _, prompt := range prompts {
		fmt.Printf("\nPrompt: %s\nResponse: ", prompt)
		callAgent(context.Background(), agent, prompt)
		fmt.Println("\n---")
	}
}
