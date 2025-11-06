package main

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"strings"

	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/cmd/launcher/adk"
	"google.golang.org/adk/cmd/launcher/web"
	"google.golang.org/adk/cmd/launcher/web/a2a"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/server/restapi/services"
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
	Nums []int `json:"nums"`
}

func checkPrimeTool(tc tool.Context, args checkPrimeToolArgs) string {
	var primes []int
	for _, num := range args.Nums {
		if isPrime(num) {
			primes = append(primes, num)
		}
	}
	if len(primes) == 0 {
		return "No prime numbers found."
	}
	var primeStrings []string
	for _, p := range primes {
		primeStrings = append(primeStrings, strconv.Itoa(p))
	}
	return fmt.Sprintf("%s are prime numbers.", strings.Join(primeStrings, ", "))
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
	launcher := web.NewLauncher(a2a.NewLauncher())
	_, err = launcher.Parse([]string{
		"--port", strconv.Itoa(port),
		"a2a", "--a2a_agent_url", "http://localhost:" + strconv.Itoa(port),
	})
	if err != nil {
		log.Fatalf("launcher.Parse() error = %v", err)
	}

	// Create ADK config
	config := &adk.Config{
		AgentLoader:    services.NewSingleAgentLoader(primeAgent),
		SessionService: session.InMemoryService(),
	}

	log.Printf("Starting A2A prime checker server on port %d\n", port)
	// Run launcher
	if err := launcher.Run(context.Background(), config); err != nil {
		log.Fatalf("launcher.Run() error = %v", err)
	}
}

// --8<-- [end:a2a-launcher]
