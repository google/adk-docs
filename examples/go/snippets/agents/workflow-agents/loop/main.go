package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/agent/workflowagents/loopagent"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/genai"
)

const (
	appName   = "DocImprovAgent"
	userID    = "test_user_123"
	modelName = "gemini-2.5-flash"
)

// --8<-- [start:init]
// ExitLoopArgs defines the (empty) arguments for the ExitLoop tool.
type ExitLoopArgs struct{}

// ExitLoopResults defines the output of the ExitLoop tool.
type ExitLoopResults struct {
	Status string `json:"status"`
}

// ExitLoop is a tool that signals the loop to terminate by setting Escalate to true.
func ExitLoop(ctx tool.Context, input ExitLoopArgs) ExitLoopResults {
	ctx.Actions().Escalate = true
	return ExitLoopResults{Status: "exiting loop"}
}

func main() {
	if err := runAgent("Write a short document about the benefits of exercise."); err != nil {
		log.Fatalf("Agent execution failed: %v", err)
	}
}

func runAgent(prompt string) error {
	ctx := context.Background()

	model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
	if err != nil {
		return fmt.Errorf("failed to create model: %v", err)
	}

	writerAgent, err := llmagent.New(llmagent.Config{
		Name:        "WriterAgent",
		Model:       model,
		Description: "Generates and refines a document.",
		Instruction: `You are a document writer.
Based on the user's request and any feedback from the critic, write or revise the document.
The current document is:
{document}

Critic's feedback:
{feedback}

Rewrite the document to address the feedback. If there is no feedback, write the initial draft.`,
	})
	if err != nil {
		return fmt.Errorf("failed to create writer agent: %v", err)
	}

	exitLoopTool, err := tool.NewFunctionTool(
		tool.FunctionToolConfig{
			Name:        "ExitLoop",
			Description: "Signals the loop to terminate when the document is well-written and complete.",
		},
		ExitLoop,
	)
	if err != nil {
		return fmt.Errorf("failed to create exit loop tool: %v", err)
	}

	criticAgent, err := llmagent.New(llmagent.Config{
		Name:        "CriticAgent",
		Model:       model,
		Description: "Critiques the document and decides if it's good enough.",
		Instruction: `You are a document critic.
Review the following document:
{document}

If the document is well-written and complete, call the "ExitLoop" tool.
Otherwise, provide constructive feedback for improvement.`,
		Tools: []tool.Tool{exitLoopTool},
	})
	if err != nil {
		return fmt.Errorf("failed to create critic agent: %v", err)
	}

	refinementLoop, err := loopagent.New(loopagent.Config{
		AgentConfig: agent.Config{
			Name:        "RefinementLoop",
			Description: "Iteratively refines a document.",
			SubAgents: []agent.Agent{
				writerAgent,
				criticAgent,
			},
		},
		MaxIterations: 5,
	})
	if err != nil {
		return fmt.Errorf("failed to create loop agent: %v", err)
	}
	// --8<-- [end:init]

	sessionService := session.InMemoryService()
	r, err := runner.New(runner.Config{
		AppName:        appName,
		Agent:          refinementLoop,
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

	fmt.Printf("Running agent loop for prompt: %q\n---\n", prompt)
	for event, err := range r.Run(ctx, userID, session.Session.ID(), userMsg, &agent.RunConfig{
		StreamingMode: agent.StreamingModeSSE,
	}) {
		if err != nil {
			return fmt.Errorf("error during agent execution: %v", err)
		}
		for _, p := range event.LLMResponse.Content.Parts {
			fmt.Print(p.Text)
		}
	}
	fmt.Println("\n---\nLoop finished.")
	return nil
}