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
	"log"
	"os"
	"strings"
	"time"

	"google.golang.org/genai"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/cmd/launcher"
	"google.golang.org/adk/cmd/launcher/full"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"
)

type CityArgs struct {
	City string `json:"city"`
}

func main() {
	ctx := context.Background()

	// 1. Setup the model.
	// Note: Authentication is handled via GOOGLE_API_KEY environment variable.
	model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{
		APIKey: os.Getenv("GOOGLE_API_KEY"),
	})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	weatherTool, err := functiontool.New[CityArgs, map[string]any](
		functiontool.Config{
			Name:        "get_weather",
			Description: "Retrieves the current weather report for a specified city.",
		},
		func(ctx tool.Context, args CityArgs) (map[string]any, error) {
			if strings.EqualFold(args.City, "new york") {
				return map[string]any{
					"status": "success",
					"report": "The weather in New York is sunny with a temperature of 25 degrees Celsius (77 degrees Fahrenheit).",
				}, nil
			}
			return map[string]any{
				"status":        "error",
				"error_message": "Weather information for '" + args.City + "' is not available.",
			}, nil
		},
	)
	if err != nil {
		log.Fatalf("Failed to create get_weather tool: %v", err)
	}

	currentTimeTool, err := functiontool.New[CityArgs, map[string]any](
		functiontool.Config{
			Name:        "get_current_time",
			Description: "Returns the current time in a specified city.",
		},
		func(ctx tool.Context, args CityArgs) (map[string]any, error) {
			var tzIdentifier string
			if strings.EqualFold(args.City, "new york") {
				tzIdentifier = "America/New_York"
			} else {
				return map[string]any{
					"status":        "error",
					"error_message": "Sorry, I don't have timezone information for " + args.City + ".",
				}, nil
			}

			tz, err := time.LoadLocation(tzIdentifier)
			if err != nil {
				return nil, err
			}

			now := time.Now().In(tz)
			report := "The current time in " + args.City + " is " + now.Format("2006-01-02 15:04:05 MST-0700")
			return map[string]any{
				"status": "success",
				"report": report,
			}, nil
		},
	)
	if err != nil {
		log.Fatalf("Failed to create get_current_time tool: %v", err)
	}

	// 2. Define the agent.
	a, err := llmagent.New(llmagent.Config{
		Name:        "weather_time_agent",
		Model:       model,
		Description: "Agent to answer questions about the time and weather in a city.",
		Instruction: "You are a helpful agent who can answer user questions about the time and weather in a city.",
		Tools: []tool.Tool{
			weatherTool,
			currentTimeTool,
		},
	})
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	// 3. Configure the launcher and run.
	config := &launcher.Config{
		AgentLoader: agent.NewSingleLoader(a),
	}

	l := full.NewLauncher()
	if err = l.Execute(ctx, config, os.Args[1:]); err != nil {
		log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
	}
}

// --8<-- [end:full_code]
