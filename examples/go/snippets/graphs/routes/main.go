//go:build ignore

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

// Package main demonstrates graph routing patterns in ADK Go v2.
//
// NOTE: This file requires google.golang.org/adk/v2 (the workflow package),
// available in ADK Go v2.0.0 and later. It carries //go:build ignore so it is
// excluded from the current examples/go module (which is still on the v1 path)
// until examples/go is migrated to google.golang.org/adk/v2 at the v2.0.0
// release.
//
// # Routing patterns in ADK Go v2
//
// ADK Go v2.0.0 provides two complementary approaches to graph routing:
//
// ## workflow package (graph engine)
//
// workflow.NewFunctionNode, workflow.NewAgentNode, and workflow.NewDynamicNode
// create nodes that communicate through session.Event fields — mirroring the
// Python Workflow(edges=[...]) API closely:
//
//   - workflow.Chain(workflow.Start, nodeA, nodeB) — sequential edges
//   - workflow.Concat + []workflow.Edge{...} — conditional branching
//   - workflow.NewEdgeBuilder with AddFanOut/AddFanIn — fan-out/join
//   - workflow.NewJoinNode — barrier that waits for all predecessors
//
// ## Prebuilt workflow agents
//
// sequentialagent, parallelagent, and loopagent are higher-level wrappers
// for the three most common topologies. They communicate through session state
// (llmagent.Config.OutputKey / ctx.Session().State().Set / {key} in Instruction).
//
// This file contains five snippet regions used in docs/graphs/routes.md:
//
//	function-node       – workflow.NewFunctionNode as a graph node (v2 graph engine)
//	sequential-nodes    – sequential route using the prebuilt sequentialagent
//	parallel-fan-out    – parallel fan-out using the prebuilt parallelagent + sequentialagent
//	nested-workflows    – nested sequentialagent inside another sequentialagent
//	loop-escalate       – loopagent with Escalate-based exit (prebuilt tier)
package main

import (
	"context"
	"fmt"
	"log"
	"strings"

	"google.golang.org/genai"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/llmagent"
	"google.golang.org/adk/v2/agent/workflowagent"
	"google.golang.org/adk/v2/agent/workflowagents/loopagent"
	"google.golang.org/adk/v2/agent/workflowagents/parallelagent"
	"google.golang.org/adk/v2/agent/workflowagents/sequentialagent"
	"google.golang.org/adk/v2/model/gemini"
	"google.golang.org/adk/v2/tool"
	"google.golang.org/adk/v2/tool/functiontool"
	"google.golang.org/adk/v2/workflow"
)

const modelName = "gemini-flash-latest"

// --8<-- [start:function-node]
// newFunctionNodePipeline demonstrates workflow.NewFunctionNode as the primary
// v2 node type. A FunctionNode wraps a plain Go function: the function returns
// a typed value, and the framework automatically wraps it in a session.Event,
// setting event.Output. The successor node receives this value as its typed
// input parameter.
//
// This is the direct Go equivalent of the Python FunctionNode:
//
//	def my_function_node(node_input: str):
//	    return Event(output=node_input.upper())
func newFunctionNodePipeline() (agent.Agent, error) {
	upperFn := func(_ agent.Context, input string) (string, error) {
		return strings.ToUpper(input), nil
	}

	suffixFn := func(_ agent.Context, input string) (string, error) {
		return input + " IS AWESOME!", nil
	}

	// workflow.NewFunctionNode wraps the function as a graph node.
	// workflow.Chain wires them in order: START → upper → suffix.
	// The output of upperFn is delivered as the typed input of suffixFn
	// via event.Output — no session state writes are needed.
	nodeA := workflow.NewFunctionNode("upper", upperFn, workflow.NodeConfig{})
	nodeB := workflow.NewFunctionNode("suffix", suffixFn, workflow.NodeConfig{})

	return workflowagent.New(workflowagent.Config{
		Name:        "function_node_pipeline",
		Description: "Demonstrates workflow.NewFunctionNode data flow via Event.Output.",
		Edges:       workflow.Chain(workflow.Start, nodeA, nodeB),
	})
}

// --8<-- [end:function-node]

// --8<-- [start:sequential-nodes]
// newSequentialNodes builds a two-step pipeline using the prebuilt
// sequentialagent. This is an alternative to the workflow graph engine for
// simple sequential topologies.
//
// The sequentialagent runs each SubAgent once, in the listed order. Data flows
// through session state: step A writes to OutputKey, step B reads it via {key}
// in its Instruction template.
//
// workflow.Chain equivalent:
//
//	edges=[("START", task_A_node, task_B_node)]
func newSequentialNodes(ctx context.Context) (agent.Agent, error) {
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("gemini.NewModel: %w", err)
	}

	taskA, err := llmagent.New(llmagent.Config{
		Name:        "task_A_agent",
		Model:       geminiModel,
		Description: "Performs task A.",
		Instruction: "Summarise the user request in one sentence.",
		OutputKey:   "task_a_result",
	})
	if err != nil {
		return nil, fmt.Errorf("taskA: %w", err)
	}

	taskB, err := llmagent.New(llmagent.Config{
		Name:        "task_B_agent",
		Model:       geminiModel,
		Description: "Performs task B using task A output.",
		Instruction: "Translate this summary into French: {task_a_result}",
	})
	if err != nil {
		return nil, fmt.Errorf("taskB: %w", err)
	}

	return sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        "sequential_workflow",
			Description: "Runs task A then task B in order.",
			SubAgents:   []agent.Agent{taskA, taskB},
		},
	})
}

// --8<-- [end:sequential-nodes]

// --8<-- [start:parallel-fan-out]
// newParallelFanOut builds a fan-out / join pipeline using the prebuilt
// parallelagent and sequentialagent. This is the prebuilt-agent alternative
// to workflow.NewJoinNode + EdgeBuilder.AddFanOut/AddFanIn.
//
// parallelagent runs researchA, researchB, and researchC concurrently; each
// writes its output to a distinct session state key via OutputKey. The
// enclosing sequentialagent then runs synthesisAgent, which reads all three
// keys via {result_A}, {result_B}, {result_C} in its Instruction.
func newParallelFanOut(ctx context.Context) (agent.Agent, error) {
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("gemini.NewModel: %w", err)
	}

	researchA, err := llmagent.New(llmagent.Config{
		Name:        "research_agent_A",
		Model:       geminiModel,
		Description: "Researches topic A.",
		Instruction: "Give a 1-sentence fact about renewable energy.",
		OutputKey:   "result_A",
	})
	if err != nil {
		return nil, fmt.Errorf("researchA: %w", err)
	}

	researchB, err := llmagent.New(llmagent.Config{
		Name:        "research_agent_B",
		Model:       geminiModel,
		Description: "Researches topic B.",
		Instruction: "Give a 1-sentence fact about electric vehicles.",
		OutputKey:   "result_B",
	})
	if err != nil {
		return nil, fmt.Errorf("researchB: %w", err)
	}

	researchC, err := llmagent.New(llmagent.Config{
		Name:        "research_agent_C",
		Model:       geminiModel,
		Description: "Researches topic C.",
		Instruction: "Give a 1-sentence fact about carbon capture.",
		OutputKey:   "result_C",
	})
	if err != nil {
		return nil, fmt.Errorf("researchC: %w", err)
	}

	parallelResearch, err := parallelagent.New(parallelagent.Config{
		AgentConfig: agent.Config{
			Name:        "parallel_research",
			Description: "Runs three research agents in parallel.",
			SubAgents:   []agent.Agent{researchA, researchB, researchC},
		},
	})
	if err != nil {
		return nil, fmt.Errorf("parallelagent: %w", err)
	}

	synthesisAgent, err := llmagent.New(llmagent.Config{
		Name:  "synthesis_agent",
		Model: geminiModel,
		Instruction: `Combine the following research results into one paragraph:
A: {result_A}
B: {result_B}
C: {result_C}`,
		Description: "Synthesises outputs from the parallel research agents.",
	})
	if err != nil {
		return nil, fmt.Errorf("synthesisAgent: %w", err)
	}

	// The top-level sequentialagent guarantees synthesis only starts after
	// all parallel branches have completed.
	return sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        "fan_out_workflow",
			Description: "Parallel research followed by synthesis.",
			SubAgents:   []agent.Agent{parallelResearch, synthesisAgent},
		},
	})
}

// --8<-- [end:parallel-fan-out]

// --8<-- [start:nested-workflows]
// newNestedWorkflows shows how to use one prebuilt workflow agent as a
// sub-agent of another — the prebuilt-agent approach to nested workflows.
//
// For the workflow graph engine alternative, wrap a workflowagent with
// workflow.NewAgentNode and place it as a node in the outer graph's edges:
//
//	innerNode, _ := workflow.NewAgentNode(innerWorkflowAgent, workflow.NodeConfig{})
//	edges := workflow.Chain(workflow.Start, outerStep, innerNode, finalNode)
func newNestedWorkflows(ctx context.Context) (agent.Agent, error) {
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("gemini.NewModel: %w", err)
	}

	innerStep1, err := llmagent.New(llmagent.Config{
		Name:        "inner_step_1",
		Model:       geminiModel,
		Description: "First step of the inner workflow.",
		Instruction: "Translate the user's request into Spanish.",
		OutputKey:   "spanish_text",
	})
	if err != nil {
		return nil, fmt.Errorf("innerStep1: %w", err)
	}

	innerStep2, err := llmagent.New(llmagent.Config{
		Name:        "inner_step_2",
		Model:       geminiModel,
		Description: "Second step of the inner workflow.",
		Instruction: "Now translate this Spanish text back into English: {spanish_text}",
	})
	if err != nil {
		return nil, fmt.Errorf("innerStep2: %w", err)
	}

	workflowB, err := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        "workflow_B",
			Description: "Translates to Spanish then back to English.",
			SubAgents:   []agent.Agent{innerStep1, innerStep2},
		},
	})
	if err != nil {
		return nil, fmt.Errorf("workflowB: %w", err)
	}

	taskA1, err := llmagent.New(llmagent.Config{
		Name:        "task_A1",
		Model:       geminiModel,
		Description: "Prepares the input for the nested workflow.",
		Instruction: "Summarise the user request in one sentence.",
		OutputKey:   "task_a1_result",
	})
	if err != nil {
		return nil, fmt.Errorf("taskA1: %w", err)
	}

	return sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        "parent_workflow",
			Description: "Runs a pre-processing step then a nested workflow.",
			SubAgents:   []agent.Agent{taskA1, workflowB},
		},
	})
}

// --8<-- [end:nested-workflows]

// --8<-- [start:loop-escalate]
// ExitLoopArgs is the (empty) input struct for the exitLoop tool.
type ExitLoopArgs struct{}

// ExitLoopResults is the (empty) output struct for the exitLoop tool.
type ExitLoopResults struct{}

// exitLoop signals the loopagent to stop by setting Escalate = true on the
// current event's actions. The tool function receives agent.Context, which
// is the unified context type in ADK Go v2.
func exitLoop(ctx agent.Context, _ ExitLoopArgs) (ExitLoopResults, error) {
	ctx.Actions().Escalate = true
	return ExitLoopResults{}, nil
}

// newLoopEscalate builds a workflow that iteratively refines a document and
// exits when the critic is satisfied. This uses the prebuilt loopagent.
//
// For the workflow graph engine alternative, create a back-edge from the
// refiner node back to the critic node using []workflow.Edge.
func newLoopEscalate(ctx context.Context) (agent.Agent, error) {
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("gemini.NewModel: %w", err)
	}

	const (
		stateDoc   = "current_draft"
		stateCrit  = "criticism"
		donePhrase = "No major issues found."
	)

	exitLoopTool, err := functiontool.New(
		functiontool.Config{
			Name:        "exitLoop",
			Description: "Call this tool ONLY when the critique says the document needs no further changes.",
		},
		exitLoop,
	)
	if err != nil {
		return nil, fmt.Errorf("functiontool.New: %w", err)
	}

	criticAgent, err := llmagent.New(llmagent.Config{
		Name:        "critic_agent",
		Model:       geminiModel,
		Description: "Reviews the draft and suggests improvements, or signals completion.",
		Instruction: fmt.Sprintf(`Review this draft:
"""{%s}"""
If it needs improvement, provide 1-2 specific suggestions.
If it is good enough, respond exactly with: "%s"`, stateDoc, donePhrase),
		OutputKey: stateCrit,
	})
	if err != nil {
		return nil, fmt.Errorf("criticAgent: %w", err)
	}

	refinerAgent, err := llmagent.New(llmagent.Config{
		Name:        "refiner_agent",
		Model:       geminiModel,
		Description: "Refines the draft or exits the loop when the critique signals completion.",
		Instruction: fmt.Sprintf(`Current draft:
"""{%s}"""
Critique: {%s}

If the critique is exactly "%s", call the exitLoop tool.
Otherwise apply the suggestions and output the improved draft.`, stateDoc, stateCrit, donePhrase),
		Tools:     []tool.Tool{exitLoopTool},
		OutputKey: stateDoc,
	})
	if err != nil {
		return nil, fmt.Errorf("refinerAgent: %w", err)
	}

	// loopagent repeatedly runs [criticAgent → refinerAgent] until either
	// refinerAgent calls exitLoop (Escalate = true) or MaxIterations is reached.
	refinementLoop, err := loopagent.New(loopagent.Config{
		MaxIterations: 5,
		AgentConfig: agent.Config{
			Name:        "refinement_loop",
			Description: "Iteratively refines the draft until the critic is satisfied.",
			SubAgents:   []agent.Agent{criticAgent, refinerAgent},
		},
	})
	if err != nil {
		return nil, fmt.Errorf("loopagent: %w", err)
	}

	initialWriterAgent, err := llmagent.New(llmagent.Config{
		Name:        "initial_writer_agent",
		Model:       geminiModel,
		Description: "Writes the first draft.",
		Instruction: "Write a 2-3 sentence draft about the user's topic.",
		OutputKey:   stateDoc,
	})
	if err != nil {
		return nil, fmt.Errorf("initialWriterAgent: %w", err)
	}

	return sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        "iterative_writer",
			Description: "Writes then iteratively refines a document.",
			SubAgents:   []agent.Agent{initialWriterAgent, refinementLoop},
		},
	})
}

// --8<-- [end:loop-escalate]

func main() {
	ctx := context.Background()

	fnPipeline, err := newFunctionNodePipeline()
	if err != nil {
		log.Fatalf("newFunctionNodePipeline: %v", err)
	}
	log.Printf("created %s", fnPipeline.Name())

	seqAgent, err := newSequentialNodes(ctx)
	if err != nil {
		log.Fatalf("newSequentialNodes: %v", err)
	}
	log.Printf("created %s", seqAgent.Name())

	parallelAgent, err := newParallelFanOut(ctx)
	if err != nil {
		log.Fatalf("newParallelFanOut: %v", err)
	}
	log.Printf("created %s", parallelAgent.Name())

	nestedAgent, err := newNestedWorkflows(ctx)
	if err != nil {
		log.Fatalf("newNestedWorkflows: %v", err)
	}
	log.Printf("created %s", nestedAgent.Name())

	loopAgent, err := newLoopEscalate(ctx)
	if err != nil {
		log.Fatalf("newLoopEscalate: %v", err)
	}
	log.Printf("created %s", loopAgent.Name())
}
