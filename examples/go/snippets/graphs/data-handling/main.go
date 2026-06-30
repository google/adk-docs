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

// Package main demonstrates data-handling patterns for ADK Go v2 workflow agents.
//
// NOTE: This file requires google.golang.org/adk/v2 (the workflow package),
// available in ADK Go v2.0.0 and later. It carries //go:build ignore so it is
// excluded from the current examples/go module (which is still on the v1 path)
// until examples/go is migrated to google.golang.org/adk/v2 at the v2.0.0
// release.
//
// # Data flow in ADK Go v2
//
// ADK Go v2 provides two complementary data-passing mechanisms depending on
// which agent style you use:
//
// ## workflow package (graph engine: FunctionNode / AgentNode / DynamicNode)
//
// Nodes communicate by setting fields on session.Event:
//
//   - Event.Output (any): the node's typed return value, set automatically by
//     the framework when a FunctionNode returns a non-*genai.Content value.
//     Successor nodes receive this as their typed `input` parameter via
//     workflow.RunNode.
//   - Event.Routes ([]string): routing keys a node emits to select which edge
//     to follow. Set explicitly by an emitting function node using
//     session.NewEvent + ev.Routes = []string{"category"}.
//   - Event.NodeInfo (*session.NodeInfo): scheduler metadata (path,
//     MessageAsOutput, OutputFor). Set by the workflow engine; nodes do not
//     set this directly.
//   - Event.Content (*genai.Content): when a FunctionNode returns a string or
//     *genai.Content, the framework stores it here for the LLM / user stream.
//
// ## Prebuilt workflow agents (sequentialagent / parallelagent / loopagent)
//
// These agents communicate through session state:
//
//   - llmagent.Config.OutputKey: the framework writes the agent's final text
//     response to state[OutputKey] after each turn.
//   - ctx.Session().State().Set / .Get: write/read arbitrary values from state
//     inside custom code.
//   - {key} in Instruction: the framework substitutes state["key"] into the
//     prompt before calling the model.
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
	"google.golang.org/adk/v2/agent/workflowagents/sequentialagent"
	"google.golang.org/adk/v2/model"
	"google.golang.org/adk/v2/model/gemini"
	"google.golang.org/adk/v2/session"
	"google.golang.org/adk/v2/workflow"
)

// --8<-- [start:event-output]
// newEventOutputPipeline demonstrates the primary data-passing mechanism for
// workflow package nodes: a FunctionNode returns a typed Go value, and the
// framework automatically sets event.Output to that value. The successor node
// receives it as its typed `input` parameter.
//
// This mirrors the Python pattern exactly:
//
//	def my_function_node(node_input: str):
//	    return Event(output=node_input.upper())
//
// In Go, the function simply returns the value — no Event construction needed.
func newEventOutputPipeline() (agent.Agent, error) {
	upperFn := func(_ agent.Context, input string) (string, error) {
		return strings.ToUpper(input), nil
	}

	suffixFn := func(_ agent.Context, input string) (string, error) {
		return input + " IS AWESOME!", nil
	}

	nodeA := workflow.NewFunctionNode("upper", upperFn, workflow.NodeConfig{})
	nodeB := workflow.NewFunctionNode("suffix", suffixFn, workflow.NodeConfig{})

	// workflow.Chain wires START → nodeA → nodeB. The output of nodeA is
	// delivered as the typed input of nodeB via event.Output.
	return workflowagent.New(workflowagent.Config{
		Name:        "event_output_pipeline",
		Description: "Demonstrates Event.Output data flow between FunctionNodes.",
		Edges:       workflow.Chain(workflow.Start, nodeA, nodeB),
	})
}

// --8<-- [end:event-output]

// --8<-- [start:routing-output]
// classifyAndRoute shows how to set event.Routes alongside event.Output from
// an emitting FunctionNode. The function constructs a session.Event directly,
// sets Routes to select the conditional edge, and sets Output to forward the
// payload to the successor node.
//
// This mirrors the Python pattern:
//
//	def router(node_input: str):
//	    return Event(route="BUG")
func classifyAndRoute(ctx agent.Context, msg string, emit func(*session.Event) error) (any, error) {
	category := classifyMessage(msg)

	ev := session.NewEvent(ctx, ctx.InvocationID())
	ev.Routes = []string{category} // drives edge dispatch
	ev.Output = msg                // forwarded as typed input to the successor
	if err := emit(ev); err != nil {
		return nil, err
	}
	return nil, nil // nil suppresses the automatic terminal event
}

func classifyMessage(msg string) string {
	switch {
	case strings.Contains(strings.ToLower(msg), "bug"):
		return "BUG"
	case strings.Contains(strings.ToLower(msg), "help"):
		return "CUSTOMER_SUPPORT"
	default:
		return "LOGISTICS"
	}
}

func newRoutingPipeline() (agent.Agent, error) {
	classifyNode := workflow.NewEmittingFunctionNode("classify", classifyAndRoute, workflow.NodeConfig{})

	bugHandler := workflow.NewFunctionNode("bug_handler",
		func(_ agent.Context, msg string) (string, error) {
			return "Handling bug: " + msg, nil
		}, workflow.NodeConfig{})

	supportHandler := workflow.NewFunctionNode("support_handler",
		func(_ agent.Context, msg string) (string, error) {
			return "Handling support: " + msg, nil
		}, workflow.NodeConfig{})

	logisticsHandler := workflow.NewFunctionNode("logistics_handler",
		func(_ agent.Context, msg string) (string, error) {
			return "Handling logistics: " + msg, nil
		}, workflow.NodeConfig{})

	edges := workflow.Concat(
		workflow.Chain(workflow.Start, classifyNode),
		[]workflow.Edge{
			{From: classifyNode, To: bugHandler, Route: workflow.StringRoute("BUG")},
			{From: classifyNode, To: supportHandler, Route: workflow.StringRoute("CUSTOMER_SUPPORT")},
			{From: classifyNode, To: logisticsHandler, Route: workflow.StringRoute("LOGISTICS")},
		},
	)
	return workflowagent.New(workflowagent.Config{
		Name:        "routing_pipeline",
		Description: "Classifies and routes a message using Event.Routes.",
		Edges:       edges,
	})
}

// --8<-- [end:routing-output]

// --8<-- [start:structured-output]
// newStructuredOutputPipeline shows how to pass a struct from one FunctionNode
// to another. The framework serialises the return value into event.Output and
// deserialises it back into the successor's typed input parameter.
//
// This is the Go equivalent of:
//
//	class CityTime(BaseModel):
//	    time_info: str
//	    city: str
//
//	def lookup_time_function(city: str):
//	    return Event(output=CityTime(time_info="10:10 AM", city=city))
//
//	def city_report(node_input: CityTime):
//	    return Event(output=f"It is {node_input.time_info} in {node_input.city}.")
type CityTime struct {
	TimeInfo string `json:"time_info"`
	City     string `json:"city"`
}

func newStructuredOutputPipeline(ctx context.Context, geminiModel model.LLM) (agent.Agent, error) {
	lookupTimeFn := func(_ agent.Context, city string) (CityTime, error) {
		// Simulate looking up the current time in the city.
		return CityTime{TimeInfo: "10:10 AM", City: city}, nil
	}

	cityReportAgent, err := llmagent.New(llmagent.Config{
		Name:        "city_report_agent",
		Model:       geminiModel,
		Description: "Reports the city and current time from the previous node's output.",
		// When wrapped as an AgentNode, the predecessor's event.Output
		// is delivered as the agent's user content. The {key} template
		// syntax is not required — the struct fields are provided inline.
		Instruction: "Report the city time information you received in a friendly sentence.",
	})
	if err != nil {
		return nil, fmt.Errorf("cityReportAgent: %w", err)
	}

	lookupTimeNode := workflow.NewFunctionNode("lookup_time", lookupTimeFn, workflow.NodeConfig{})
	cityReportNode, err := workflow.NewAgentNode(cityReportAgent, workflow.NodeConfig{})
	if err != nil {
		return nil, fmt.Errorf("NewAgentNode: %w", err)
	}

	return workflowagent.New(workflowagent.Config{
		Name:      "city_time_pipeline",
		Edges:     workflow.Chain(workflow.Start, lookupTimeNode, cityReportNode),
		SubAgents: []agent.Agent{cityReportAgent},
	})
}

// --8<-- [end:structured-output]

// --8<-- [start:output-key]
// newOutputKeyPipeline demonstrates the OutputKey mechanism for the prebuilt
// sequentialagent. When OutputKey is set on an llmagent.Config, the framework
// automatically writes the agent's final text response to session state under
// that key. Downstream agents read it by referencing {key} in their Instruction.
//
// This pattern applies to sequentialagent / parallelagent / loopagent.
// For the workflow package (FunctionNode / AgentNode), use Event.Output instead.
func newOutputKeyPipeline(ctx context.Context, geminiModel model.LLM) (agent.Agent, error) {
	step1, err := llmagent.New(llmagent.Config{
		Name:        "step_1",
		Model:       geminiModel,
		Description: "Transforms the user's text.",
		Instruction: "Convert the user's message to uppercase. Output only the transformed text.",
		OutputKey:   "upper_result",
	})
	if err != nil {
		return nil, fmt.Errorf("step1: %w", err)
	}

	step2, err := llmagent.New(llmagent.Config{
		Name:        "step_2",
		Model:       geminiModel,
		Description: "Reports the transformed text.",
		Instruction: "The transformed text is: {upper_result}. Report it to the user.",
	})
	if err != nil {
		return nil, fmt.Errorf("step2: %w", err)
	}

	return sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:      "output_key_pipeline",
			SubAgents: []agent.Agent{step1, step2},
		},
	})
}

// --8<-- [end:output-key]

// --8<-- [start:state-scopes]
// stateScopes shows how session-state key prefixes control the lifetime and
// visibility of stored values. This pattern applies to the prebuilt workflow
// agents (sequentialagent / parallelagent / loopagent) and to tools and
// callbacks. For the workflow package (FunctionNode / AgentNode), prefer
// returning values directly via Event.Output.
//
// Available prefixes:
//
//	session.KeyPrefixApp  ("app:")  – shared across all users and sessions
//	session.KeyPrefixUser ("user:") – tied to the user, shared across sessions
//	session.KeyPrefixTemp ("temp:") – discarded after the current invocation
//
// Keys with no prefix persist for the lifetime of the session.
func stateScopes(ctx agent.Context) error {
	st := ctx.Session().State()

	// Session-scoped (no prefix) — persists for the life of this session.
	if err := st.Set("attempts", 0); err != nil {
		return fmt.Errorf("state.Set attempts: %w", err)
	}

	// App-scoped — shared across all users and sessions for this app.
	if err := st.Set(session.KeyPrefixApp+"global_counter", 42); err != nil {
		return fmt.Errorf("state.Set app:global_counter: %w", err)
	}

	// User-scoped — shared across all sessions belonging to this user.
	if err := st.Set(session.KeyPrefixUser+"login_count", 1); err != nil {
		return fmt.Errorf("state.Set user:login_count: %w", err)
	}

	// Temp-scoped — discarded after this invocation ends.
	if err := st.Set(session.KeyPrefixTemp+"scratch", "ephemeral"); err != nil {
		return fmt.Errorf("state.Set temp:scratch: %w", err)
	}

	return nil
}

// --8<-- [end:state-scopes]

// --8<-- [start:input-output-schema]
// FlightSearchInput is the typed input schema for the flight-search agent node.
// workflow.NewAgentNodeTyped[FlightSearchInput, FlightSearchOutput] reflects
// these structs into *jsonschema.Schema automatically — no hand-built schema
// construction needed.
type FlightSearchInput struct {
	Origin        string `json:"origin"         jsonschema:"description=Departure airport code e.g. SFO"`
	Destination   string `json:"destination"    jsonschema:"description=Arrival airport code e.g. CDG"`
	DepartureDate string `json:"departure_date" jsonschema:"description=Travel date in YYYY-MM-DD format"`
}

// FlightSearchOutput is the typed output schema for the flight-search agent node.
type FlightSearchOutput struct {
	CheapestPrice string `json:"cheapest_price" jsonschema:"description=Cheapest available fare e.g. $450"`
	FlightCount   string `json:"flight_count"   jsonschema:"description=Number of matching flights found"`
}

// newSchemaAgentPipeline demonstrates workflow.NewAgentNodeTyped, which infers
// *jsonschema.Schema from the generic type parameters. This is the Go equivalent
// of Python's:
//
//	flight_searcher = Agent(
//	    input_schema=FlightSearchInput,
//	    output_schema=FlightSearchOutput,
//	    ...
//	)
//
// The node's event.Output carries the structured result to the successor —
// no OutputKey or state write is needed.
func newSchemaAgentPipeline(ctx context.Context, geminiModel model.LLM) (agent.Agent, error) {
	flightSearchAgent, err := llmagent.New(llmagent.Config{
		Name:        "flight_searcher",
		Model:       geminiModel,
		Description: "Searches for available flights and returns structured results.",
		Instruction: `You are a flight-search assistant. Respond ONLY with a JSON object.`,
	})
	if err != nil {
		return nil, fmt.Errorf("flightSearchAgent: %w", err)
	}

	synthAgent, err := llmagent.New(llmagent.Config{
		Name:        "trip_assistant",
		Model:       geminiModel,
		Description: "Summarises flight search results for the user.",
		Instruction: `You help users plan trips. Summarise the flight result you received.`,
	})
	if err != nil {
		return nil, fmt.Errorf("synthAgent: %w", err)
	}

	// NewAgentNodeTyped[In, Out] reflects FlightSearchInput and FlightSearchOutput
	// into *jsonschema.Schema automatically. The node enforces the input schema
	// and constrains the model reply to the output schema's shape.
	flightNode, err := workflow.NewAgentNodeTyped[FlightSearchInput, FlightSearchOutput](flightSearchAgent, workflow.NodeConfig{})
	if err != nil {
		return nil, fmt.Errorf("flightNode: %w", err)
	}

	synthNode, err := workflow.NewAgentNode(synthAgent, workflow.NodeConfig{})
	if err != nil {
		return nil, fmt.Errorf("synthNode: %w", err)
	}

	return workflowagent.New(workflowagent.Config{
		Name:      "flight_booking_pipeline",
		Edges:     workflow.Chain(workflow.Start, flightNode, synthNode),
		SubAgents: []agent.Agent{flightSearchAgent, synthAgent},
	})
}

// --8<-- [end:input-output-schema]

func main() {
	ctx := context.Background()

	if _, err := newEventOutputPipeline(); err != nil {
		log.Printf("newEventOutputPipeline: %v", err)
	}

	if _, err := newRoutingPipeline(); err != nil {
		log.Printf("newRoutingPipeline: %v", err)
	}

	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{})
	if err != nil {
		log.Printf("gemini.NewModel: %v", err)
		return
	}

	if _, err := newStructuredOutputPipeline(ctx, model); err != nil {
		log.Printf("newStructuredOutputPipeline: %v", err)
	}

	if _, err := newOutputKeyPipeline(ctx, model); err != nil {
		log.Printf("newOutputKeyPipeline: %v", err)
	}

	if _, err := newSchemaAgentPipeline(ctx, model); err != nil {
		log.Printf("newSchemaAgentPipeline: %v", err)
	}
}
