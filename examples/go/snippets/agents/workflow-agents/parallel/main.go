package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/agent/workflowagents/parallelagent"
	"google.golang.org/adk/agent/workflowagents/sequentialagent"
	"google.golang.org/adk/llm/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/sessionservice"
	"google.golang.org/genai"
)

const (
	appName   = "ParallelResearchAgent"
	userID    = "test_user_789"
	modelName = "gemini-1.5-flash"
)

func main() {
	if err := runAgent("Research the latest trends in renewable energy, electric vehicles, and carbon capture."); err != nil {
		log.Fatalf("Agent execution failed: %v", err)
	}
}

func runAgent(prompt string) error {
	ctx := context.Background()

	// init_start
	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return fmt.Errorf("failed to create model: %v", err)
	}

	createResearcherAgent := func(topic, outputKey string) (agent.Agent, error) {
		return llmagent.New(llmagent.Config{
			Name:        fmt.Sprintf("ResearcherAgent-%s", topic),
			Model:       model,
			Description: fmt.Sprintf("Researches the topic of %s.", topic),
			Instruction: fmt.Sprintf("You are a research assistant. Your task is to research the following topic: %s. Summarize your findings.", topic),
		})
	}

	researcher1, err := createResearcherAgent("renewable energy", "renewable_energy_summary")
	if err != nil {
		return err
	}
	researcher2, err := createResearcherAgent("electric vehicle technology", "ev_summary")
	if err != nil {
		return err
	}
	researcher3, err := createResearcherAgent("carbon capture methods", "carbon_capture_summary")
	if err != nil {
		return err
	}

	parallelResearchAgent, err := parallelagent.New(parallelagent.Config{
		AgentConfig: agent.Config{
			Name:        "ParallelResearcher",
			Description: "Runs multiple researchers concurrently.",
			SubAgents:   []agent.Agent{researcher1, researcher2, researcher3},
		},
	})
	if err != nil {
		return fmt.Errorf("failed to create parallel agent: %v", err)
	}

	summaryAgent, err := llmagent.New(llmagent.Config{
		Name:        "SummaryAgent",
		Model:       model,
		Description: "Summarizes the research findings from all researchers.",
		Instruction: `You are a summary assistant.
Combine the following research summaries into a single, coherent report:
- Renewable Energy: {renewable_energy_summary}
- Electric Vehicles: {ev_summary}
- Carbon Capture: {carbon_capture_summary}`,
	})
	if err != nil {
		return fmt.Errorf("failed to create summary agent: %v", err)
	}

	pipeline, err := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{
			Name:        "ResearchPipeline",
			Description: "Runs a parallel research task and then summarizes the results.",
			SubAgents:   []agent.Agent{parallelResearchAgent, summaryAgent},
		},
	})
	if err != nil {
		return fmt.Errorf("failed to create sequential agent pipeline: %v", err)
	}
	// init_end

	sessionService := sessionservice.Mem()
	r, err := runner.New(&runner.Config{
		AppName:        appName,
		Agent:          pipeline,
		SessionService: sessionService,
	})
	if err != nil {
		return fmt.Errorf("failed to create runner: %v", err)
	}

	session, err := sessionService.Create(ctx, &sessionservice.CreateRequest{
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

	fmt.Printf("Running parallel research pipeline for prompt: %q\n---\n", prompt)
	for event, err := range r.Run(ctx, userID, session.Session.ID().SessionID, userMsg, nil) {
		if err != nil {
			return fmt.Errorf("error during agent execution: %v", err)
		}
		for _, p := range event.LLMResponse.Content.Parts {
			fmt.Print(p.Text)
		}
	}
	fmt.Println("\n---\nPipeline finished.")
	return nil
}
