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

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/agent/workflowagents/sequentialagent"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/genai"
)

const (
	appName   = "CodePipelineAgent"
	userID    = "test_user_456"
	modelName = "gemini-2.5-flash"
)

func main() {
	ctx := context.Background()

	if err := runAgent(ctx, "Write a Go function to calculate the factorial of a number."); err != nil {
		log.Fatalf("Agent execution failed: %v", err)
	}
}

func runAgent(ctx context.Context, prompt string) error {
	// --8<-- [start:init]
	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return fmt.Errorf("failed to create model: %v", err)
	}

	codeWriterAgent, err := llmagent.New(llmagent.Config{
		Name:        "CodeWriterAgent",
		Model:       model,
		Description: "Writes initial Go code based on a specification.",
		Instruction: `You are a Go Code Generator.
Based *only* on the user's request, write Go code that fulfills the requirement.
Output *only* the complete Go code block, enclosed in triple backticks ('''go ... ''').
Do not add any other text before or after the code block.`,
		OutputKey: "generated_code",
	})
	if err != nil {
		return fmt.Errorf("failed to create code writer agent: %v", err)
	}

	codeReviewerAgent, err := llmagent.New(llmagent.Config{
		Name:        "CodeReviewerAgent",
		Model:       model,
		Description: "Reviews code and provides feedback.",
		Instruction: `You are an expert Go Code Reviewer.
Your task is to provide constructive feedback on the provided code.

**Code to Review:**
'''go
{generated_code}
'''

**Review Criteria:**
1.  **Correctness:** Does the code work as intended? Are there logic errors?
2.  **Readability:** Is the code clear and easy to understand? Follows Go style guidelines?
3.  **Idiomatic Go:** Does the code use Go's features in a natural and standard way?
4.  **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
5.  **Best Practices:** Does the code follow common Go best practices?

**Output:**
Provide your feedback as a concise, bulleted list. Focus on the most important points for improvement.
If the code is excellent and requires no changes, simply state: "No major issues found."
Output *only* the review comments or the "No major issues" statement.`,
		OutputKey: "review_comments",
	})
	if err != nil {
		return fmt.Errorf("failed to create code reviewer agent: %v", err)
	}

	codeRefactorerAgent, err := llmagent.New(llmagent.Config{
		Name:        "CodeRefactorerAgent",
		Model:       model,
		Description: "Refactors code based on review comments.",
		Instruction: `You are a Go Code Refactoring AI.
Your goal is to improve the given Go code based on the provided review comments.

**Original Code:**
'''go
{generated_code}
'''

**Review Comments:**
{review_comments}

**Task:**
Carefully apply the suggestions from the review comments to refactor the original code.
If the review comments state "No major issues found," return the original code unchanged.
Ensure the final code is complete, functional, and includes necessary imports.

**Output:**
Output *only* the final, refactored Go code block, enclosed in triple backticks ('''go ... ''').
Do not add any other text before or after the code block.`,
		OutputKey: "refactored_code",
	})
	if err != nil {
		return fmt.Errorf("failed to create code refactorer agent: %v", err)
	}

	codePipelineAgent, err := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        appName,
			Description: "Executes a sequence of code writing, reviewing, and refactoring.",
			SubAgents: []agent.Agent{
				codeWriterAgent,
				codeReviewerAgent,
				codeRefactorerAgent,
			},
		},
	})
	if err != nil {
		return fmt.Errorf("failed to create sequential agent: %v", err)
	}
	// --8<-- [end:init]

	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          codePipelineAgent,
		SessionService: sessionService,
	})
	if err != nil {
		return fmt.Errorf("failed to create runner: %v", err)
	}

	session, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  userID,
	})
	if err != nil {
		return fmt.Errorf("failed to create session: %v", err)
	}

	userMsg := &genai.Content{
		Parts: []*genai.Part{{Text: prompt}},
		Role:  string(genai.RoleUser),
	}

	fmt.Printf("Running agent pipeline for prompt: %q\n---\n", prompt)
	for event, err := range r.Run(ctx, userID, session.Session.ID(), userMsg, agent.RunConfig{
		StreamingMode: agent.StreamingModeNone,
	}) {
		if err != nil {
			return fmt.Errorf("error during agent execution: %v", err)
		}

		for _, p := range event.Content.Parts {
			fmt.Print(p.Text)
		}
	}
	fmt.Println("\n---\nPipeline finished.")
	return nil
}
