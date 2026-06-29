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

// Package main provides snippet examples for graph-based workflow agents in ADK Go.
package main

import (
	"context"
	"fmt"
	"iter"
	"log"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/workflowagents/sequentialagent"
	"google.golang.org/adk/v2/model"
	"google.golang.org/adk/v2/session"
	"google.golang.org/genai"
)

// --8<-- [start:sequential-get-started]
// cityGeneratorRun yields a fixed city name and writes it to session state.
func cityGeneratorRun(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
	return func(yield func(*session.Event, error) bool) {
		city := "Tokyo"
		if err := ctx.Session().State().Set("city_name", city); err != nil {
			yield(nil, fmt.Errorf("failed to set city_name: %w", err))
			return
		}
		yield(&session.Event{
			LLMResponse: model.LLMResponse{
				Content: &genai.Content{
					Parts: []*genai.Part{{Text: city}},
				},
			},
		}, nil)
	}
}

// lookupTimeRun reads the city from state and returns simulated time
// information for that city.
func lookupTimeRun(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
	return func(yield func(*session.Event, error) bool) {
		city, _ := ctx.Session().State().Get("city_name")
		timeInfo := fmt.Sprintf("10:10 AM in %v", city)
		if err := ctx.Session().State().Set("time_info", timeInfo); err != nil {
			yield(nil, fmt.Errorf("failed to set time_info: %w", err))
			return
		}
		yield(&session.Event{
			LLMResponse: model.LLMResponse{
				Content: &genai.Content{
					Parts: []*genai.Part{{Text: timeInfo}},
				},
			},
		}, nil)
	}
}

// cityReportRun formats a final message combining the city and time from state.
func cityReportRun(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
	return func(yield func(*session.Event, error) bool) {
		city, _ := ctx.Session().State().Get("city_name")
		timeStr, _ := ctx.Session().State().Get("time_info")
		msg := fmt.Sprintf("It is %v in %v right now.\nWORKFLOW COMPLETED.", timeStr, city)
		yield(&session.Event{
			LLMResponse: model.LLMResponse{
				Content: &genai.Content{
					Parts: []*genai.Part{{Text: msg}},
				},
			},
		}, nil)
	}
}

func newSequentialGetStarted() (agent.Agent, error) {
	cityAgent, err := agent.New(agent.Config{
		Name:        "city_generator_agent",
		Description: "Returns the name of a random city and stores it in state.",
		Run:         cityGeneratorRun,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create city agent: %w", err)
	}

	timeAgent, err := agent.New(agent.Config{
		Name:        "lookup_time_agent",
		Description: "Reads the city from state and returns the current time.",
		Run:         lookupTimeRun,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create time agent: %w", err)
	}

	reportAgent, err := agent.New(agent.Config{
		Name:        "city_report_agent",
		Description: "Reports the city and current time from state.",
		Run:         cityReportRun,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create report agent: %w", err)
	}

	rootAgent, err := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        "root_agent",
			Description: "A sequential workflow: generate city → look up time → report.",
			SubAgents:   []agent.Agent{cityAgent, timeAgent, reportAgent},
		},
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create sequential agent: %w", err)
	}

	return rootAgent, nil
}

// --8<-- [end:sequential-get-started]

// --8<-- [start:process-pipeline]
// messageProcessorRun classifies an incoming message by writing the category
// to session state.
func messageProcessorRun(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
	return func(yield func(*session.Event, error) bool) {
		// In a real workflow this step calls an LLM; here we return a fixed
		// category for illustration.
		category := "BUG"
		if err := ctx.Session().State().Set("message_category", category); err != nil {
			yield(nil, fmt.Errorf("failed to set message_category: %w", err))
			return
		}
		yield(&session.Event{
			LLMResponse: model.LLMResponse{
				Content: &genai.Content{
					Parts: []*genai.Part{{Text: category}},
				},
			},
		}, nil)
	}
}

// bugHandlerRun handles messages that were classified as bugs.
func bugHandlerRun(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
	return func(yield func(*session.Event, error) bool) {
		yield(&session.Event{
			LLMResponse: model.LLMResponse{
				Content: &genai.Content{
					Parts: []*genai.Part{{Text: "Handling bug..."}},
				},
			},
		}, nil)
	}
}

func newProcessPipeline() (agent.Agent, error) {
	processAgent, err := agent.New(agent.Config{
		Name:        "process_message",
		Description: "Classifies a user message into BUG, CUSTOMER_SUPPORT, or LOGISTICS.",
		Run:         messageProcessorRun,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create process agent: %w", err)
	}

	bugAgent, err := agent.New(agent.Config{
		Name:        "bug_handler",
		Description: "Handles bug reports.",
		Run:         bugHandlerRun,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create bug handler: %w", err)
	}

	// In Go, conditional routing is expressed by composing workflow agents and
	// reading session state within each sub-agent's Run function. A
	// SequentialAgent runs each sub-agent in the listed order; the category
	// written to state by processAgent is available to every subsequent agent.
	rootAgent, err := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        "routing_workflow",
			Description: "Classifies then routes a message to the appropriate handler.",
			SubAgents:   []agent.Agent{processAgent, bugAgent},
		},
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create routing workflow: %w", err)
	}

	return rootAgent, nil
}

// --8<-- [end:process-pipeline]

func main() {
	ctx := context.Background()
	_ = ctx

	seqAgent, err := newSequentialGetStarted()
	if err != nil {
		log.Fatalf("Failed to create sequential agent: %v", err)
	}
	log.Printf("Created sequential workflow agent: %s", seqAgent.Name())

	pipelineAgent, err := newProcessPipeline()
	if err != nil {
		log.Fatalf("Failed to create process pipeline: %v", err)
	}
	log.Printf("Created process pipeline agent: %s", pipelineAgent.Name())
}
