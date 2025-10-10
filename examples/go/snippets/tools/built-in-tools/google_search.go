package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/geminitool"
	"google.golang.org/genai"
)

func createSearchAgent(ctx context.Context) (agent.Agent, error) {
	model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
	if err != nil {
		return nil, fmt.Errorf("failed to create model: %v", err)
	}

	return llmagent.New(llmagent.Config{
		Name:        "basic_search_agent",
		Model:       model,
		Description: "Agent to answer questions using Google Search.",
		Instruction: "I can answer your questions by searching the web. Just ask me anything!",
		Tools:       []tool.Tool{geminitool.GoogleSearch{}},
	})
}

const (
	userID  = "user1234"
	appName = "Google Search_agent"
)

func callAgent(ctx context.Context, a agent.Agent, prompt string) error {
	sessionService := session.InMemoryService()
	session, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: appName,
		UserID:  userID,
	})
	if err != nil {
		return fmt.Errorf("failed to create the session service: %v", err)
	}

	config := runner.Config{
		AppName:        appName,
		Agent:          a,
		SessionService: sessionService,
	}
	r, err := runner.New(config)
	if err != nil {
		return fmt.Errorf("failed to create the runner: %v", err)
	}

	sessionID := session.Session.ID()
	userMsg := &genai.Content{
		Parts: []*genai.Part{{Text: prompt}},
		Role:  string(genai.RoleUser),
	}

	// The r.Run method streams events and errors.
	// The loop iterates over the results, handling them as they arrive.
	for event, err := range r.Run(ctx, userID, sessionID, userMsg, &agent.RunConfig{
		StreamingMode: agent.StreamingModeSSE,
	}) {
		if err != nil {
			fmt.Printf("\nAGENT_ERROR: %v\n", err)
		} else {
			for _, p := range event.LLMResponse.Content.Parts {
				fmt.Print(p.Text)
			}
		}
	}
	return nil
}

func main() {
	agent, err := createSearchAgent(context.Background())
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}
	fmt.Println("Agent created:", agent.Name())
	prompt := "what's the latest ai news?"
	fmt.Printf("\nPrompt: %s\nResponse: ", prompt)
	if err := callAgent(context.Background(), agent, prompt); err != nil {
		log.Fatalf("Error calling agent: %v", err)
	}
	fmt.Println("\n---")
}
