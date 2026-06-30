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

// Package main provides snippet examples for graph-based workflow agents in ADK Go v2.
//
// NOTE: This file requires google.golang.org/adk/v2 (the workflow package),
// available in ADK Go v2.0.0 and later.
//
// Both snippets use the v2 graph engine (workflow.NewFunctionNode +
// workflowagent.New) rather than the prebuilt workflow agents from v1.x.
// This mirrors the Python Workflow(edges=[...]) API directly:
//
//   - workflow.Chain(workflow.Start, nodeA, nodeB) — sequential edges
//   - workflow.NewEmittingFunctionNode + ev.Routes + []workflow.Edge — routing
//   - workflow.StringRoute("category") — conditional edge matcher
package main

import (
	"fmt"
	"log"
	"strings"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/workflowagent"
	"google.golang.org/adk/v2/session"
	"google.golang.org/adk/v2/workflow"
)

// --8<-- [start:sequential-get-started]
// cityTime holds the data passed from the lookup step to the report step.
type cityTime struct {
	City     string
	TimeInfo string
}

// newSequentialGetStarted builds a three-node sequential workflow using the
// v2 graph engine. Each node is a workflow.NewFunctionNode whose return value
// is automatically wrapped in session.Event.Output and forwarded to the next
// node as its typed input.
//
// This is the Go equivalent of the Python Workflow example:
//
//	root_agent = Workflow(
//	    name="root_agent",
//	    edges=[("START", city_generator_agent, lookup_time_function,
//	             city_report_agent, completed_message_function)],
//	)
func newSequentialGetStarted() (agent.Agent, error) {
	// Step 1: return a city name. The string is set as event.Output and
	// becomes the typed input of the next node.
	cityGeneratorNode := workflow.NewFunctionNode("city_generator_agent",
		func(_ agent.Context, _ any) (string, error) {
			return "Tokyo", nil
		},
		workflow.NodeConfig{},
	)

	// Step 2: receive the city name and return structured time data.
	lookupTimeNode := workflow.NewFunctionNode("lookup_time_function",
		func(_ agent.Context, city string) (cityTime, error) {
			return cityTime{City: city, TimeInfo: "10:10 AM"}, nil
		},
		workflow.NodeConfig{},
	)

	// Step 3: receive the cityTime struct and produce the final report string.
	cityReportNode := workflow.NewFunctionNode("city_report_agent",
		func(_ agent.Context, ct cityTime) (string, error) {
			return fmt.Sprintf("It is %s in %s right now.\nWORKFLOW COMPLETED.",
				ct.TimeInfo, ct.City), nil
		},
		workflow.NodeConfig{},
	)

	// workflow.Chain wires START → cityGeneratorNode → lookupTimeNode → cityReportNode.
	// Data flows through event.Output: no session state writes needed.
	return workflowagent.New(workflowagent.Config{
		Name:        "root_agent",
		Description: "Sequential workflow: generate city → look up time → report.",
		Edges:       workflow.Chain(workflow.Start, cityGeneratorNode, lookupTimeNode, cityReportNode),
	})
}

// --8<-- [end:sequential-get-started]

// --8<-- [start:process-pipeline]
// classifyMessage is the router node. It emits ev.Routes to select which
// branch to follow — the Go equivalent of Python's:
//
//	def router(node_input: str):
//	    return Event(route=["BUG"])
func classifyMessage(ctx agent.Context, msg string, emit func(*session.Event) error) (any, error) {
	// In a real workflow this step calls an LLM; here we classify by keyword.
	category := "LOGISTICS"
	lower := strings.ToLower(msg)
	switch {
	case strings.Contains(lower, "bug") || strings.Contains(lower, "error"):
		category = "BUG"
	case strings.Contains(lower, "help") || strings.Contains(lower, "support"):
		category = "CUSTOMER_SUPPORT"
	}

	ev := session.NewEvent(ctx, ctx.InvocationID())
	ev.Routes = []string{category} // drives edge dispatch
	ev.Output = msg                // forward original message to the chosen handler
	if err := emit(ev); err != nil {
		return nil, err
	}
	return nil, nil // nil suppresses the automatic terminal event
}

// newProcessPipeline builds a classification + conditional-routing workflow
// using the v2 graph engine. The classifyMessage emitting node sets
// ev.Routes, and the graph engine dispatches to the matching handler via
// workflow.StringRoute.
//
// This is the Go equivalent of the Python Workflow example:
//
//	root_agent = Workflow(
//	    name="routing_workflow",
//	    edges=[
//	        ("START", process_message, router),
//	        (router, {
//	            "BUG": response_1_bug,
//	            "CUSTOMER_SUPPORT": response_2_support,
//	            "LOGISTICS": response_3_logistics,
//	        }),
//	    ],
//	)
func newProcessPipeline() (agent.Agent, error) {
	classifyNode := workflow.NewEmittingFunctionNode(
		"process_message", classifyMessage, workflow.NodeConfig{},
	)

	bugNode := workflow.NewFunctionNode("response_1_bug",
		func(_ agent.Context, _ any) (string, error) {
			return "Handling bug...", nil
		},
		workflow.NodeConfig{},
	)

	supportNode := workflow.NewFunctionNode("response_2_support",
		func(_ agent.Context, _ any) (string, error) {
			return "Handling customer support...", nil
		},
		workflow.NodeConfig{},
	)

	logisticsNode := workflow.NewFunctionNode("response_3_logistics",
		func(_ agent.Context, _ any) (string, error) {
			return "Handling logistics...", nil
		},
		workflow.NodeConfig{},
	)

	// workflow.Concat merges the sequential chain with the conditional edges.
	// Each workflow.Edge carries a workflow.StringRoute matcher that the engine
	// checks against ev.Routes emitted by classifyNode.
	edges := workflow.Concat(
		workflow.Chain(workflow.Start, classifyNode),
		[]workflow.Edge{
			{From: classifyNode, To: bugNode, Route: workflow.StringRoute("BUG")},
			{From: classifyNode, To: supportNode, Route: workflow.StringRoute("CUSTOMER_SUPPORT")},
			{From: classifyNode, To: logisticsNode, Route: workflow.StringRoute("LOGISTICS")},
		},
	)

	return workflowagent.New(workflowagent.Config{
		Name:        "routing_workflow",
		Description: "Classifies a message and routes it to the appropriate handler.",
		Edges:       edges,
	})
}

// --8<-- [end:process-pipeline]

func main() {
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
