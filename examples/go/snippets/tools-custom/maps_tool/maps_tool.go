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
	"os"
	"os/exec"

	"github.com/modelcontextprotocol/go-sdk/mcp"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/cmd/launcher/adk"
	"google.golang.org/adk/cmd/launcher/full"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/server/restapi/services"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/mcptoolset"
	"google.golang.org/genai"
)

func main() {
	// Retrieve the API key from an environment variable.
	// This is the recommended approach for security.
	googleMapsAPIKey := os.Getenv("GOOGLE_MAPS_API_KEY")
	if googleMapsAPIKey == "" {
		log.Fatal("GOOGLE_MAPS_API_KEY environment variable not set")
	}

	ctx := context.Background()
	// Get the Gemini API Key from an environment variable
	geminiAPIKey := os.Getenv("GOOGLE_API_KEY")
	if geminiAPIKey == "" {
		log.Fatal("GOOGLE_API_KEY environment variable not set")
	}

	model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{APIKey: geminiAPIKey})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	cmd := exec.Command("npx", "-y", "@modelcontextprotocol/server-google-maps")
	// Pass the API key as an environment variable to the npx process
	// This is how the MCP server for Google Maps expects the key.
	cmd.Env = append(os.Environ(), fmt.Sprintf("GOOGLE_MAPS_API_KEY=%s", googleMapsAPIKey))

	mcpToolSet, err := mcptoolset.New(mcptoolset.Config{
		Transport: &mcp.CommandTransport{Command: cmd},
	})
	if err != nil {
		log.Fatalf("Failed to create MCP tool set: %v", err)
	}

	// Create LLMAgent with MCP tool set
	agent, err := llmagent.New(llmagent.Config{
		Name:        "maps_assistant_agent",
		Model:       model,
		Description: "Help the user with mapping, directions, and finding places using Google Maps tools.",
		Instruction: "Help the user with mapping, directions, and finding places using Google Maps tools.",
		Toolsets:    []tool.Toolset{mcpToolSet},
	})

	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}
	config := &adk.Config{
		AgentLoader: services.NewSingleAgentLoader(agent),
	}
	l := full.NewLauncher()
	err = l.Execute(ctx, config, os.Args[1:])
	if err != nil {
		log.Fatalf("run failed: %v\n\n%s", err, l.CommandLineSyntax())
	}
}
