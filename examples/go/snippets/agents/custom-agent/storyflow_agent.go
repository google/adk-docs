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
	"fmt"
	"iter"
	"log"

	"google.golang.org/adk/agent/workflowagents/loopagent"
	"google.golang.org/adk/agent/workflowagents/sequentialagent"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/genai"
)

// --8<-- [start:init]
// StoryFlowAgent is a custom agent that orchestrates a story generation workflow.
// It encapsulates the logic of running sub-agents in a specific sequence.
type StoryFlowAgent struct {
	storyGenerator     agent.Agent
	revisionLoopAgent  agent.Agent
	postProcessorAgent agent.Agent
}

// NewStoryFlowAgent creates and configures the entire custom agent workflow.
// It takes individual LLM agents as input and internally creates the necessary
// workflow agents (loop, sequential), returning the final orchestrator agent.
func NewStoryFlowAgent(
	storyGenerator,
	critic,
	reviser,
	grammarCheck,
	toneCheck agent.Agent,
) (agent.Agent, error) {
	loopAgent, err := loopagent.New(loopagent.Config{
		MaxIterations: 2,
		AgentConfig: agent.Config{
			Name:      "CriticReviserLoop",
			SubAgents: []agent.Agent{critic, reviser},
		},
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create loop agent: %w", err)
	}

	sequentialAgent, err := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:      "PostProcessing",
			SubAgents: []agent.Agent{grammarCheck, toneCheck},
		},
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create sequential agent: %w", err)
	}

	// The StoryFlowAgent struct holds the agents needed for the Run method.
	orchestrator := &StoryFlowAgent{
		storyGenerator:     storyGenerator,
		revisionLoopAgent:  loopAgent,
		postProcessorAgent: sequentialAgent,
	}

	// agent.New creates the final agent, wiring up the Run method.
	return agent.New(agent.Config{
		Name:        "StoryFlowAgent",
		Description: "Orchestrates story generation, critique, revision, and checks.",
		SubAgents:   []agent.Agent{storyGenerator, loopAgent, sequentialAgent},
		Run:         orchestrator.Run,
	})
}

// --8<-- [end:init]

// --8<-- [start:executionlogic]
// Run defines the custom execution logic for the StoryFlowAgent.
func (s *StoryFlowAgent) Run(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
	return func(yield func(*session.Event, error) bool) {
		// Stage 1: Initial Story Generation
		for event, err := range s.storyGenerator.Run(ctx) {
			if err != nil {
				yield(nil, fmt.Errorf("story generator failed: %w", err))
				return
			}
			if !yield(event, nil) {
				return
			}
		}

		// Check if story was generated before proceeding
		currentStory, err := ctx.Session().State().Get("current_story")
		if err != nil || currentStory == "" {
			log.Println("Failed to generate initial story. Aborting workflow.")
			return
		}

		// Stage 2: Critic-Reviser Loop
		for event, err := range s.revisionLoopAgent.Run(ctx) {
			if err != nil {
				yield(nil, fmt.Errorf("loop agent failed: %w", err))
				return
			}
			if !yield(event, nil) {
				return
			}
		}

		// Stage 3: Post-Processing
		for event, err := range s.postProcessorAgent.Run(ctx) {
			if err != nil {
				yield(nil, fmt.Errorf("sequential agent failed: %w", err))
				return
			}
			if !yield(event, nil) {
				return
			}
		}

		// Stage 4: Conditional Regeneration
		toneResult, err := ctx.Session().State().Get("tone_check_result")
		if err != nil {
			log.Printf("Could not read tone_check_result from state: %v. Assuming tone is not negative.", err)
			return
		}

		if tone, ok := toneResult.(string); ok && tone == "negative" {
			log.Println("Tone is negative. Regenerating story...")
			for event, err := range s.storyGenerator.Run(ctx) {
				if err != nil {
					yield(nil, fmt.Errorf("story regeneration failed: %w", err))
					return
				}
				if !yield(event, nil) {
					return
				}
			}
		} else {
			log.Println("Tone is not negative. Keeping current story.")
		}
	}
}

// --8<-- [end:executionlogic]

const (
	modelName = "gemini-2.0-flash"
	appName   = "story_app"
	userID    = "user_12345"
)

func main() {
	ctx := context.Background()
	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	// --8<-- [start:llmagents]
	// --- Define the individual LLM agents ---
	storyGenerator, err := llmagent.New(llmagent.Config{
		Name:        "StoryGenerator",
		Model:       model,
		Description: "Generates the initial story.",
		Instruction: "You are a story writer. Write a short story (around 100 words) about a cat, based on the topic: {topic}",
		OutputKey:   "current_story",
	})
	if err != nil {
		log.Fatalf("Failed to create StoryGenerator agent: %v", err)
	}

	critic, err := llmagent.New(llmagent.Config{
		Name:        "Critic",
		Model:       model,
		Description: "Critiques the story.",
		Instruction: "You are a story critic. Review the story: {current_story}. Provide 1-2 sentences of constructive criticism on how to improve it. Focus on plot or character.",
		OutputKey:   "criticism",
	})
	if err != nil {
		log.Fatalf("Failed to create Critic agent: %v", err)
	}

	reviser, err := llmagent.New(llmagent.Config{
		Name:        "Reviser",
		Model:       model,
		Description: "Revises the story based on criticism.",
		Instruction: "You are a story reviser. Revise the story: {current_story}, based on the criticism: {criticism}. Output only the revised story.",
		OutputKey:   "current_story",
	})
	if err != nil {
		log.Fatalf("Failed to create Reviser agent: %v", err)
	}

	grammarCheck, err := llmagent.New(llmagent.Config{
		Name:        "GrammarCheck",
		Model:       model,
		Description: "Checks grammar and suggests corrections.",
		Instruction: "You are a grammar checker. Check the grammar of the story: {current_story}. Output only the suggested corrections as a list, or output 'Grammar is good!' if there are no errors.",
		OutputKey:   "grammar_suggestions",
	})
	if err != nil {
		log.Fatalf("Failed to create GrammarCheck agent: %v", err)
	}

	toneCheck, err := llmagent.New(llmagent.Config{
		Name:        "ToneCheck",
		Model:       model,
		Description: "Analyzes the tone of the story.",
		Instruction: "You are a tone analyzer. Analyze the tone of the story: {current_story}. Output only one word: 'positive' if the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral' otherwise.",
		OutputKey:   "tone_check_result",
	})
	if err != nil {
		log.Fatalf("Failed to create ToneCheck agent: %v", err)
	}
	// --8<-- [end:llmagents]

	// --8<-- [start:story_flow_agent]
	// Instantiate the custom agent, which encapsulates the workflow agents.
	storyFlowAgent, err := NewStoryFlowAgent(
		storyGenerator,
		critic,
		reviser,
		grammarCheck,
		toneCheck,
	)
	if err != nil {
		log.Fatalf("Failed to create story flow agent: %v", err)
	}

	// --- Run the Agent ---
	sessionService := session.InMemoryService()
	initialState := map[string]any{
		"topic": "a brave kitten exploring a haunted house",
	}
	sessionInstance, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  userID,
		State:   initialState,
	})
	if err != nil {
		log.Fatalf("Failed to create session: %v", err)
	}

	userTopic := "a lonely robot finding a friend in a junkyard"

	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          storyFlowAgent,
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatalf("Failed to create runner: %v", err)
	}

	input := genai.NewContentFromText("Generate a story about: "+userTopic, genai.RoleUser)
	events := r.Run(ctx, userID, sessionInstance.Session.ID(), input, agent.RunConfig{
		StreamingMode: agent.StreamingModeSSE,
	})

	var finalResponse string
	for event, err := range events {
		if err != nil {
			log.Fatalf("An error occurred during agent execution: %v", err)
		}

		for _, part := range event.Content.Parts {
			// Accumulate text from all parts of the final response.
			finalResponse += part.Text
		}
	}

	fmt.Println("\n--- Agent Interaction Result ---")
	fmt.Println("Agent Final Response: " + finalResponse)

	finalSession, err := sessionService.Get(ctx, &session.GetRequest{
		UserID:    userID,
		AppName:   appName,
		SessionID: sessionInstance.Session.ID(),
	})

	if err != nil {
		log.Fatalf("Failed to retrieve final session: %v", err)
	}

	fmt.Println("Final Session State:", finalSession.Session.State())
}

// --8<-- [end:story_flow_agent]
// --8<-- [end:full_code]
