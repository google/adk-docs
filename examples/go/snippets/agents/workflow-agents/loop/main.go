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
	"google.golang.org/adk/agent/workflowagents/loopagent"
	"google.golang.org/adk/agent/workflowagents/sequentialagent"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"
	"google.golang.org/genai"
)

const (
	appName    = "IterativeWritingPipeline"
	userID     = "test_user_456"
	modelName  = "gemini-2.5-flash"
	stateDoc   = "current_document"
	stateCrit  = "criticism"
	donePhrase = "No major issues found."
)

// --8<-- [start:init]
// ExitLoopArgs defines the (empty) arguments for the ExitLoop tool.
type ExitLoopArgs struct{}

// ExitLoopResults defines the output of the ExitLoop tool.
type ExitLoopResults struct{}

// ExitLoop is a tool that signals the loop to terminate by setting Escalate to true.
func ExitLoop(ctx tool.Context, input ExitLoopArgs) (ExitLoopResults, error) {
	fmt.Printf("[Tool Call] exitLoop triggered by %s \n", ctx.AgentName())
	ctx.Actions().Escalate = true
	return ExitLoopResults{}, nil
}

func main() {
	ctx := context.Background()

	if err := runAgent(ctx, "Write a document about a cat"); err != nil {
		log.Fatalf("Agent execution failed: %v", err)
	}
}

func runAgent(ctx context.Context, prompt string) error {
	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return fmt.Errorf("failed to create model: %v", err)
	}

	// STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
	initialWriterAgent, err := llmagent.New(llmagent.Config{
		Name:        "InitialWriterAgent",
		Model:       model,
		Description: "Writes the initial document draft based on the topic.",
		Instruction: `You are a Creative Writing Assistant tasked with starting a story.
Write the *first draft* of a short story (aim for 2-4 sentences).
Base the content *only* on the topic provided in the user's prompt.
Output *only* the story/document text. Do not add introductions or explanations.`,
		OutputKey: stateDoc,
	})
	if err != nil {
		return fmt.Errorf("failed to create initial writer agent: %v", err)
	}

	// STEP 2a: Critic Agent (Inside the Refinement Loop)
	criticAgentInLoop, err := llmagent.New(llmagent.Config{
		Name:        "CriticAgent",
		Model:       model,
		Description: "Reviews the current draft, providing critique or signaling completion.",
		Instruction: fmt.Sprintf(`You are a Constructive Critic AI reviewing a short document draft.
**Document to Review:**
"""
{%s}
"""
**Task:**
Review the document.
IF you identify 1-2 *clear and actionable* ways it could be improved:
Provide these specific suggestions concisely. Output *only* the critique text.
ELSE IF the document is coherent and addresses the topic adequately:
Respond *exactly* with the phrase "%s" and nothing else.`, stateDoc, donePhrase),
		OutputKey: stateCrit,
	})
	if err != nil {
		return fmt.Errorf("failed to create critic agent: %v", err)
	}

	exitLoopTool, err := functiontool.New(
		functiontool.Config{
			Name:        "exitLoop",
			Description: "Call this function ONLY when the critique indicates no further changes are needed.",
		},
		ExitLoop,
	)
	if err != nil {
		return fmt.Errorf("failed to create exit loop tool: %v", err)
	}

	// STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
	refinerAgentInLoop, err := llmagent.New(llmagent.Config{
		Name:  "RefinerAgent",
		Model: model,
		Instruction: fmt.Sprintf(`You are a Creative Writing Assistant refining a document based on feedback OR exiting the process.
**Current Document:**

"""
{%s}
"""

**Critique/Suggestions:**
{%s}
**Task:**
Analyze the 'Critique/Suggestions'.
IF the critique is *exactly* "%s":
You MUST call the 'exitLoop' function. Do not output any text.
ELSE (the critique contains actionable feedback):
Carefully apply the suggestions to improve the 'Current Document'. Output *only* the refined document text.`, stateDoc, stateCrit, donePhrase),
		Description: "Refines the document based on critique, or calls exitLoop if critique indicates completion.",
		Tools:       []tool.Tool{exitLoopTool},
		OutputKey:   stateDoc,
	})
	if err != nil {
		return fmt.Errorf("failed to create refiner agent: %v", err)
	}

	// STEP 2: Refinement Loop Agent
	refinementLoop, err := loopagent.New(loopagent.Config{
		AgentConfig: agent.Config{
			Name:      "RefinementLoop",
			SubAgents: []agent.Agent{criticAgentInLoop, refinerAgentInLoop},
		},
		MaxIterations: 5,
	})
	if err != nil {
		return fmt.Errorf("failed to create loop agent: %v", err)
	}

	// STEP 3: Overall Sequential Pipeline
	iterativeWriterAgent, err := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:      appName,
			SubAgents: []agent.Agent{initialWriterAgent, refinementLoop},
		},
	})
	if err != nil {
		return fmt.Errorf("failed to create sequential agent pipeline: %v", err)
	}
	// --8<-- [end:init]

	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          iterativeWriterAgent,
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

	fmt.Printf("---"+" Starting Iterative Writing Pipeline for topic: %q ---"+"\n", prompt)
	loopIteration := 0

	for event, err := range r.Run(ctx, userID, session.Session.ID(), userMsg, agent.RunConfig{
		StreamingMode: agent.StreamingModeNone,
	}) {
		if err != nil {
			return fmt.Errorf("error during agent execution: %v", err)
		}

		if event.Content == nil {
			continue
		}

		outputText := ""
		for _, p := range event.Content.Parts {
			outputText += p.Text
		}
		outputText = strings.TrimSpace(outputText)

		switch event.Author {
		case "InitialWriterAgent":
			fmt.Printf("\n[Initial Draft] By %s (%s):\n%s\n", event.Author, stateDoc, outputText)
		case "CriticAgent":
			loopIteration++
			fmt.Printf("\n[Loop Iteration %d] Critique by %s (%s):\n%s\n", loopIteration, event.Author, stateCrit, outputText)
		case "RefinerAgent":
			if !event.Actions.Escalate {
				fmt.Printf("[Loop Iteration %d] Refinement by %s (%s):\n%s\n", loopIteration, event.Author, stateDoc, outputText)
			}
		}

		if event.Actions.Escalate {
			fmt.Println("\n--- Refinement Loop terminated (Escalation detected) ---")
		}
	}
	fmt.Printf("\n--- Pipeline Finished ---\n")
	return nil
}
