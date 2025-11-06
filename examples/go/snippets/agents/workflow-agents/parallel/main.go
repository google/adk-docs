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

package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/agent/workflowagents/parallelagent"
	"google.golang.org/adk/agent/workflowagents/sequentialagent"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/genai"
)

const (
	appName   = "parallel_research_app"
	userID    = "research_user_01"
	modelName = "gemini-2.0-flash"
)

func main() {
	ctx := context.Background()

	if err := runAgent(ctx, "Summarize recent sustainable tech advancements."); err != nil {
		log.Fatalf("Agent execution failed: %v", err)
	}
}

func runAgent(ctx context.Context, prompt string) error {
	// --8<-- [start:init]
	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return fmt.Errorf("failed to create model: %v", err)
	}

	// --- 1. Define Researcher Sub-Agents (to run in parallel) ---
	researcher1, err := llmagent.New(llmagent.Config{
		Name:  "RenewableEnergyResearcher",
		Model: model,
		Instruction: `You are an AI Research Assistant specializing in energy.
Research the latest advancements in 'renewable energy sources'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output *only* the summary.`,
		Description: "Researches renewable energy sources.",
		OutputKey:   "renewable_energy_result",
	})
	if err != nil {
		return err
	}
	researcher2, err := llmagent.New(llmagent.Config{
		Name:  "EVResearcher",
		Model: model,
		Instruction: `You are an AI Research Assistant specializing in transportation.
Research the latest developments in 'electric vehicle technology'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output *only* the summary.`,
		Description: "Researches electric vehicle technology.",
		OutputKey:   "ev_technology_result",
	})
	if err != nil {
		return err
	}
	researcher3, err := llmagent.New(llmagent.Config{
		Name:  "CarbonCaptureResearcher",
		Model: model,
		Instruction: `You are an AI Research Assistant specializing in climate solutions.
Research the current state of 'carbon capture methods'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output *only* the summary.`,
		Description: "Researches carbon capture methods.",
		OutputKey:   "carbon_capture_result",
	})
	if err != nil {
		return err
	}

	// --- 2. Create the ParallelAgent (Runs researchers concurrently) ---
	parallelResearchAgent, err := parallelagent.New(parallelagent.Config{
		AgentConfig: agent.Config{
			Name:        "ParallelWebResearchAgent",
			Description: "Runs multiple research agents in parallel to gather information.",
			SubAgents:   []agent.Agent{researcher1, researcher2, researcher3},
		},
	})
	if err != nil {
		return fmt.Errorf("failed to create parallel agent: %v", err)
	}

	// --- 3. Define the Merger Agent (Runs *after* the parallel agents) ---
	synthesisAgent, err := llmagent.New(llmagent.Config{
		Name:  "SynthesisAgent",
		Model: model,
		Instruction: `You are an AI Assistant responsible for combining research findings into a structured report.
Your primary task is to synthesize the following research summaries, clearly attributing findings to their source areas. Structure your response using headings for each topic. Ensure the report is coherent and integrates the key points smoothly.
**Crucially: Your entire response MUST be grounded *exclusively* on the information provided in the 'Input Summaries' below. Do NOT add any external knowledge, facts, or details not present in these specific summaries.**
**Input Summaries:**

*   **Renewable Energy:**
    {renewable_energy_result}

*   **Electric Vehicles:**
    {ev_technology_result}

*   **Carbon Capture:**
    {carbon_capture_result}

**Output Format:**

## Summary of Recent Sustainable Technology Advancements

### Renewable Energy Findings
(Based on RenewableEnergyResearcher's findings)
[Synthesize and elaborate *only* on the renewable energy input summary provided above.]

### Electric Vehicle Findings
(Based on EVResearcher's findings)
[Synthesize and elaborate *only* on the EV input summary provided above.]

### Carbon Capture Findings
(Based on CarbonCaptureResearcher's findings)
[Synthesize and elaborate *only* on the carbon capture input summary provided above.]

### Overall Conclusion
[Provide a brief (1-2 sentence) concluding statement that connects *only* the findings presented above.]

Output *only* the structured report following this format. Do not include introductory or concluding phrases outside this structure, and strictly adhere to using only the provided input summary content.`,
		Description: "Combines research findings from parallel agents into a structured, cited report, strictly grounded on provided inputs.",
	})
	if err != nil {
		return fmt.Errorf("failed to create synthesis agent: %v", err)
	}

	// --- 4. Create the SequentialAgent (Orchestrates the overall flow) ---
	pipeline, err := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        "ResearchAndSynthesisPipeline",
			Description: "Coordinates parallel research and synthesizes the results.",
			SubAgents:   []agent.Agent{parallelResearchAgent, synthesisAgent},
		},
	})
	if err != nil {
		return fmt.Errorf("failed to create sequential agent pipeline: %v", err)
	}
	// --8<-- [end:init]

	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          pipeline,
		SessionService: sessionService,
	})
	if err != nil {
		return fmt.Errorf("failed to create runner: %v", err)
	}

	session, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  userID,
	})
	if err != nil {
		return fmt.Errorf("failed to create session: %v", err)
	}

	userMsg := &genai.Content{
		Parts: []*genai.Part{{Text: prompt}},
		Role:  string(genai.RoleUser),
	}

	fmt.Printf("Running Research & Synthesis Pipeline for query: %q\n---\n", prompt)
	researcherNames := map[string]bool{
		"RenewableEnergyResearcher": true,
		"EVResearcher":              true,
		"CarbonCaptureResearcher":   true,
	}
	synthesisAgentName := "SynthesisAgent"

	for event, err := range r.Run(ctx, userID, session.Session.ID(), userMsg, agent.RunConfig{
		StreamingMode: agent.StreamingModeNone,
	}) {
		if err != nil {
			return fmt.Errorf("error during agent execution: %v", err)
		}

		if _, ok := researcherNames[event.Author]; ok {
			fmt.Printf("    -> Intermediate Result from %s:\n", event.Author)
			for _, p := range event.Content.Parts {
				fmt.Print(p.Text)
			}
			fmt.Println()
		} else if event.Author == synthesisAgentName {
			fmt.Printf("\n<<< Final Synthesized Response (from %s):\n", event.Author)
			for _, p := range event.Content.Parts {
				fmt.Print(p.Text)
			}
			fmt.Println()
		}
	}
	fmt.Println("\n---\nPipeline finished.")
	return nil
}
