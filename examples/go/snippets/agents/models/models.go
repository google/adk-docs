package main

import (
	"context"
	"log"

	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/llm/gemini"
	"google.golang.org/genai"
)


func main() {
	ctx := context.Background()
	// --8<-- [start:gemini-example]
	// --- Example using a stable Gemini Flash model ---
	modelFlash, err := gemini.NewModel(ctx, "gemini-2.0-flash", &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("failed to create model: %v", err)
	}
	agentGeminiFlash, err := llmagent.New(llmagent.Config{
		// Use the latest stable Flash model identifier
		Model:       modelFlash,
		Name:        "gemini_flash_agent",
		Instruction: "You are a fast and helpful Gemini assistant.",
		// ... other agent parameters
	})
	if err != nil {
		log.Fatalf("failed to create agent: %v", err)
	}

	// --- Example using a powerful Gemini Pro model ---
	// Note: Always check the official Gemini documentation for the latest model names,
	// including specific preview versions if needed. Preview models might have
	// different availability or quota limitations.
	modelPro, err := gemini.NewModel(ctx, "gemini-2.5-pro-preview-03-25", &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("failed to create model: %v", err)
	}
	agentGeminiPro, err := llmagent.New(llmagent.Config{
		// Use the latest generally available Pro model identifier
		Model:       modelPro,
		Name:        "gemini_pro_agent",
		Instruction: "You are a powerful and knowledgeable Gemini assistant.",
		// ... other agent parameters
	})
	if err != nil {
		log.Fatalf("failed to create agent: %v", err)
	}
	// --8<-- [end:gemini-example]
	log.Println("agentGeminiFlash created successfully.")
	log.Println("agentGeminiPro created successfully.")
	_, _ = agentGeminiFlash, agentGeminiPro // Avoid unused variable error
}
