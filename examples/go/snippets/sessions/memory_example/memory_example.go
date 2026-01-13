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

// --8<-- [start:full_example]

import (
	"context"
	"fmt"
	"log"
	"strings"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/memory"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"
	"google.golang.org/genai"
)

const (
	appName = "go_memory_example_app"
	userID  = "go_mem_user"
	modelID = "gemini-2.5-pro"
)

// Args defines the input structure for the memory search tool.
type Args struct {
	Query string `json:"query" jsonschema:"The query to search for in the memory."`
}

// Result defines the output structure for the memory search tool.
type Result struct {
	Results []string `json:"results"`
}

// --8<-- [start:tool_search]

// memorySearchToolFunc is the implementation of the memory search tool.
// This function demonstrates accessing memory via tool.Context.
func memorySearchToolFunc(tctx tool.Context, args Args) (Result, error) {
	fmt.Printf("Tool: Searching memory for query: '%s'\n", args.Query)
	// The SearchMemory function is available on the context.
	searchResults, err := tctx.SearchMemory(context.Background(), args.Query)
	if err != nil {
		log.Printf("Error searching memory: %v", err)
		return Result{}, fmt.Errorf("failed memory search")
	}

	var results []string
	for _, res := range searchResults.Memories {
		if res.Content != nil {
			results = append(results, textParts(res.Content)...)
		}
	}
	return Result{Results: results}, nil
}

// Define a tool that can search memory.
var memorySearchTool = must(functiontool.New(
	functiontool.Config{
		Name:        "search_past_conversations",
		Description: "Searches past conversations for relevant information.",
	},
	memorySearchToolFunc,
))

// --8<-- [end:tool_search]

// This example demonstrates how to use the MemoryService in the Go ADK.
// It covers two main scenarios:
// 1. Adding a completed session to memory and recalling it in a new session.
// 2. Searching memory from within a custom tool using the tool.Context.
func main() {
	ctx := context.Background()

	// --- Services ---
	// Services must be shared across runners to share state and memory.
	sessionService := session.InMemoryService()
	memoryService := memory.InMemoryService() // Use in-memory for this demo.

	// --- Scenario 1: Capture information in one session ---
	fmt.Println("--- Turn 1: Capturing Information ---")
	infoCaptureAgent := must(llmagent.New(llmagent.Config{
		Name:        "InfoCaptureAgent",
		Model:       must(gemini.NewModel(ctx, modelID, nil)),
		Instruction: "Acknowledge the user's statement.",
	}))

	runner1 := must(runner.New(runner.Config{
		AppName:        appName,
		Agent:          infoCaptureAgent,
		SessionService: sessionService,
		MemoryService:  memoryService, // Provide the memory service to the Runner
	}))

	session1ID := "session_info"
	must(sessionService.Create(ctx, &session.CreateRequest{AppName: appName, UserID: userID, SessionID: session1ID}))

	userInput1 := genai.NewContentFromText("My favorite project is Project Alpha.", "user")
	var finalResponseText string
	for event, err := range runner1.Run(ctx, userID, session1ID, userInput1, agent.RunConfig{}) {
		if err != nil {
			log.Printf("Agent 1 Error: %v", err)
			continue
		}
		if event.Content != nil && !event.LLMResponse.Partial {
			finalResponseText = strings.Join(textParts(event.LLMResponse.Content), "")
		}
	}
	fmt.Printf("Agent 1 Response: %s\n", finalResponseText)

	// Add the completed session to the Memory Service
	fmt.Println("\n--- Adding Session 1 to Memory ---")
	resp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: session1ID})
	if err != nil {
		log.Fatalf("Failed to get completed session: %v", err)
	}
	if err := memoryService.AddSession(ctx, resp.Session); err != nil {
		log.Fatalf("Failed to add session to memory: %v", err)
	}
	fmt.Println("Session added to memory.")

	// --- Scenario 2: Recall the information in a new session using a tool ---
	fmt.Println("\n--- Turn 2: Recalling Information ---")

	memoryRecallAgent := must(llmagent.New(llmagent.Config{
		Name:        "MemoryRecallAgent",
		Model:       must(gemini.NewModel(ctx, modelID, nil)),
		Instruction: "Answer the user's question. Use the 'search_past_conversations' tool if the answer might be in past conversations.",
		Tools:       []tool.Tool{memorySearchTool}, // Give the agent the tool
	}))

	runner2 := must(runner.New(runner.Config{
		Agent:          memoryRecallAgent,
		AppName:        appName,
		SessionService: sessionService,
		MemoryService:  memoryService,
	}))

	session2ID := "session_recall"
	must(sessionService.Create(ctx, &session.CreateRequest{AppName: appName, UserID: userID, SessionID: session2ID}))
	userInput2 := genai.NewContentFromText("What is my favorite project?", "user")

	var finalResponseText2 string
	for event, err := range runner2.Run(ctx, userID, session2ID, userInput2, agent.RunConfig{}) {
		if err != nil {
			log.Printf("Agent 2 Error: %v", err)
			continue
		}
		if event.Content != nil && !event.LLMResponse.Partial {
			finalResponseText2 = strings.Join(textParts(event.LLMResponse.Content), "")
		}
	}
	fmt.Printf("Agent 2 Response: %s\n", finalResponseText2)
}

// --8<-- [end:full_example]

// --- Helper Functions ---

func must[T any](v T, err error) T {
	if err != nil {
		log.Fatalf("Setup failed: %v", err)
	}
	return v
}

func textParts(c *genai.Content) (ret []string) {
	if c == nil {
		return nil
	}
	for _, p := range c.Parts {
		if p.Text != "" {
			ret = append(ret, p.Text)
		}
	}
	return ret
}
