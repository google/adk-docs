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

	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"

	"google.golang.org/genai"
)

// --- Documentation Snippets ---
// The following functions are self-contained examples for documentation.
// They are not called by the main application.

func _snippet_identity(model model.LLM) {
	// --8<-- [start:identity]
	// Example: Defining the basic identity
	agent, err := llmagent.New(llmagent.Config{
		Name:        "capital_agent",
		Model:       model,
		Description: "Answers user questions about the capital city of a given country.",
		// instruction and tools will be added next
	})
	// --8<-- [end:identity]

	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Agent created:", agent.Name())
}

func _snippet_instruction(model model.LLM) {
	// --8<-- [start:instruction]
	// Example: Adding instructions
	agent, err := llmagent.New(llmagent.Config{
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
		// tools will be added next
	})
	// --8<-- [end:instruction]

	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Agent with instruction created:", agent.Name())
}

func _snippet_tool_example(model model.LLM) {
	// --8<-- [start:tool_example]
	// Define a tool function
	type getCapitalCityArgs struct {
		Country string `json:"country" jsonschema:"The country to get the capital of."`
	}
	getCapitalCity := func(ctx tool.Context, args getCapitalCityArgs) (map[string]any, error) {
		// Replace with actual logic (e.g., API call, database lookup)
		capitals := map[string]string{"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
		capital, ok := capitals[strings.ToLower(args.Country)]
		if !ok {
			return nil, fmt.Errorf("Sorry, I don't know the capital of %s.", args.Country)
		}
		return map[string]any{"result": capital}, nil
	}

	// Add the tool to the agent
	capitalTool, err := functiontool.New(
		functiontool.Config{
			Name:        "get_capital_city",
			Description: "Retrieves the capital city for a given country.",
		},
		getCapitalCity,
	)
	if err != nil {
		log.Fatal(err)
	}
	agent, err := llmagent.New(llmagent.Config{
		Name:        "capital_agent",
		Model:       model,
		Description: "Answers user questions about the capital city of a given country.",
		Instruction: "You are an agent that provides the capital city of a country... (previous instruction text)",
		Tools:       []tool.Tool{capitalTool},
	})
	// --8<-- [end:tool_example]

	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Agent with tool created:", agent.Name())
}

func _snippet_schema_example(model model.LLM) {
	// --8<-- [start:schema_example]
	capitalOutput := &genai.Schema{
		Type:        genai.TypeObject,
		Description: "Schema for capital city information.",
		Properties: map[string]*genai.Schema{
			"capital": {
				Type:        genai.TypeString,
				Description: "The capital city of the country.",
			},
		},
	}

	agent, err := llmagent.New(llmagent.Config{
		Name:         "structured_capital_agent",
		Model:        model,
		Description:  "Provides capital information in a structured format.",
		Instruction:  `You are a Capital Information Agent. Given a country, respond ONLY with a JSON object containing the capital. Format: {"capital": "capital_name"}`,
		OutputSchema: capitalOutput,
		OutputKey:    "found_capital",
		// Cannot use the capitalTool tool effectively here
	})
	// --8<-- [end:schema_example]
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Agent with output schema created:", agent.Name())
}

func _snippet_gen_config(model model.LLM) {
	// --8<-- [start:gen_config]
	temperature := float32(0.2)
	agent, err := llmagent.New(llmagent.Config{
		Name:  "gen_config_agent",
		Model: model,
		GenerateContentConfig: &genai.GenerateContentConfig{
			Temperature:     &temperature,
			MaxOutputTokens: 250,
		},
	})
	// --8<-- [end:gen_config]

	if err != nil {
		log.Fatalf("Failed to create agent with generation config: %v", err)
	}
	fmt.Println("Agent with generation config created:", agent.Name())
}

func _snippet_include_contents(model model.LLM) {
	// --8<-- [start:include_contents]
	agent, err := llmagent.New(llmagent.Config{
		Name:            "stateless_agent",
		Model:           model,
		IncludeContents: llmagent.IncludeContentsNone,
	})
	// --8<-- [end:include_contents]
	if err != nil {
		log.Fatalf("Failed to create agent with include contents none: %v", err)
	}
	fmt.Println("Stateless agent created:", agent.Name())
}

func main() {
	// Call all snippet functions to ensure they compile.
	ctx := context.Background()

	modelName := "gemini-2.5-flash"
	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	_snippet_include_contents(model)
	_snippet_identity(model)
	_snippet_instruction(model)
	_snippet_tool_example(model)
	_snippet_gen_config(model)
	_snippet_schema_example(model)
	// Note: The full runnable example is in the ../main.go file.
}
