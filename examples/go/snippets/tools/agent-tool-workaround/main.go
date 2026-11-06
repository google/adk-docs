// Copyright 2026 Google LLC
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
	"log"
	"os"
	"time"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/llmagent"
	"google.golang.org/adk/v2/cmd/launcher"
	"google.golang.org/adk/v2/cmd/launcher/console"
	"google.golang.org/adk/v2/cmd/launcher/universal"
	"google.golang.org/adk/v2/model"
	"google.golang.org/adk/v2/model/gemini"
	"google.golang.org/adk/v2/tool"
	"google.golang.org/adk/v2/tool/agenttool"
	"google.golang.org/adk/v2/tool/functiontool"
	"google.golang.org/adk/v2/tool/geminitool"
	"google.golang.org/genai"
)

// --8<-- [start:agents]
func newAgent(m model.LLM) (agent.Agent, error) {
	searchAgent, err := llmagent.New(llmagent.Config{
		Name:        "search_agent",
		Model:       m,
		Description: "Searches the web for current information.",
		Instruction: "Use Google Search to answer the request.",
		Tools:       []tool.Tool{geminitool.GoogleSearch{}},
	})
	if err != nil {
		return nil, err
	}

	currentTime, err := functiontool.New(functiontool.Config{
		Name:        "current_time",
		Description: "Returns the current time in UTC.",
	}, func(ctx agent.Context, args struct{}) (map[string]string, error) {
		return map[string]string{"utc": time.Now().UTC().Format(time.RFC3339)}, nil
	})
	if err != nil {
		return nil, err
	}

	return llmagent.New(llmagent.Config{
		Name:        "assistant",
		Model:       m,
		Instruction: "Use search_agent for web searches and current_time for the time.",
		Tools: []tool.Tool{
			agenttool.New(searchAgent, nil),
			currentTime,
		},
	})
}

// --8<-- [end:agents]

func main() {
	ctx := context.Background()
	m, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
		APIKey: os.Getenv("GOOGLE_API_KEY"),
	})
	if err != nil {
		log.Fatal(err)
	}
	a, err := newAgent(m)
	if err != nil {
		log.Fatal(err)
	}
	l := universal.NewLauncher(console.NewLauncher())
	if err := l.Execute(ctx, &launcher.Config{
		AgentLoader: agent.NewSingleLoader(a),
	}, os.Args[1:]); err != nil {
		log.Fatal(err)
	}
}
