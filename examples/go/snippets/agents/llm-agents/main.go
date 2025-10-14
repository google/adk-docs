// --8<-- [start:full_code]
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"strings"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"

	"google.golang.org/genai"
)

// --- Main Runnable Example ---

const (
	modelName = "gemini-2.0-flash"
	appName   = "agent_comparison_app"
	userID    = "test_user_456"
)

type getCapitalCityArgs struct {
	Country string `json:"country"`
}

// getCapitalCity retrieves the capital city of a given country.
func getCapitalCity(ctx tool.Context, args getCapitalCityArgs) map[string]any {
	fmt.Printf("\n-- Tool Call: getCapitalCity(country='%s') --\n", args.Country)
	capitals := map[string]string{
		"united states": "Washington, D.C.",
		"canada":        "Ottawa",
		"france":        "Paris",
		"japan":         "Tokyo",
	}
	capital, ok := capitals[strings.ToLower(args.Country)]
	if !ok {
		result := fmt.Sprintf("Sorry, I couldn't find the capital for %s.", args.Country)
		fmt.Printf("-- Tool Result: '%s' --\n", result)
		return map[string]any{"result": result}
	}
	fmt.Printf("-- Tool Result: '%s' --\n", capital)
	return map[string]any{"result": capital}
}

func main() {
	ctx := context.Background()

	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	capitalTool, err := tool.NewFunctionTool(
		tool.FunctionToolConfig{
			Name:        "get_capital_city",
			Description: "Retrieves the capital city for a given country.",
		},
		getCapitalCity,
	)
	if err != nil {
		log.Fatalf("Failed to create function tool: %v", err)
	}

	countryInputSchema := &genai.Schema{
		Type:        genai.TypeObject,
		Description: "Input for specifying a country.",
		Properties: map[string]*genai.Schema{
			"country": {
				Type:        genai.TypeString,
				Description: "The country to get information about.",
			},
		},
		Required: []string{"country"},
	}

	capitalAgentWithTool, err := llmagent.New(llmagent.Config{
		Name:        "capital_agent_tool",
		Model:       model,
		Description: "Retrieves the capital city using a specific tool.",
		Instruction: `You are a helpful agent that provides the capital city of a country using a tool.
The user will provide the country name in a JSON format like {"country": "country_name"}.
1. Extract the country name.
2. Use the 'get_capital_city' tool to find the capital.
3. Respond clearly to the user, stating the capital city found by the tool.`,
		Tools:       []tool.Tool{capitalTool},
		InputSchema: countryInputSchema,
		OutputKey:   "capital_tool_result",
	})
	if err != nil {
		log.Fatalf("Failed to create capital agent with tool: %v", err)
	}

	capitalInfoOutputSchema := &genai.Schema{
		Type:        genai.TypeObject,
		Description: "Schema for capital city information.",
		Properties: map[string]*genai.Schema{
			"capital": {
				Type:        genai.TypeString,
				Description: "The capital city of the country.",
			},
			"population_estimate": {
				Type:        genai.TypeString,
				Description: "An estimated population of the capital city.",
			},
		},
		Required: []string{"capital", "population_estimate"},
	}
	schemaJSON, _ := json.Marshal(capitalInfoOutputSchema)
	structuredInfoAgentSchema, err := llmagent.New(llmagent.Config{
		Name:        "structured_info_agent_schema",
		Model:       model,
		Description: "Provides capital and estimated population in a specific JSON format.",
		Instruction: fmt.Sprintf(`You are an agent that provides country information.
The user will provide the country name in a JSON format like {"country": "country_name"}.
Respond ONLY with a JSON object matching this exact schema:
%s
Use your knowledge to determine the capital and estimate the population. Do not use any tools.`, string(schemaJSON)),
		InputSchema:  countryInputSchema,
		OutputSchema: capitalInfoOutputSchema,
		OutputKey:    "structured_info_result",
	})
	if err != nil {
		log.Fatalf("Failed to create structured info agent: %v", err)
	}

	fmt.Println("--- Testing Agent with Tool ---")
	callAgent(ctx, capitalAgentWithTool, "capital_tool_result", `{"country": "France"}`)
	callAgent(ctx, capitalAgentWithTool, "capital_tool_result", `{"country": "Canada"}`)

	fmt.Println("\n\n--- Testing Agent with Output Schema (No Tool Use) ---")
	callAgent(ctx, structuredInfoAgentSchema, "structured_info_result", `{"country": "France"}`)
	callAgent(ctx, structuredInfoAgentSchema, "structured_info_result", `{"country": "Japan"}`)
}

func callAgent(ctx context.Context, a agent.Agent, outputKey string, prompt string) {
	fmt.Printf("\n>>> Calling Agent: '%s' | Query: %s\n", a.Name(), prompt)
	sessionService := session.InMemoryService()

	sessionCreateResponse, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  userID,
	})
	if err != nil {
		log.Fatalf("Failed to create the session service: %v", err)
	}

	session := sessionCreateResponse.Session

	config := runner.Config{
		AppName:        appName,
		Agent:          a,
		SessionService: sessionService,
	}

	r, err := runner.New(config)
	if err != nil {
		log.Fatalf("Failed to create the runner: %v", err)
	}

	sessionID := session.ID()
	userMsg := &genai.Content{
		Parts: []*genai.Part{
			genai.NewPartFromText(prompt),
		},
		Role: string(genai.RoleUser),
	}

	for event, err := range r.Run(ctx, userID, sessionID, userMsg, &agent.RunConfig{
		StreamingMode: agent.StreamingModeSSE,
	}) {
		if err != nil {
			fmt.Printf("\nAGENT_ERROR: %v\n", err)
		} else if event.Partial {
			for _, p := range event.Content.Parts {
				fmt.Print(p.Text)
			}
		}
	}

	if outputKey != "" {
		storedOutput, error := session.State().Get(outputKey)
		if error == nil {
			fmt.Printf("--- Session State ['%s']: ", outputKey)
			storedString, isString := storedOutput.(string)
			if isString {
				var prettyJSON map[string]interface{}
				if err := json.Unmarshal([]byte(storedString), &prettyJSON); err == nil {
					indentedJSON, err := json.MarshalIndent(prettyJSON, "", "  ")
					if err == nil {
						fmt.Println(string(indentedJSON))
					} else {
						fmt.Println(storedString)
					}
				} else {
					fmt.Println(storedString)
				}
			} else {
				fmt.Println(storedOutput)
			}
			fmt.Println(strings.Repeat("-", 30))
		}
	}
}
// --8<-- [end:full_code]