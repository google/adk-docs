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

// Package main demonstrates graph routing patterns in ADK Go.
//
// In ADK Go, workflow graphs are expressed through three composable workflow
// agent types rather than an edges-array DSL:
//
//   - [sequentialagent] – runs sub-agents one after another in the listed order.
//   - [parallelagent]   – runs sub-agents concurrently in isolated branches.
//   - [loopagent]       – repeatedly runs sub-agents until MaxIterations is
//     reached or any sub-agent sets EventActions.Escalate = true.
//
// Data flows between steps via session state: an agent writes its output to a
// named key using llmagent.Config.OutputKey, and downstream agents read it by
// referencing {key} in their Instruction template.
//
// This file contains four snippet regions used in docs/graphs/routes.md:
//
//	sequential-nodes    – route sequences (one or more nodes in order)
//	function-node       – custom Run function as a workflow step
//	parallel-fan-out    – parallel fan-out collected by a synthesis agent
//	nested-workflows    – workflow agent nested inside another workflow agent
//	loop-escalate       – loop with Escalate-based exit (conditional routing)
package main

import (
	"context"
	"fmt"
	"iter"
	"log"
	"strings"

	"google.golang.org/genai"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/agent/workflowagents/loopagent"
	"google.golang.org/adk/agent/workflowagents/parallelagent"
	"google.golang.org/adk/agent/workflowagents/sequentialagent"
	"google.golang.org/adk/model"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"
)

const modelName = "gemini-flash-latest"

// --8<-- [start:function-node]
// upperCaseRun is a custom Run function that acts as a workflow step (node).
// It reads the user content, transforms it, writes to state, and yields an
// event — equivalent to a Python FunctionNode that returns Event(output=...).
func upperCaseRun(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
	return func(yield func(*session.Event, error) bool) {
		var inputText string
		if ctx.UserContent() != nil {
			for _, p := range ctx.UserContent().Parts {
				inputText += p.Text
			}
		}
		result := strings.ToUpper(inputText)

		if err := ctx.Session().State().Set("upper_result", result); err != nil {
			yield(nil, fmt.Errorf("state.Set: %w", err))
			return
		}
		yield(&session.Event{
			LLMResponse: model.LLMResponse{
				Content: &genai.Content{
					Parts: []*genai.Part{{Text: result}},
				},
			},
		}, nil)
	}
}

// --8<-- [end:function-node]

// --8<-- [start:sequential-nodes]
// newSequentialNodes builds a two-step sequential workflow.
// It is the Go equivalent of:
//
//	edges=[("START", task_A_node, task_B_node)]
//
// The sequentialagent runs each SubAgent once, in the listed order.
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
// newParallelFanOut builds a workflow that fans out across three parallel
// research agents and then re-joins by passing their OutputKey results into
// a single synthesis agent via session state — the Go equivalent of using a
// JoinNode followed by a final task.
//
// Python equivalent:
//
//	edges=[
//	    ("START", research_A, join_node),
//	    ("START", research_B, join_node),
//	    ("START", research_C, join_node),
//	    (join_node, synthesis_agent),
//	]
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

	// parallelagent runs researchA, researchB, and researchC concurrently.
	// Each agent writes its output to a distinct key in session state.
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

	// synthesisAgent reads all three results from state and produces a report.
	// This is the "join" step: it only runs after parallelResearch completes.
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

	// The top-level sequentialagent guarantees that synthesis only starts
	// after all parallel branches have completed.
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
// newNestedWorkflows shows how to use one workflow agent as a sub-agent of
// another — the Go equivalent of nesting Workflow objects as nodes.
//
// Python equivalent:
//
//	root_agent = Workflow(
//	    name="parent_workflow",
//	    edges=[("START", task_A1, nested_workflow_B)],
//	)
func newNestedWorkflows(ctx context.Context) (agent.Agent, error) {
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("gemini.NewModel: %w", err)
	}

	// --- Inner workflow B ---
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

	// workflowB is a self-contained sequential workflow used as a sub-agent.
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

	// --- Outer step that runs before workflowB ---
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

	// parentWorkflow runs taskA1, then hands off to workflowB as a single node.
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
// current event's actions. This is the Go equivalent of routing to an exit
// node in a Python conditional-branch graph.
func exitLoop(ctx agent.Context, _ ExitLoopArgs) (ExitLoopResults, error) {
	ctx.Actions().Escalate = true
	return ExitLoopResults{}, nil
}

// newLoopEscalate builds a workflow that iteratively refines a document and
// exits the loop when the critic is satisfied.
//
// Python equivalent of the conditional routing pattern:
//
//	edges=[
//	    ("START", critic_node, router),
//	    (router, {"DONE": exit_node, "REFINE": refiner_node}),
//	    (refiner_node, critic_node),  # loop back
//	]
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

	// criticAgent reviews the current draft and either provides feedback or
	// writes donePhrase when no further changes are needed.
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

	// refinerAgent applies the critique or calls exitLoop if done.
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

	// initialWriterAgent produces the first draft before the loop starts.
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

	// The top-level sequentialagent runs the writer once, then hands off to
	// the loop, which runs until escalation or max iterations.
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

	// Demonstrate that the function-node custom Run can be wrapped in an agent.
	funcNode, err := agent.New(agent.Config{
		Name:        "upper_case_node",
		Description: "Transforms input to upper case.",
		Run:         upperCaseRun,
	})
	if err != nil {
		log.Fatalf("agent.New (function-node): %v", err)
	}
	log.Printf("created %s", funcNode.Name())
}
