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

//go:build ignore

// Package main demonstrates dynamic workflow patterns in ADK Go v2.
//
// NOTE: This file requires the google.golang.org/adk/workflow package,
// which is available in ADK Go v2.0.0 and later. The workflow package is
// not present in v1.x releases. The snippets in this file are based on the
// examples found in adk-go/tree/v2/examples/workflow/.
//
// Key types and functions used in this file:
//
//   - workflow.NewFunctionNode[IN, OUT]  – wraps a plain Go function as a workflow node.
//     Equivalent to Python's @node decorator on a regular function.
//
//   - workflow.NewDynamicNode[IN, OUT]   – wraps an orchestrator function that calls
//     workflow.RunNode to schedule child nodes at runtime. Equivalent to
//     Python's @node(rerun_on_resume=True) on an async orchestrator.
//
//   - workflow.RunNode[OUT]              – executes a child node from inside a dynamic
//     node body and returns its typed output. Equivalent to ctx.run_node().
//
//   - workflow.NewAgentNode              – wraps an agent.Agent as a workflow Node so it
//     can be invoked via workflow.RunNode inside a dynamic orchestrator.
//
//   - workflow.NewParallelWorker         – runs a wrapped node concurrently for each
//     item in a list input. Equivalent to asyncio.gather() in Python.
//
//   - workflow.ResumeOrRequestInput      – collapses the re-entry HITL pattern:
//     pauses for input on the first pass and returns the human's reply on
//     resume. Equivalent to yielding RequestInput then checking ctx for reply.
//
//   - workflow.WithRunID                 – option for workflow.RunNode that supplies a
//     stable custom identifier, equivalent to ctx.run_node(..., run_id=...).
//
//   - workflowagent.New                 – creates an agent.Agent backed by a Workflow
//     engine. Use workflow.Chain to build the edges slice.
package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"google.golang.org/genai"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/llmagent"
	"google.golang.org/adk/v2/agent/workflowagent"
	"google.golang.org/adk/v2/cmd/launcher"
	"google.golang.org/adk/v2/cmd/launcher/full"
	"google.golang.org/adk/v2/model/gemini"
	"google.golang.org/adk/v2/session"
	"google.golang.org/adk/v2/workflow"
)

// --8<-- [start:get-started]
// helloNode is a simple FunctionNode that returns "Hello World".
// In Python this would be written as:
//
//	@node(name="hello_node")
//	def my_node(node_input: Any):
//	    return "Hello World"
//
// In Go, workflow.NewFunctionNode wraps the same logic with the
// required node interface, inferring input and output types from
// the generic parameters.
var helloNode = workflow.NewFunctionNode("hello_node",
	func(_ agent.Context, _ string) (string, error) {
		return "Hello World", nil
	},
	workflow.NodeConfig{},
)

// myWorkflow is a dynamic orchestrator node. It calls workflow.RunNode
// to schedule helloNode as a child and returns its output.
// In Python this would be:
//
//	@node(rerun_on_resume=True)
//	async def my_workflow(ctx: Context, node_input: str) -> str:
//	    result = await ctx.run_node(my_node, node_input="hello")
//	    return result
//
// workflow.NewDynamicNode defaults RerunOnResume to &true, matching the
// Python @node(rerun_on_resume=True) behaviour.
var myWorkflow = workflow.NewDynamicNode[string, string]("my_workflow",
	func(ctx agent.Context, _ string, _ func(*session.Event) error) (string, error) {
		return workflow.RunNode[string](ctx, helloNode, "hello")
	},
	workflow.NodeConfig{},
)

func runGetStarted() error {
	ctx := context.Background()

	// workflowagent.New creates an agent.Agent backed by the workflow engine.
	// workflow.Chain(workflow.Start, myWorkflow) produces the edges slice
	// equivalent to Python's edges=[("START", my_workflow)].
	wa, err := workflowagent.New(workflowagent.Config{
		Name:        "root_agent",
		Description: "A minimal dynamic workflow.",
		Edges:       workflow.Chain(workflow.Start, myWorkflow),
	})
	if err != nil {
		return fmt.Errorf("workflowagent.New: %w", err)
	}

	l := full.NewLauncher()
	return l.Execute(ctx, &launcher.Config{
		AgentLoader: agent.NewSingleLoader(wa),
	}, os.Args[1:])
}

// --8<-- [end:get-started]

// --8<-- [start:building-blocks-nodes]
// myFunctionNode demonstrates the explicit NewFunctionNode constructor —
// equivalent to wrapping a function in a FunctionNode manually in Python:
//
//	success_node = FunctionNode(my_function_node, name="hello", rerun_on_resume=True)
//
// Creating the node directly (rather than via @node) is useful when you
// need multiple nodes from the same function with different configurations,
// or when wrapping functions from an external library.
var myFunctionNode = workflow.NewFunctionNode("hello",
	func(_ agent.Context, _ any) (string, error) {
		return "Hello World", nil
	},
	workflow.NodeConfig{},
)

// myFormattingNode is a second function node that the dynamic orchestrator
// calls in sequence, mirroring:
//
//	result_formatted = await ctx.run_node(my_formatting_node, node_input=result)
var myFormattingNode = workflow.NewFunctionNode("format",
	func(_ agent.Context, in string) (string, error) {
		return fmt.Sprintf("[formatted] %s", in), nil
	},
	workflow.NodeConfig{},
)

// --8<-- [end:building-blocks-nodes]

// --8<-- [start:building-blocks-workflow]
// orchestratorWorkflow is a dynamic node that schedules two children in
// sequence via workflow.RunNode, equivalent to:
//
//	@node(rerun_on_resume=True)
//	async def my_workflow(ctx):
//	    result = await ctx.run_node(my_function_node, node_input="Hello")
//	    result_formatted = await ctx.run_node(my_formatting_node, node_input=result)
//	    return result_formatted
var orchestratorWorkflow = workflow.NewDynamicNode[string, string]("my_workflow",
	func(ctx agent.Context, _ string, _ func(*session.Event) error) (string, error) {
		result, err := workflow.RunNode[string](ctx, myFunctionNode, "Hello")
		if err != nil {
			return "", err
		}
		return workflow.RunNode[string](ctx, myFormattingNode, result)
	},
	workflow.NodeConfig{},
)

// --8<-- [end:building-blocks-workflow]

// --8<-- [start:data-handling]
// newDataHandlingWorkflow demonstrates how to pass data between a dynamic
// orchestrator and an LlmAgent-backed node. workflow.NewAgentNode wraps an
// agent.Agent so it can be invoked via workflow.RunNode.
//
// In Python this mirrors:
//
//	city_report_agent = Agent(name="city_report_agent", ...)
//	@node
//	async def city_workflow(ctx: Context):
//	    city_time = await ctx.run_node(city_time_function, "Paris")
//	    report_text = await ctx.run_node(city_report_agent, city_time)
//	    return report_text
func newDataHandlingWorkflow(ctx context.Context) (agent.Agent, error) {
	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("gemini.NewModel: %w", err)
	}

	// cityTimeNode is a FunctionNode that returns a formatted city-time string.
	cityTimeNode := workflow.NewFunctionNode("city_time_function",
		func(_ agent.Context, city string) (string, error) {
			return fmt.Sprintf("10:10 AM in %s", city), nil
		},
		workflow.NodeConfig{},
	)

	// cityReportAgent is an LlmAgent that receives the city-time string and
	// produces a human-friendly report.
	cityReportAgent, err := llmagent.New(llmagent.Config{
		Name:        "city_report_agent",
		Model:       model,
		Description: "Reports city time information.",
		Instruction: "Output the data provided by the previous node in a friendly sentence.",
	})
	if err != nil {
		return nil, fmt.Errorf("llmagent.New (cityReport): %w", err)
	}

	// workflow.NewAgentNode wraps cityReportAgent so it can be called from
	// inside a dynamic node via workflow.RunNode.
	cityReportNode, err := workflow.NewAgentNode(cityReportAgent, workflow.NodeConfig{})
	if err != nil {
		return nil, fmt.Errorf("workflow.NewAgentNode: %w", err)
	}

	cityWorkflow := workflow.NewDynamicNode[string, string]("city_workflow",
		func(ctx agent.Context, _ string, _ func(*session.Event) error) (string, error) {
			cityTime, err := workflow.RunNode[string](ctx, cityTimeNode, "Paris")
			if err != nil {
				return "", err
			}
			return workflow.RunNode[string](ctx, cityReportNode, cityTime)
		},
		workflow.NodeConfig{},
	)

	return workflowagent.New(workflowagent.Config{
		Name:      "data_handling_workflow",
		SubAgents: []agent.Agent{cityReportAgent},
		Edges:     workflow.Chain(workflow.Start, cityWorkflow),
	})
}

// --8<-- [end:data-handling]

// --8<-- [start:loop-route]
// newLoopWorkflow demonstrates an iterative loop inside a dynamic node.
// The orchestrator body uses a plain Go for loop to keep calling the
// lintCheckNode until there are no findings — equivalent to Python's:
//
//	@node
//	async def code_workflow(ctx: Context, user_request: str):
//	    code = await ctx.run_node(coder_agent, user_request)
//	    check_resp = await ctx.run_node(compile_lint_check, code)
//	    while check_resp.findings:
//	        code = await ctx.run_node(fixer_agent, ...)
//	        check_resp = await ctx.run_node(compile_lint_check, code)
//	    return code
func newLoopWorkflow(ctx context.Context) (agent.Agent, error) {
	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("gemini.NewModel: %w", err)
	}

	coderAgent, err := llmagent.New(llmagent.Config{
		Name:        "generator_agent",
		Model:       model,
		Description: "Writes Go code for the user request.",
		Instruction: "Write Go code for the user request. Output only the code.",
		OutputKey:   "generated_code",
	})
	if err != nil {
		return nil, fmt.Errorf("llmagent.New (coder): %w", err)
	}

	coderNode, err := workflow.NewAgentNode(coderAgent, workflow.NodeConfig{})
	if err != nil {
		return nil, fmt.Errorf("workflow.NewAgentNode (coder): %w", err)
	}

	// lintCheckNode simulates a lint/compile check. It returns an empty
	// string when there are no findings, signalling the loop to exit.
	lintCheckNode := workflow.NewFunctionNode("lint_reviewer",
		func(_ agent.Context, code string) (string, error) {
			// Simulate a lint check: return findings or empty string when clean.
			if len(code) < 50 {
				return "Code is too short; add error handling.", nil
			}
			return "", nil // no findings — loop exits
		},
		workflow.NodeConfig{},
	)

	fixerAgent, err := llmagent.New(llmagent.Config{
		Name:        "fixer_agent",
		Model:       model,
		Description: "Refactors code based on lint findings.",
		Instruction: "Refactor the provided code to address the review findings. Output only the improved code.",
	})
	if err != nil {
		return nil, fmt.Errorf("llmagent.New (fixer): %w", err)
	}

	fixerNode, err := workflow.NewAgentNode(fixerAgent, workflow.NodeConfig{})
	if err != nil {
		return nil, fmt.Errorf("workflow.NewAgentNode (fixer): %w", err)
	}

	codeWorkflow := workflow.NewDynamicNode[string, string]("code_workflow",
		func(ctx agent.Context, userRequest string, _ func(*session.Event) error) (string, error) {
			code, err := workflow.RunNode[string](ctx, coderNode, userRequest)
			if err != nil {
				return "", err
			}

			findings, err := workflow.RunNode[string](ctx, lintCheckNode, code)
			if err != nil {
				return "", err
			}

			// Loop until the lint check reports no findings.
			for findings != "" {
				code, err = workflow.RunNode[string](ctx, fixerNode, code)
				if err != nil {
					return "", err
				}
				findings, err = workflow.RunNode[string](ctx, lintCheckNode, code)
				if err != nil {
					return "", err
				}
			}
			return code, nil
		},
		workflow.NodeConfig{},
	)

	return workflowagent.New(workflowagent.Config{
		Name:      "code_pipeline",
		SubAgents: []agent.Agent{coderAgent, fixerAgent},
		Edges:     workflow.Chain(workflow.Start, codeWorkflow),
	})
}

// --8<-- [end:loop-route]

// --8<-- [start:parallel-route]
// newParallelWorkflow demonstrates parallel execution using
// workflow.NewParallelWorker. The worker node runs a wrapped child node
// concurrently for each element in a list input, collecting results.
//
// This is the Go equivalent of using asyncio.gather in Python:
//
//	@node(rerun_on_resume=True)
//	async def parallel_supervisor(ctx, node_input, real_node):
//	    tasks = [ctx.run_node(real_node, item) for item in node_input]
//	    results = await asyncio.gather(*tasks)
//	    return results
func newParallelWorkflow() (agent.Agent, error) {
	// workerNode processes a single item. NewParallelWorker will call it
	// once per element of the list input, concurrently.
	workerNode := workflow.NewFunctionNode("worker",
		func(_ agent.Context, item string) (string, error) {
			return fmt.Sprintf("processed: %s", item), nil
		},
		workflow.NodeConfig{},
	)

	// NewParallelWorker wraps workerNode so it runs concurrently for each
	// element of a []string input. maxConcurrency=0 means unlimited.
	parallelWorker, err := workflow.NewParallelWorker(
		"parallel_supervisor",
		workerNode,
		0, // maxConcurrency: 0 = unlimited
		workflow.NodeConfig{},
	)
	if err != nil {
		return nil, fmt.Errorf("workflow.NewParallelWorker: %w", err)
	}

	return workflowagent.New(workflowagent.Config{
		Name:        "parallel_workflow",
		Description: "Runs a worker node in parallel for each item in the input list.",
		Edges:       workflow.Chain(workflow.Start, parallelWorker),
	})
}

// --8<-- [end:parallel-route]

// --8<-- [start:human-input]
// newHITLWorkflow demonstrates the re-entry HITL pattern using
// workflow.ResumeOrRequestInput. On the first pass the node emits a
// RequestInput event and returns ErrNodeInterrupted (pausing the workflow).
// After the human replies, the same node is re-run from the top
// (RerunOnResume=&true) and ResumeOrRequestInput returns the human's reply.
//
// In Python this is equivalent to:
//
//	@node(rerun_on_resume=True)
//	async def get_user_approval(ctx, node_input):
//	    yield RequestInput(message="Please approve this request (Yes/No)")
//
//	@node(rerun_on_resume=True)
//	async def handle_process(ctx, node_input):
//	    user_response = await ctx.run_node(get_user_approval)
//	    if user_response.lower() == "yes":
//	        return "Approved"
//	    return "Denied"
func newHITLWorkflow() (agent.Agent, error) {
	rerun := true

	// approvalNode pauses on the first pass to ask the user for a Yes/No
	// approval, then resolves their decision on resume.
	// workflow.ResumeOrRequestInput handles both phases.
	approvalNode := workflow.NewEmittingFunctionNode[any, any]("get_user_approval",
		func(nc agent.Context, _ any, emit func(*session.Event) error) (any, error) {
			// ResumeOrRequestInput: on first pass, emits the prompt and
			// returns ErrNodeInterrupted. On re-run after the human replies,
			// it returns the reply payload directly.
			reply, err := workflow.ResumeOrRequestInput(nc, emit, session.RequestInput{
				InterruptID: "user_approval",
				Message:     "Please approve this request (Yes/No)",
			})
			if err != nil {
				return nil, err
			}

			response, _ := reply.(string)
			if response == "" {
				response = "No"
			}
			if response == "yes" || response == "Yes" {
				return "Approved", nil
			}
			return "Denied", nil
		},
		workflow.NodeConfig{RerunOnResume: &rerun},
	)

	return workflowagent.New(workflowagent.Config{
		Name:        "hitl_workflow",
		Description: "Pauses for user approval before completing a task.",
		Edges:       workflow.Chain(workflow.Start, approvalNode),
	})
}

// --8<-- [end:human-input]

// --8<-- [start:custom-execution-ids]
// newCustomIDWorkflow demonstrates supplying stable custom run IDs via
// workflow.WithRunID — equivalent to Python's:
//
//	task = ctx.run_node(process_order, order, run_id=f"order-{order.order_id}")
//
// Custom run IDs must contain at least one non-numeric character to avoid
// collision with auto-generated sequential integer IDs.
func newCustomIDWorkflow() (agent.Agent, error) {
	processOrderNode := workflow.NewFunctionNode("process_order",
		func(_ agent.Context, orderID string) (string, error) {
			return fmt.Sprintf("processed order %s", orderID), nil
		},
		workflow.NodeConfig{},
	)

	orders := []string{"ord-001", "ord-002", "ord-003"}

	processAllOrders := workflow.NewDynamicNode[any, []string]("process_all_orders",
		func(ctx agent.Context, _ any, _ func(*session.Event) error) ([]string, error) {
			results := make([]string, 0, len(orders))
			for _, orderID := range orders {
				// WithRunID supplies a stable, deterministic identifier for
				// each child invocation. IDs must contain at least one
				// non-numeric character to avoid collision with the
				// auto-generated sequential counter IDs.
				result, err := workflow.RunNode[string](
					ctx,
					processOrderNode,
					orderID,
					workflow.WithRunID(fmt.Sprintf("order-%s", orderID)),
				)
				if err != nil {
					return nil, fmt.Errorf("process order %s: %w", orderID, err)
				}
				results = append(results, result)
			}
			return results, nil
		},
		workflow.NodeConfig{},
	)

	return workflowagent.New(workflowagent.Config{
		Name:        "custom_id_workflow",
		Description: "Processes orders with stable per-order execution IDs.",
		Edges:       workflow.Chain(workflow.Start, processAllOrders),
	})
}

// --8<-- [end:custom-execution-ids]

func main() {
	if err := runGetStarted(); err != nil {
		log.Fatalf("runGetStarted: %v", err)
	}
}
