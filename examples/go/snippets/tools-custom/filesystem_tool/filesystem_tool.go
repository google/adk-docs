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
	"path/filepath"

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
	// It's good practice to define paths dynamically if possible,
	// or ensure the user understands the need for an ABSOLUTE path.
	// For this example, we'll construct a path relative to the current working directory.
	// REPLACE THIS with an actual absolute path if needed for your setup.
	targetFolderPath, err := filepath.Abs("./test_data")
	if err != nil {
		log.Fatalf("Failed to get absolute path: %v", err)
	}
	// Ensure the directory exists
	if err := os.MkdirAll(targetFolderPath, 0755); err != nil {
		log.Fatalf("Failed to create target directory: %v", err)
	}
	fmt.Printf("Using target folder: %s\n", targetFolderPath)

	ctx := context.Background()
	// Get the API Key from an environment variable
	apiKey := os.Getenv("GOOGLE_API_KEY")
	if apiKey == "" {
		log.Fatal("GOOGLE_API_KEY environment variable not set")
	}

	model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{APIKey: apiKey})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	mcpToolset, err := mcptoolset.New(mcptoolset.Config{
		Transport: &mcp.CommandTransport{
			Command: exec.Command("npx",
				"-y",
				"@modelcontextprotocol/server-filesystem",
				targetFolderPath,
			),
		},
		// Optional: Filter which tools from the MCP server are exposed
		// ToolFilter: tool.StringPredicate([]string{"list_directory", "read_file"}),
	})
	if err != nil {
		log.Fatalf("Failed to create MCP toolset: %v", err)
	}

	agent, err := llmagent.New(llmagent.Config{
		Name:        "filesystem_assistant_agent",
		Model:       model,
		Description: "Help the user manage their files. You can list files, read files, etc.",
		Instruction: "Help the user manage their files. You can list files, read files, etc.",
		Toolsets:    []tool.Toolset{mcpToolset},
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
