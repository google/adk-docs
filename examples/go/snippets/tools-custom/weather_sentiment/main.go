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
	"google.golang.org/adk/tool/functiontool"
	"google.golang.org/genai"
)

type getWeatherReportArgs struct {
	City string `json:"city" jsonschema:"The city for which to get the weather report."`
}

type getWeatherReportResult struct {
	Status       string `json:"status"`
	Report       string `json:"report,omitempty"`
	ErrorMessage string `json:"error_message,omitempty"`
}

func getWeatherReport(ctx tool.Context, args getWeatherReportArgs) getWeatherReportResult {
	if strings.ToLower(args.City) == "london" {
		return getWeatherReportResult{Status: "success", Report: "The current weather in London is cloudy with a temperature of 18 degrees Celsius and a chance of rain."}
	}
	if strings.ToLower(args.City) == "paris" {
		return getWeatherReportResult{Status: "success", Report: "The weather in Paris is sunny with a temperature of 25 degrees Celsius."}
	}
	return getWeatherReportResult{Status: "error", ErrorMessage: fmt.Sprintf("Weather information for '%s' is not available.", args.City)}
}

type analyzeSentimentArgs struct {
	Text string `json:"text" jsonschema:"The text to analyze for sentiment."`
}

type analyzeSentimentResult struct {
	Sentiment  string  `json:"sentiment"`
	Confidence float64 `json:"confidence"`
}

func analyzeSentiment(ctx tool.Context, args analyzeSentimentArgs) analyzeSentimentResult {
	if strings.Contains(strings.ToLower(args.Text), "good") || strings.Contains(strings.ToLower(args.Text), "sunny") {
		return analyzeSentimentResult{Sentiment: "positive", Confidence: 0.8}
	}
	if strings.Contains(strings.ToLower(args.Text), "rain") || strings.Contains(strings.ToLower(args.Text), "bad") {
		return analyzeSentimentResult{Sentiment: "negative", Confidence: 0.7}
	}
	return analyzeSentimentResult{Sentiment: "neutral", Confidence: 0.6}
}

func main() {
	ctx := context.Background()
	model, err := gemini.NewModel(ctx, "gemini-2.0-flash", &genai.ClientConfig{})
	if err != nil {
		log.Fatal(err)
	}

	weatherTool, err := functiontool.New(
		functiontool.Config{
			Name:        "get_weather_report",
			Description: "Retrieves the current weather report for a specified city.",
		},
		getWeatherReport,
	)
	if err != nil {
		log.Fatal(err)
	}

	sentimentTool, err := functiontool.New(
		functiontool.Config{
			Name:        "analyze_sentiment",
			Description: "Analyzes the sentiment of the given text.",
		},
		analyzeSentiment,
	)
	if err != nil {
		log.Fatal(err)
	}

	weatherSentimentAgent, err := llmagent.New(llmagent.Config{
		Name:        "weather_sentiment_agent",
		Model:       model,
		Instruction: "You are a helpful assistant that provides weather information and analyzes the sentiment of user feedback. **If the user asks about the weather in a specific city, use the 'get_weather_report' tool to retrieve the weather details.** **If the 'get_weather_report' tool returns a 'success' status, provide the weather report to the user.** **If the 'get_weather_report' tool returns an 'error' status, inform the user that the weather information for the specified city is not available and ask if they have another city in mind.** **After providing a weather report, if the user gives feedback on the weather (e.g., 'That's good' or 'I don't like rain'), use the 'analyze_sentiment' tool to understand their sentiment.** Then, briefly acknowledge their sentiment. You can handle these tasks sequentially if needed.",
		Tools:       []tool.Tool{weatherTool, sentimentTool},
	})
	if err != nil {
		log.Fatal(err)
	}

	sessionService := session.InMemoryService()
	runner, err := runner.New(runner.Config{
		AppName:        "weather_sentiment_agent",
		Agent:          weatherSentimentAgent,
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatal(err)
	}

	session, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: "weather_sentiment_agent",
		UserID:  "user1234",
	})
	if err != nil {
		log.Fatal(err)
	}

	run(ctx, runner, session.Session.ID(), "weather in london?")
	run(ctx, runner, session.Session.ID(), "I don't like rain.")
}

func run(ctx context.Context, r *runner.Runner, sessionID string, prompt string) {
	fmt.Printf("\n> %s\n", prompt)
	events := r.Run(
		ctx,
		"user1234",
		sessionID,
		genai.NewContentFromText(prompt, genai.RoleUser),
		agent.RunConfig{
			StreamingMode: agent.StreamingModeNone,
		},
	)
	for event, err := range events {
		if err != nil {
			log.Fatalf("ERROR during agent execution: %v", err)
		}

		if event.Content.Parts[0].Text != "" {
			fmt.Printf("Agent Response: %s\n", event.Content.Parts[0].Text)
		}
	}
}
