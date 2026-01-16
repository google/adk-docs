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
	"strconv"
	"strings"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/cmd/launcher"
	"google.golang.org/adk/cmd/launcher/web"
	"google.golang.org/adk/cmd/launcher/web/a2a"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/functiontool"
	"google.golang.org/genai"
)

// isPrime checks if a number is prime.
func isPrime(n int) bool {
	if n <= 1 {
		return false
	}
	for i := 2; i*i <= n; i++ {
		if n%i == 0 {
			return false
		}
	}
	return true
}

type checkPrimeToolArgs struct {
	Nums []int `json:"nums" jsonschema:"A list of numbers to check for primality."`
}

func checkPrimeTool(tc tool.Context, args checkPrimeToolArgs) (string, error) {
	var primes []int
	for _, num := range args.Nums {
		if isPrime(num) {
			primes = append(primes, num)
		}
	}
	if len(primes) == 0 {
		return "", fmt.Errorf("no prime numbers found")
	}
	var primeStrings []string
	for _, p := range primes {
		primeStrings = append(primeStrings, strconv.Itoa(p))
	}
	return fmt.Sprintf("%s are prime numbers.", strings.Join(primeStrings, ", ")), nil
}

// --8<-- [start:a2a-launcher]
func main() {
	ctx := context.Background()
	primeTool, err := functiontool.New(functiontool.Config{
		Name:        "prime_checking",
		Description: "Check if numbers in a list are prime using efficient mathematical algorithms",
	}, checkPrimeTool)
	if err != nil {
		log.Fatalf("Failed to create prime_checking tool: %v", err)
	}

	model, err := gemini.NewModel(ctx, "gemini-2.0-flash", &genai.ClientConfig{})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	primeAgent, err := llmagent.New(llmagent.Config{
		Name:        "check_prime_agent",
		Description: "check prime agent that can check whether numbers are prime.",
		Instruction: `
			You check whether numbers are prime.
			When checking prime numbers, call the check_prime tool with a list of integers. Be sure to pass in a list of integers. You should never pass in a string.
			You should not rely on the previous history on prime results.
    `,
		Model: model,
		Tools: []tool.Tool{primeTool},
	})
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	// Create launcher. The a2a.NewLauncher() will dynamically generate the agent card.
	port := 8001
	webLauncher := web.NewLauncher(a2a.NewLauncher())
	_, err = webLauncher.Parse([]string{
		"--port", strconv.Itoa(port),
		"a2a", "--a2a_agent_url", "http://localhost:" + strconv.Itoa(port),
	})
	if err != nil {
		log.Fatalf("launcher.Parse() error = %v", err)
	}

	// Create ADK config
	config := &launcher.Config{
		AgentLoader:    agent.NewSingleLoader(primeAgent),
		SessionService: session.InMemoryService(),
	}

	log.Printf("Starting A2A prime checker server on port %d\n", port)
	// Run launcher
	if err := webLauncher.Run(context.Background(), config); err != nil {
		log.Fatalf("webLauncher.Run() error = %v", err)
	}
}

// --8<-- [end:a2a-launcher]
