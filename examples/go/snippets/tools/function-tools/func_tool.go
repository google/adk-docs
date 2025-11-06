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
	"strings"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/agenttool"
	"google.golang.org/adk/tool/functiontool"

	"google.golang.org/genai"
)

// mockStockPrices provides a simple in-memory database of stock prices
// to simulate a real-world stock data API. This allows the example to
// demonstrate tool functionality without making external network calls.
var mockStockPrices = map[string]float64{
	"GOOG": 300.6,
	"AAPL": 123.4,
	"MSFT": 234.5,
}

// getStockPriceArgs defines the schema for the arguments passed to the getStockPrice tool.
// Using a struct is the recommended approach in the Go ADK as it provides strong
// typing and clear validation for the expected inputs.
type getStockPriceArgs struct {
	Symbol string `json:"symbol" jsonschema:"The stock ticker symbol, e.g., GOOG"`
}

// getStockPriceResults defines the output schema for the getStockPrice tool.
type getStockPriceResults struct {
	Symbol string  `json:"symbol"`
	Price  float64 `json:"price,omitempty"`
	Error  string  `json:"error,omitempty"`
}

// getStockPrice is a tool that retrieves the stock price for a given ticker symbol
// from the mockStockPrices map. It demonstrates how a function can be used as a
// tool by an agent. If the symbol is found, it returns a struct containing the
// symbol and its price. Otherwise, it returns a struct with an error message.
func getStockPrice(ctx tool.Context, input getStockPriceArgs) getStockPriceResults {
	symbolUpper := strings.ToUpper(input.Symbol)
	if price, ok := mockStockPrices[symbolUpper]; ok {
		fmt.Printf("Tool: Found price for %s: %f\n", input.Symbol, price)
		return getStockPriceResults{Symbol: input.Symbol, Price: price}
	}
	return getStockPriceResults{Symbol: input.Symbol, Error: "No data found for symbol"}
}

// createStockAgent initializes and configures an LlmAgent.
// This agent is equipped with the getStockPrice tool and is instructed
// on how to respond to user queries about stock prices. It uses the
// Gemini model to understand user intent and decide when to use its tools.
func createStockAgent(ctx context.Context) (agent.Agent, error) {
	stockPriceTool, err := functiontool.New(
		functiontool.Config{
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
		Name:        "stock_agent",
		Model:       model,
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
func callAgent(ctx context.Context, a agent.Agent, prompt string) {
	sessionService := session.InMemoryService()
	// Create a new session for the agent interactions.
	session, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  userID,
	})
	if err != nil {
		log.Fatalf("Failed to create the session service: %v", err)
	}
	config := runner.Config{
		AppName:        appName,
		Agent:          a,
		SessionService: sessionService,
	}

	// Create the runner to manage the agent execution.
	r, err := runner.New(config)

	if err != nil {
		log.Fatalf("Failed to create the runner: %v", err)
	}

	sessionID := session.Session.ID()

	userMsg := &genai.Content{
		Parts: []*genai.Part{
			genai.NewPartFromText(prompt),
		},
		Role: string(genai.RoleUser),
	}

	for event, err := range r.Run(ctx, userID, sessionID, userMsg, agent.RunConfig{
		StreamingMode: agent.StreamingModeNone,
	}) {
		if err != nil {
			fmt.Printf("\nAGENT_ERROR: %v\n", err)
		} else {
			for _, p := range event.Content.Parts {
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

// --8<-- [start:agent_tool_example]
// createSummarizerAgent creates an agent whose sole purpose is to summarize text.
func createSummarizerAgent(ctx context.Context) (agent.Agent, error) {
	model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
	if err != nil {
		return nil, err
	}
	return llmagent.New(llmagent.Config{
		Name:        "SummarizerAgent",
		Model:       model,
		Instruction: "You are an expert at summarizing text. Take the user's input and provide a concise summary.",
		Description: "An agent that summarizes text.",
	})
}

// createMainAgent creates the primary agent that will use the summarizer agent as a tool.
func createMainAgent(ctx context.Context, tools ...tool.Tool) (agent.Agent, error) {
	model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
	if err != nil {
		return nil, err
	}
	return llmagent.New(llmagent.Config{
		Name:  "MainAgent",
		Model: model,
		Instruction: "You are a helpful assistant. If you are asked to summarize a long text, use the 'summarize' tool. " +
			"After getting the summary, present it to the user by saying 'Here is a summary of the text:'.",
		Description: "The main agent that can delegate tasks.",
		Tools:       tools,
	})
}

func RunAgentAsToolSimulation() {
	ctx := context.Background()

	// 1. Create the Tool Agent (Summarizer)
	summarizerAgent, err := createSummarizerAgent(ctx)
	if err != nil {
		log.Fatalf("Failed to create summarizer agent: %v", err)
	}

	// 2. Wrap the Tool Agent in an AgentTool
	summarizeTool := agenttool.New(summarizerAgent, &agenttool.Config{
		SkipSummarization: true,
	})

	// 3. Create the Main Agent and provide it with the AgentTool
	mainAgent, err := createMainAgent(ctx, summarizeTool)
	if err != nil {
		log.Fatalf("Failed to create main agent: %v", err)
	}

	// 4. Run the main agent
	prompt := `
		Please summarize this text for me:
		Quantum computing represents a fundamentally different approach to computation,
		leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers
		that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively
		being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled,
		meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and
		interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such
		as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far
		faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages.
	`
	fmt.Printf("\nPrompt: %s\nResponse: ", prompt)
	callAgent(context.Background(), mainAgent, prompt)
	fmt.Println("\n---")
}

// --8<-- [end:agent_tool_example]

func main() {
	fmt.Println("Attempting to run the agent simulation...")
	RunAgentSimulation()
	fmt.Println("\nAttempting to run the agent-as-a-tool simulation...")
	RunAgentAsToolSimulation()
}
