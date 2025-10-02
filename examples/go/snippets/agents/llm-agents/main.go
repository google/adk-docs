package main

import (
	"context"
	"fmt"
	"log"
	"strings"

	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/llm/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/sessionservice"
	"google.golang.org/adk/tool"
	"google.golang.org/genai"
)

// getCapitalCityArgs defines the schema for the arguments passed to the getCapitalCity tool.
type getCapitalCityArgs struct {
	Country string `json:"country" adk:"description=The country to get the capital for."`
}

// getCapitalCity is a tool that retrieves the capital city for a given country.
func getCapitalCity(ctx context.Context, args getCapitalCityArgs) map[string]any {
	capitals := map[string]string{
		"france": "Paris",
		"japan":  "Tokyo",
		"canada": "Ottawa",
	}
	capital, ok := capitals[strings.ToLower(args.Country)]
	if !ok {
		return map[string]any{"result": fmt.Sprintf("Sorry, I don't know the capital of %s.", args.Country)}
	}
	return map[string]any{"result": capital}
}

func main() {
	ctx := context.Background()

	capitalTool, err := tool.NewFunctionTool(
		tool.FunctionToolConfig{
			Name:        "getCapitalCity",
			Description: "The country to get capital for.",
		},
		getCapitalCity,
	)
	if err != nil {
		log.Fatalf("Failed to create function tool: %v", err)
	}

	model, err := gemini.NewModel(ctx, "gemini-2.0-flash", &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	capitalAgent, err := llmagent.New(llmagent.Config{
		Name:        "capital_agent",
		Model:       model,
		Description: "Answers user questions about the capital city of a given country.",
		Instruction: `You are an agent that provides the capital city of a country.
When a user asks for the capital of a country:
1. Identify the country name from the user's query.
2. Use the 'get_capital_city' tool to find the capital.
3. Respond clearly to the user, stating the capital city.
Example Query: "What's the capital of {country}?"
Example Response: "The capital of France is Paris."`,
		Tools: []tool.Tool{capitalTool},
	})
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	sessionService := sessionservice.Mem()
	r, err := runner.New(&runner.Config{
		AppName:        "capital-agent-example",
		Agent:          capitalAgent,
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatalf("Failed to create runner: %v", err)
	}

	session, err := sessionService.Create(ctx, &sessionservice.CreateRequest{
		AppName: "capital-agent-example",
		UserID:  "user123",
	})
	if err != nil {
		log.Fatalf("Failed to create session: %v", err)
	}

	userMsg := &genai.Content{
		Parts: []*genai.Part{{Text: "What is the capital of France?"}},
		Role:  string(genai.RoleUser),
	}

	fmt.Println("Running Capital Agent...")
	for event, err := range r.Run(ctx, "user123", session.Session.ID().SessionID, userMsg, &runner.RunConfig{
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
	fmt.Println()
}
