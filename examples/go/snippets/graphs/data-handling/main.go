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

// Package main demonstrates data-handling patterns for ADK Go workflow agents.
//
// In ADK Go, data flows between workflow steps through session state rather than
// through an Event.output field. The two primary mechanisms are:
//
//  1. OutputKey on llmagent.Config — the framework automatically captures the
//     agent's final text response and writes it to the named session-state key.
//     Downstream agents read that value by referencing {key} in their Instruction
//     template.
//
//  2. ctx.Session().State().Set / .Get — for custom Run functions and tools that
//     need to write or read arbitrary values from session state directly.
//
// State keys may carry a prefix to control their lifetime and scope:
//
//	session.KeyPrefixApp  ("app:")  – shared across all users and sessions for the app
//	session.KeyPrefixUser ("user:") – shared across all sessions for a user
//	session.KeyPrefixTemp ("temp:") – discarded after the current invocation ends
//
// Keys without a prefix persist for the lifetime of the session.
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
	"google.golang.org/adk/agent/workflowagents/sequentialagent"
	"google.golang.org/adk/model"
	"google.golang.org/adk/session"
)

// --8<-- [start:output-key]
// OutputKey is the primary mechanism for passing data between llmagent steps in
// a sequential workflow. When OutputKey is set, the framework automatically
// saves the agent's final text response to session state under that key after
// each turn. Downstream agents read the value by referencing {key} in their
// Instruction template.
//
// This is the Go equivalent of the Python Event(output=...) pattern:
//
//	def my_function_node():
//	    return Event(output="The Result")
func newOutputKeyPipeline(ctx context.Context, geminiModel model.LLM) (agent.Agent, error) {
	// step1 writes its response to state["upper_result"].
	step1, err := llmagent.New(llmagent.Config{
		Name:        "step_1",
		Model:       geminiModel,
		Description: "Transforms the user's text.",
		Instruction: "Convert the user's message to uppercase. Output only the transformed text.",
		OutputKey:   "upper_result", // framework saves final response here
	})
	if err != nil {
		return nil, fmt.Errorf("step1: %w", err)
	}

	// step2 reads state["upper_result"] via the {upper_result} template placeholder.
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

// --8<-- [start:custom-run-node]
// customRunNode is a workflow step (node) implemented as a custom Run function.
// It transforms its input, writes the result to session state, and yields a
// session.Event — the Go equivalent of a Python FunctionNode that returns
// Event(output=value).
//
// Data written by custom Run functions via ctx.Session().State().Set is
// immediately available to the next step through the {key} Instruction template.
func customRunNode(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
	return func(yield func(*session.Event, error) bool) {
		// Read the user's original message.
		var inputText string
		if ctx.UserContent() != nil {
			for _, p := range ctx.UserContent().Parts {
				inputText += p.Text
			}
		}

		// Transform and persist to state so downstream steps can read it.
		result := strings.ToUpper(strings.TrimSpace(inputText))
		if err := ctx.Session().State().Set("upper_result", result); err != nil {
			yield(nil, fmt.Errorf("state.Set upper_result: %w", err))
			return
		}

		// Yield the transformed text as the event output.
		yield(&session.Event{
			LLMResponse: model.LLMResponse{
				Content: &genai.Content{
					Parts: []*genai.Part{{Text: result}},
				},
			},
		}, nil)
	}
}

// --8<-- [end:custom-run-node]

// --8<-- [start:state-scopes]
// stateScopes shows how session-state key prefixes control the lifetime and
// visibility of stored values across workflow steps.
//
// Available prefixes (defined as constants in the session package):
//
//	session.KeyPrefixApp  ("app:")  – shared across all users and sessions for the app
//	session.KeyPrefixUser ("user:") – tied to the user, shared across their sessions
//	session.KeyPrefixTemp ("temp:") – discarded when the current invocation ends
//
// Keys with no prefix persist for the lifetime of the session.
//
// This is the Go equivalent of the Python Event(state={...}) pattern:
//
//	async def init_state_node(attempts: int = 0):
//	    yield Event(state={"attempts": attempts})
func stateScopes(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
	return func(yield func(*session.Event, error) bool) {
		st := ctx.Session().State()

		// Session-scoped (no prefix) — persists for the life of this session.
		if err := st.Set("attempts", 0); err != nil {
			yield(nil, fmt.Errorf("state.Set attempts: %w", err))
			return
		}

		// App-scoped — shared across all users and sessions for this app.
		if err := st.Set(session.KeyPrefixApp+"global_counter", 42); err != nil {
			yield(nil, fmt.Errorf("state.Set app:global_counter: %w", err))
			return
		}

		// User-scoped — shared across all sessions belonging to this user.
		if err := st.Set(session.KeyPrefixUser+"login_count", 1); err != nil {
			yield(nil, fmt.Errorf("state.Set user:login_count: %w", err))
			return
		}

		// Temp-scoped — discarded after this invocation (single request/response) ends.
		if err := st.Set(session.KeyPrefixTemp+"scratch", "ephemeral"); err != nil {
			yield(nil, fmt.Errorf("state.Set temp:scratch: %w", err))
			return
		}

		yield(&session.Event{
			LLMResponse: model.LLMResponse{
				Content: &genai.Content{
					Parts: []*genai.Part{{Text: "State initialised."}},
				},
			},
		}, nil)
	}
}

// --8<-- [end:state-scopes]

// --8<-- [start:message-output]
// messageOutputNode is a workflow step that emits a progress message for the
// user. In Python this would be:
//
//	async def user_message(node_input: str):
//	    yield Event(message="Beginning research process...")
//
// In Go, the equivalent is to yield a session.Event whose LLMResponse.Content
// contains the text intended for the user. The step does not need to write to
// state; the runner surfaces the event text to the caller as a partial response.
func messageOutputNode(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
	return func(yield func(*session.Event, error) bool) {
		yield(&session.Event{
			LLMResponse: model.LLMResponse{
				Content: &genai.Content{
					Parts: []*genai.Part{{Text: "Beginning research process..."}},
				},
			},
		}, nil)
	}
}

// --8<-- [end:message-output]

// --8<-- [start:input-output-schema]
// newSchemaAgentPipeline builds a two-agent sequential pipeline where the first
// agent has a structured InputSchema and OutputSchema and the second reads the
// first agent's output from session state.
//
// InputSchema constrains what the agent accepts when called as a sub-agent
// tool. OutputSchema forces the model to reply with a JSON object matching the
// provided schema — equivalent to Pydantic BaseModel in Python:
//
//	class FlightSearchOutput(BaseModel):
//	    origin: str
//	    destination: str
//
//	flight_searcher = Agent(
//	    input_schema=FlightSearchInput,
//	    output_schema=FlightSearchOutput,
//	    ...
//	)
func newSchemaAgentPipeline(ctx context.Context, geminiModel model.LLM) (agent.Agent, error) {
	// InputSchema: defines the expected JSON shape when this agent is invoked
	// as a sub-agent / tool by another agent.
	flightInputSchema := &genai.Schema{
		Type:        genai.TypeObject,
		Description: "Input for a flight search request.",
		Properties: map[string]*genai.Schema{
			"origin": {
				Type:        genai.TypeString,
				Description: "Departure airport code, e.g. SFO.",
			},
			"destination": {
				Type:        genai.TypeString,
				Description: "Arrival airport code, e.g. CDG.",
			},
			"departure_date": {
				Type:        genai.TypeString,
				Description: "Departure date in YYYY-MM-DD format.",
			},
		},
		Required: []string{"origin", "destination", "departure_date"},
	}

	// OutputSchema: forces the model to reply with a JSON object matching
	// this schema. When OutputSchema is set the agent cannot use tools.
	flightOutputSchema := &genai.Schema{
		Type:        genai.TypeObject,
		Description: "Result of a flight search.",
		Properties: map[string]*genai.Schema{
			"cheapest_price": {
				Type:        genai.TypeString,
				Description: "Cheapest available fare as a formatted string, e.g. '$450'.",
			},
			"flight_count": {
				Type:        genai.TypeString,
				Description: "Number of matching flights found.",
			},
		},
		Required: []string{"cheapest_price", "flight_count"},
	}

	flightSearchAgent, err := llmagent.New(llmagent.Config{
		Name:        "flight_searcher",
		Model:       geminiModel,
		Description: "Searches for available flights and returns structured results.",
		Instruction: `You are a flight-search assistant.
Given a search request, respond ONLY with a JSON object.
Estimate the cheapest price and count of available flights.`,
		InputSchema:  flightInputSchema,
		OutputSchema: flightOutputSchema,
		OutputKey:    "flight_search_result", // saves JSON string to state
	})
	if err != nil {
		return nil, fmt.Errorf("flightSearchAgent: %w", err)
	}

	// The assistant agent reads the structured result from state via the
	// {flight_search_result} template placeholder in its Instruction.
	assistantAgent, err := llmagent.New(llmagent.Config{
		Name:        "trip_assistant",
		Model:       geminiModel,
		Description: "Summarises flight search results for the user.",
		Instruction: `You help users plan trips.
The flight search returned this result: {flight_search_result}
Summarise the cheapest option for the user in a friendly sentence.`,
	})
	if err != nil {
		return nil, fmt.Errorf("assistantAgent: %w", err)
	}

	return sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        "flight_booking_pipeline",
			Description: "Searches for flights then presents the results to the user.",
			SubAgents:   []agent.Agent{flightSearchAgent, assistantAgent},
		},
	})
}

// --8<-- [end:input-output-schema]

// --8<-- [start:template-data-access]
// newCityTimePipeline demonstrates how an agent reads structured data that was
// written to session state by the previous step using the {key} template syntax
// in its Instruction — the Go equivalent of:
//
//	city_report_agent = Agent(
//	    input_schema=CityTime,
//	    instruction="It is {CityTime.time_info} in {CityTime.city} right now.",
//	)
//
// In Go, each field is a separate state key. The {key} placeholder in
// Instruction is replaced by the ADK framework with the current value of
// state["key"] before the instruction is sent to the model.
func newCityTimePipeline(ctx context.Context, geminiModel model.LLM) (agent.Agent, error) {
	// cityGeneratorAgent writes the city name to state["city_name"].
	cityGeneratorAgent, err := llmagent.New(llmagent.Config{
		Name:        "city_generator_agent",
		Model:       geminiModel,
		Description: "Returns the name of a random city.",
		Instruction: "Output only the name of one well-known city. Nothing else.",
		OutputKey:   "city_name",
	})
	if err != nil {
		return nil, fmt.Errorf("cityGeneratorAgent: %w", err)
	}

	// lookupTimeAgent reads state["city_name"] via {city_name} and writes the
	// current time to state["time_info"].
	lookupTimeAgent, err := llmagent.New(llmagent.Config{
		Name:        "lookup_time_agent",
		Model:       geminiModel,
		Description: "Returns the current time in the city from the previous step.",
		Instruction: "What time is it right now in {city_name}? Output only the time, e.g. '10:10 AM'.",
		OutputKey:   "time_info",
	})
	if err != nil {
		return nil, fmt.Errorf("lookupTimeAgent: %w", err)
	}

	// cityReportAgent reads both state["city_name"] and state["time_info"] via
	// the {city_name} and {time_info} placeholders in its Instruction.
	cityReportAgent, err := llmagent.New(llmagent.Config{
		Name:        "city_report_agent",
		Model:       geminiModel,
		Description: "Reports the city and the current time.",
		Instruction: "Return a sentence in the following format: It is {time_info} in {city_name} right now.",
	})
	if err != nil {
		return nil, fmt.Errorf("cityReportAgent: %w", err)
	}

	return sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        "city_time_pipeline",
			Description: "Generates a city name, looks up the time, then reports both.",
			SubAgents:   []agent.Agent{cityGeneratorAgent, lookupTimeAgent, cityReportAgent},
		},
	})
}

// --8<-- [end:template-data-access]

func main() {
	ctx := context.Background()

	// A nil model is used here so the file builds without credentials.
	// Real usage requires a valid model from gemini.NewModel.
	var geminiModel model.LLM

	if _, err := newOutputKeyPipeline(ctx, geminiModel); err != nil {
		log.Printf("newOutputKeyPipeline: %v", err)
	}
	if _, err := newSchemaAgentPipeline(ctx, geminiModel); err != nil {
		log.Printf("newSchemaAgentPipeline: %v", err)
	}
	if _, err := newCityTimePipeline(ctx, geminiModel); err != nil {
		log.Printf("newCityTimePipeline: %v", err)
	}

	// Wrap custom Run functions in agent.Agent so they participate in the
	// normal agent lifecycle.
	customNode, err := agent.New(agent.Config{
		Name: "custom_run_node",
		Run:  customRunNode,
	})
	if err != nil {
		log.Printf("agent.New(customRunNode): %v", err)
	}
	_ = customNode

	msgNode, err := agent.New(agent.Config{
		Name: "message_output_node",
		Run:  messageOutputNode,
	})
	if err != nil {
		log.Printf("agent.New(messageOutputNode): %v", err)
	}
	_ = msgNode

	stateNode, err := agent.New(agent.Config{
		Name: "state_scopes_node",
		Run:  stateScopes,
	})
	if err != nil {
		log.Printf("agent.New(stateScopes): %v", err)
	}
	_ = stateNode
}
