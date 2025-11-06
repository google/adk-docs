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
	"google.golang.org/adk/tool/functiontool"

	"google.golang.org/genai"
)

// --- Main Runnable Example ---

const (
	modelName = "gemini-2.0-flash"
	appName   = "agent_comparison_app"
	userID    = "test_user_456"
)

type getCapitalCityArgs struct {
	Country string `json:"country" jsonschema:"The country to get the capital of."`
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

// callAgent is a helper function to execute an agent with a given prompt and handle its output.
func callAgent(ctx context.Context, a agent.Agent, outputKey string, prompt string) {
	fmt.Printf("\n>>> Calling Agent: '%s' | Query: %s\n", a.Name(), prompt)
	// Create an in-memory session service to manage agent state.
	sessionService := session.InMemoryService()

	// Create a new session for the agent interaction.
	sessionCreateResponse, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  userID,
	})
	if err != nil {
		log.Fatalf("Failed to create the session service: %v", err)
	}

	session := sessionCreateResponse.Session

	// Configure the runner with the application name, agent, and session service.
	config := runner.Config{
		AppName:        appName,
		Agent:          a,
		SessionService: sessionService,
	}

	// Create a new runner instance.
	r, err := runner.New(config)
	if err != nil {
		log.Fatalf("Failed to create the runner: %v", err)
	}

	// Prepare the user's message to send to the agent.
	sessionID := session.ID()
	userMsg := &genai.Content{
		Parts: []*genai.Part{
			genai.NewPartFromText(prompt),
		},
		Role: string(genai.RoleUser),
	}

	// Run the agent and process the streaming events.
	for event, err := range r.Run(ctx, userID, sessionID, userMsg, agent.RunConfig{
		StreamingMode: agent.StreamingModeSSE,
	}) {
		if err != nil {
			fmt.Printf("\nAGENT_ERROR: %v\n", err)
		} else if event.Partial {
			// Print partial responses as they are received.
			for _, p := range event.Content.Parts {
				fmt.Print(p.Text)
			}
		}
	}

	// After the run, check if there's an expected output key in the session state.
	if outputKey != "" {
		storedOutput, error := session.State().Get(outputKey)
		if error == nil {
			// Pretty-print the stored output if it's a JSON string.
			fmt.Printf("\n--- Session State ['%s']: ", outputKey)
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

func main() {
	ctx := context.Background()

	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	capitalTool, err := functiontool.New(
		functiontool.Config{
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

// --8<-- [end:full_code]
