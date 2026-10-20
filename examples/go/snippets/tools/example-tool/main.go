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

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/llmagent"
	"google.golang.org/adk/v2/cmd/launcher"
	"google.golang.org/adk/v2/cmd/launcher/console"
	"google.golang.org/adk/v2/cmd/launcher/universal"
	"google.golang.org/adk/v2/model"
	"google.golang.org/adk/v2/model/gemini"
	"google.golang.org/adk/v2/tool"
	"google.golang.org/adk/v2/tool/exampletool"
	"google.golang.org/genai"
)

// --8<-- [start:examples]
func newAgent(m model.LLM) (agent.Agent, error) {
	examples, err := exampletool.New(exampletool.ExampleToolConfig{
		Examples: []*exampletool.Example{
			{
				Input: genai.NewContentFromText("The delivery arrived early!", "user"),
				Output: []*genai.Content{
					genai.NewContentFromText("positive", "model"),
				},
			},
			{
				Input: genai.NewContentFromText("The package is damaged.", "user"),
				Output: []*genai.Content{
					genai.NewContentFromText("negative", "model"),
				},
			},
		},
	})
	if err != nil {
		return nil, err
	}

	return llmagent.New(llmagent.Config{
		Name:        "sentiment_agent",
		Model:       m,
		Instruction: "Classify sentiment. Reply with only positive or negative.",
		Tools:       []tool.Tool{examples},
	})
}

// --8<-- [end:examples]

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
