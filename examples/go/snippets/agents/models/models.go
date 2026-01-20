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
	"log"

	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/model/gemini"
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
	// --8<-- [end:gemini-example]

	// --8<-- [start:gemini-example-2]
	// --- Example using a powerful Gemini Pro model ---
	// Note: Always check the official Gemini documentation for the latest model names,
	// including specific preview versions if needed. Preview models might have
	// different availability or quota limitations.
	modelPro, err := gemini.NewModel(ctx, "gemini-2.5-pro", &genai.ClientConfig{})
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
	// --8<-- [end:gemini-example-2]
	log.Println("agentGeminiFlash created successfully.")
	log.Println("agentGeminiPro created successfully.")
	_, _ = agentGeminiFlash, agentGeminiPro // Avoid unused variable error
}
