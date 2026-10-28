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

// Package main demonstrates graph routing patterns in ADK Go v2 using the
// graph engine: workflow.NewFunctionNode, workflow.NewAgentNode, workflow.Chain,
// workflow.Concat, workflow.NewEdgeBuilder, workflow.NewJoinNode, and
// workflowagent.New.
//
// NOTE: This file requires google.golang.org/adk/v2 (the workflow package),
// available in ADK Go v2.0.0 and higher.
//
// This file contains five snippet regions used in docs/graphs/routes.md:
//
//	function-node       – workflow.NewFunctionNode as a graph node
//	sequential-nodes    – sequential route using workflow.Chain
//	parallel-fan-out    – fan-out/join using workflow.NewJoinNode + EdgeBuilder
//	nested-workflows    – inner workflowagent wrapped as workflow.NewAgentNode
//	loop-escalate       – back-edge loop using workflow.EdgeBuilder.AddRoute
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

	// workflow.NewFunctionNode wraps each function as a graph node.
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
// newSequentialNodes builds a two-step sequential workflow using the v2 graph
// engine. workflow.Chain wires the nodes in order; each node's typed return
// value is forwarded to the next node via event.Output.
//
// This is the Go equivalent of:
//
//	edges=[("START", task_A_node, task_B_node)]
func newSequentialNodes() (agent.Agent, error) {
	// task_A_node: transforms the user's input.
	taskANode := workflow.NewFunctionNode("task_A_node",
		func(_ agent.Context, input string) (string, error) {
			return "Summary: " + strings.TrimSpace(input), nil
		},
		workflow.NodeConfig{},
	)

	// task_B_node: receives task A's output as its typed input and produces
	// the final result. No session state reads needed.
	taskBNode := workflow.NewFunctionNode("task_B_node",
		func(_ agent.Context, summary string) (string, error) {
			return strings.ToUpper(summary), nil
		},
		workflow.NodeConfig{},
	)

	return workflowagent.New(workflowagent.Config{
		Name:        "sequential_workflow",
		Description: "Runs task A then task B in order via workflow.Chain.",
		Edges:       workflow.Chain(workflow.Start, taskANode, taskBNode),
	})
}

// --8<-- [end:sequential-nodes]

// --8<-- [start:parallel-fan-out]
// newParallelFanOut builds a fan-out / join workflow using the v2 graph engine.
// Three research nodes run in parallel from Start; workflow.NewJoinNode waits
// for all of them to complete and emits a map[nodeName]output to the format
// node, which assembles the results for a synthesis node.
//
// Graph topology:
//
//	START ─┬─> research_A ──┐
//	       ├─> research_B ──┼─> gather (JoinNode) ─> format ─> synthesis
//	       └─> research_C ──┘
//
// Python equivalent:
//
//	edges=[
//	    ("START", research_A, my_join_node),
//	    ("START", research_B, my_join_node),
//	    ("START", research_C, my_join_node),
//	    (my_join_node, format_node),
//	    (format_node, synthesis_node),
//	]
func newParallelFanOut() (agent.Agent, error) {
	researchA := workflow.NewFunctionNode("research_A",
		func(_ agent.Context, _ any) (string, error) {
			return "Fact about renewable energy.", nil
		},
		workflow.NodeConfig{},
	)
	researchB := workflow.NewFunctionNode("research_B",
		func(_ agent.Context, _ any) (string, error) {
			return "Fact about electric vehicles.", nil
		},
		workflow.NodeConfig{},
	)
	researchC := workflow.NewFunctionNode("research_C",
		func(_ agent.Context, _ any) (string, error) {
			return "Fact about carbon capture.", nil
		},
		workflow.NodeConfig{},
	)

	// workflow.NewJoinNode waits for all predecessors (research_A, research_B,
	// research_C) to complete and emits a map[nodeName]output to its successor.
	gatherNode := workflow.NewJoinNode("gather")

	// formatNode receives map[string]any from gatherNode and assembles a
	// combined prompt string.
	formatNode := workflow.NewFunctionNode("format",
		func(_ agent.Context, results map[string]any) (string, error) {
			return fmt.Sprintf("A: %v\nB: %v\nC: %v",
				results["research_A"],
				results["research_B"],
				results["research_C"],
			), nil
		},
		workflow.NodeConfig{},
	)

	synthesisNode := workflow.NewFunctionNode("synthesis",
		func(_ agent.Context, prompt string) (string, error) {
			return "Combined report: " + prompt, nil
		},
		workflow.NodeConfig{},
	)

	// EdgeBuilder.AddFanOut fans workflow.Start out to all three research nodes.
	// EdgeBuilder.AddFanIn routes all three research nodes into gatherNode.
	eb := workflow.NewEdgeBuilder()
	eb.AddFanOut(workflow.Start, researchA, researchB, researchC)
	eb.AddFanIn(gatherNode, researchA, researchB, researchC)
	eb.Add(gatherNode, formatNode)
	eb.Add(formatNode, synthesisNode)

	return workflowagent.New(workflowagent.Config{
		Name:        "fan_out_workflow",
		Description: "Parallel research fan-out with JoinNode barrier and synthesis.",
		Edges:       eb.Build(),
	})
}

// --8<-- [end:parallel-fan-out]

// --8<-- [start:nested-workflows]
// newNestedWorkflows shows how to nest one workflowagent inside another using
// the v2 graph engine. The inner workflowagent is wrapped with
// workflow.NewAgentNode and placed as a node in the outer graph's edge slice.
// From the outer graph's perspective the inner workflow is a single node that
// runs to completion before the edge to finalNode is followed.
//
// Python equivalent:
//
//	root_agent = Workflow(
//	    name="parent_workflow",
//	    edges=[("START", task_A1, workflow_B, final_node)],
//	)
func newNestedWorkflows() (agent.Agent, error) {
	// --- Inner workflow B ---
	innerStep1 := workflow.NewFunctionNode("inner_step_1",
		func(_ agent.Context, input string) (string, error) {
			return "[ES] " + input, nil // simulate translation to Spanish
		},
		workflow.NodeConfig{},
	)
	innerStep2 := workflow.NewFunctionNode("inner_step_2",
		func(_ agent.Context, spanish string) (string, error) {
			return "[EN] " + spanish, nil // simulate translation back to English
		},
		workflow.NodeConfig{},
	)

	// workflowB is a self-contained inner graph.
	workflowB, err := workflowagent.New(workflowagent.Config{
		Name:        "workflow_B",
		Description: "Translates input to Spanish then back to English.",
		Edges:       workflow.Chain(workflow.Start, innerStep1, innerStep2),
	})
	if err != nil {
		return nil, fmt.Errorf("workflowB: %w", err)
	}

	// --- Outer graph ---
	taskA1 := workflow.NewFunctionNode("task_A1",
		func(_ agent.Context, input string) (string, error) {
			return "Summary: " + strings.TrimSpace(input), nil
		},
		workflow.NodeConfig{},
	)

	finalNode := workflow.NewFunctionNode("final_node",
		func(_ agent.Context, result string) (string, error) {
			return "Final: " + result, nil
		},
		workflow.NodeConfig{},
	)

	// workflow.NewAgentNode wraps workflowB so it can be placed as a node
	// in the outer graph's edges slice.
	innerNode, err := workflow.NewAgentNode(workflowB, workflow.NodeConfig{})
	if err != nil {
		return nil, fmt.Errorf("NewAgentNode(workflowB): %w", err)
	}

	return workflowagent.New(workflowagent.Config{
		Name:        "parent_workflow",
		Description: "Runs task_A1 then the nested workflow_B then final_node.",
		Edges:       workflow.Chain(workflow.Start, taskA1, innerNode, finalNode),
		SubAgents:   []agent.Agent{workflowB},
	})
}

// --8<-- [end:nested-workflows]

// --8<-- [start:loop-escalate]
// draft carries the working document through the refinement loop.
type draft struct {
	Text string `json:"text"`
}

// criticResult is emitted by the critic node with the review verdict and
// optional suggestions. The router reads Verdict to set Event.Routes.
type criticResult struct {
	Verdict     string `json:"verdict"`     // "REFINE" or "DONE"
	Suggestions string `json:"suggestions"` // non-empty when Verdict == "REFINE"
}

// writeDraft is the initial writer node: produces the first draft from the
// user's topic. Its typed return value becomes the input to the critic node
// via Event.Output — no session state writes needed.
func writeDraft(_ agent.Context, topic string) (draft, error) {
	// In a real workflow this would call an LLM; here we return a stub.
	return draft{Text: "Draft about " + topic + ": placeholder content."}, nil
}

// reviewDraft is the critic node: inspects the draft and returns a verdict.
// "DONE" exits the loop; "REFINE" triggers a back-edge to the refiner.
func reviewDraft(_ agent.Context, d draft) (criticResult, error) {
	// Simulate a critic: approve once the draft contains "improved".
	if strings.Contains(d.Text, "improved") {
		return criticResult{Verdict: "DONE"}, nil
	}
	return criticResult{
		Verdict:     "REFINE",
		Suggestions: "Add more detail and mark the text as improved.",
	}, nil
}

// routeVerdict reads the critic's verdict and sets Event.Routes so the
// graph engine dispatches to either the refiner or the done node.
// Returning nil suppresses the automatic terminal event.
func routeVerdict(ctx agent.Context, r criticResult, emit func(*session.Event) error) (any, error) {
	ev := session.NewEvent(ctx, ctx.InvocationID())
	ev.Routes = []string{r.Verdict}
	ev.Output = r // forward the full result to the chosen successor
	if err := emit(ev); err != nil {
		return nil, err
	}
	return nil, nil
}

// refineDraft applies the critic's suggestions and returns the improved draft.
// Its output feeds back to the critic node via the back-edge.
func refineDraft(_ agent.Context, r criticResult) (draft, error) {
	return draft{Text: "improved draft incorporating: " + r.Suggestions}, nil
}

// reportDone is the terminal node, reached only when the critic is satisfied.
func reportDone(_ agent.Context, r criticResult) (string, error) {
	return "Refinement complete. Final verdict: " + r.Verdict, nil
}

// newLoopEscalate builds an iterative document-refinement workflow using the
// graph engine. The critic node emits a route ("REFINE" or "DONE") and the
// engine dispatches to either the refiner (which loops back to the critic via
// a back-edge) or the terminal done node.
//
// Graph topology:
//
//	START → writer → critic → router ─┬─ "REFINE" → refiner ──┐
//	                                   └─ "DONE"   → done       │
//	                 ▲_______________________________┘ (back-edge)
//
// Python equivalent:
//
//	edges=[
//	    ("START", writer_node, critic_node, router),
//	    (router, {"REFINE": refiner_node, "DONE": done_node}),
//	    (refiner_node, critic_node),  # back-edge creates the loop
//	]
func newLoopEscalate() (agent.Agent, error) {
	writerNode := workflow.NewFunctionNode("writer", writeDraft, workflow.NodeConfig{})
	criticNode := workflow.NewFunctionNode("critic", reviewDraft, workflow.NodeConfig{})
	routerNode := workflow.NewEmittingFunctionNode("router", routeVerdict, workflow.NodeConfig{})
	refinerNode := workflow.NewFunctionNode("refiner", refineDraft, workflow.NodeConfig{})
	doneNode := workflow.NewFunctionNode("done", reportDone, workflow.NodeConfig{})

	// Build the edges. The back-edge from refinerNode to criticNode creates
	// the loop; the graph engine re-activates criticNode with a fresh
	// lifecycle on each iteration.
	eb := workflow.NewEdgeBuilder()
	eb.Add(workflow.Start, writerNode)
	eb.Add(writerNode, criticNode)
	eb.Add(criticNode, routerNode)
	eb.AddRoute(routerNode, refinerNode, workflow.StringRoute("REFINE"))
	eb.AddRoute(routerNode, doneNode, workflow.StringRoute("DONE"))
	eb.AddRoute(refinerNode, criticNode, workflow.Default) // back-edge: loop back for another review

	return workflowagent.New(workflowagent.Config{
		Name:        "iterative_writer",
		Description: "Writes then iteratively refines a document using a critic/refiner loop.",
		Edges:       eb.Build(),
	})
}

// --8<-- [end:loop-escalate]

func main() {
	fnPipeline, err := newFunctionNodePipeline()
	if err != nil {
		log.Fatalf("newFunctionNodePipeline: %v", err)
	}
	log.Printf("created %s", fnPipeline.Name())

	seqAgent, err := newSequentialNodes()
	if err != nil {
		log.Fatalf("newSequentialNodes: %v", err)
	}
	log.Printf("created %s", seqAgent.Name())

	parallelAgent, err := newParallelFanOut()
	if err != nil {
		log.Fatalf("newParallelFanOut: %v", err)
	}
	log.Printf("created %s", parallelAgent.Name())

	nestedAgent, err := newNestedWorkflows()
	if err != nil {
		log.Fatalf("newNestedWorkflows: %v", err)
	}
	log.Printf("created %s", nestedAgent.Name())

	loopAgent, err := newLoopEscalate()
	if err != nil {
		log.Fatalf("newLoopEscalate: %v", err)
	}
	log.Printf("created %s", loopAgent.Name())
}
