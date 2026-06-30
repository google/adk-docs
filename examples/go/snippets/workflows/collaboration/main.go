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

// Package main demonstrates collaborative agent team patterns in ADK Go v2.
//
// NOTE: This file requires google.golang.org/adk/v2, available in ADK Go
// v2.0.0 and higher.
//
// # Agent collaboration modes in ADK Go v2
//
// The Mode field on llmagent.Config controls how a subagent behaves when
// invoked by a coordinator agent. Three modes are available:
//
//   - "chat" (ModeChat, default): full user interaction; agent controls
//     flow until it explicitly calls transfer_to_agent.
//   - "task" (ModeTask): agent may ask the user clarifying questions and
//     automatically returns control to the parent when it calls complete_task.
//   - "single_turn" (ModeSingleTurn): no user interaction; executes one turn
//     and returns automatically; can run in parallel with peer agents.
//
// When a coordinator llmagent declares SubAgents, ADK automatically generates
// request_task_<name> tools for each subagent, wiring the delegation pattern.
//
// When an llmagent is used as a node in the v2 workflow graph engine
// (workflow.NewAgentNode), the engine automatically applies ModeSingleTurn
// if no mode is configured on the agent.
package main

import (
	"context"
	"log"

	"google.golang.org/genai"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/llmagent"
	"google.golang.org/adk/v2/model/gemini"
	"google.golang.org/adk/v2/tool"
	"google.golang.org/adk/v2/tool/functiontool"
)

// --8<-- [start:get-started]
// Stub tool functions — in a real agent these call external services.
func getWeather(_ agent.Context, _ struct{ City string }) (string, error) {
	return "Sunny, 22°C", nil
}

func searchFlights(_ agent.Context, _ struct{ Origin, Destination string }) (string, error) {
	return "3 flights found", nil
}

func bookFlight(_ agent.Context, _ struct{ FlightID string }) (string, error) {
	return "Flight booked", nil
}

// newCollaborativeTeam builds a coordinator agent with two subagents, each
// configured with a different collaboration mode. This is the Go equivalent of:
//
//	weather_agent = Agent(name="weather_checker", mode="single_turn", ...)
//	flight_agent  = Agent(name="flight_booker",   mode="task",        ...)
//	root = Agent(name="travel_planner", sub_agents=[weather_agent, flight_agent])
func newCollaborativeTeam(ctx context.Context) (agent.Agent, error) {
	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{})
	if err != nil {
		return nil, err
	}

	getWeatherTool, err := functiontool.New(functiontool.Config{
		Name:        "get_weather",
		Description: "Returns the current weather for a city.",
	}, getWeather)
	if err != nil {
		return nil, err
	}

	searchFlightsTool, err := functiontool.New(functiontool.Config{
		Name:        "search_flights",
		Description: "Searches for available flights between two airports.",
	}, searchFlights)
	if err != nil {
		return nil, err
	}

	bookFlightTool, err := functiontool.New(functiontool.Config{
		Name:        "book_flight",
		Description: "Books a specific flight by ID.",
	}, bookFlight)
	if err != nil {
		return nil, err
	}

	// weatherAgent runs in ModeSingleTurn: no user interaction, executes one
	// turn and returns automatically. Equivalent to mode="single_turn" in Python.
	weatherAgent, err := llmagent.New(llmagent.Config{
		Name:        "weather_checker",
		Model:       model,
		Mode:        llmagent.ModeSingleTurn,
		Description: "Checks the current weather for a given city.",
		Instruction: "Use the get_weather tool to look up the current weather.",
		Tools:       []tool.Tool{getWeatherTool},
	})
	if err != nil {
		return nil, err
	}

	// flightAgent runs in ModeTask: may ask the user clarifying questions and
	// automatically returns control to the coordinator when done. Equivalent to
	// mode="task" in Python.
	flightAgent, err := llmagent.New(llmagent.Config{
		Name:        "flight_booker",
		Model:       model,
		Mode:        llmagent.ModeTask,
		Description: "Searches for and books flights.",
		Instruction: "Help the user find and book a flight using the available tools.",
		Tools:       []tool.Tool{searchFlightsTool, bookFlightTool},
	})
	if err != nil {
		return nil, err
	}

	// The coordinator agent declares SubAgents. ADK automatically generates
	// request_task_weather_checker and request_task_flight_booker tools so the
	// coordinator can delegate work to each subagent.
	return llmagent.New(llmagent.Config{
		Name:        "travel_planner",
		Model:       model,
		Description: "Coordinator agent that delegates to weather and flight subagents.",
		Instruction: "Help the user plan their trip. Use the weather checker and flight booker as needed.",
		SubAgents:   []agent.Agent{weatherAgent, flightAgent},
	})
}

// --8<-- [end:get-started]

func main() {
	ctx := context.Background()

	rootAgent, err := newCollaborativeTeam(ctx)
	if err != nil {
		log.Fatalf("newCollaborativeTeam: %v", err)
	}
	log.Printf("created coordinator agent: %s", rootAgent.Name())
}
