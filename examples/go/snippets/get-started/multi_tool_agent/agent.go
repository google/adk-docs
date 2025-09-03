package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"google.com/adk/agent"
	"google.com/adk/session"
	"google.com/adk/tool"
)

func main() {
	if err := run(); err != nil {
		log.Fatal(err)
	}
}

func run() error {
	a, err := agent.New(
		agent.WithName("weather_time_agent"),
		agent.WithModel("gemini-2.0-flash"),
		agent.WithDescription("Agent to answer questions about the time and weather in a city."),
		agent.WithInstruction("You are a helpful agent who can answer user questions about the time and weather in a city."),
		agent.WithTools(
			tool.MustNew(getWeather),
			tool.MustNew(getCurrentTime),
		),
	)
	if err != nil {
		return fmt.Errorf("failed to create agent: %w", err)
	}

	s, err := session.New(a)
	if err != nil {
		return fmt.Errorf("failed to create session: %w", err)
	}
	defer s.Close()

	scanner := bufio.NewScanner(os.Stdin)
	fmt.Println("Chat with the agent (type 'quit' to exit).")
	for {
		fmt.Print("> ")
		if !scanner.Scan() {
			break
		}
		input := scanner.Text()
		if strings.ToLower(input) == "quit" {
			break
		}

		output, err := s.Send(input)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			continue
		}
		fmt.Println(output)
	}

	if err := scanner.Err(); err != nil {
		return fmt.Errorf("scanner error: %w", err)
	}

	return nil
}

// getWeather retrieves the current weather report for a specified city.
//
// city: The name of the city for which to retrieve the weather report.
func getWeather(city string) map[string]string {
	if strings.ToLower(city) == "new york" {
		return map[string]string{
			"status": "success",
			"report": "The weather in New York is sunny with a temperature of 25 degrees Celsius (77 degrees Fahrenheit).",
		}
	}
	return map[string]string{
		"status":        "error",
		"error_message": fmt.Sprintf("Weather information for '%s' is not available.", city),
	}
}

// getCurrentTime returns the current time in a specified city.
//
// city: The name of the city for which to retrieve the current time.
func getCurrentTime(city string) map[string]string {
	loc, err := time.LoadLocation(strings.ReplaceAll(city, " ", "_"))
	if err != nil {
		// Fallback for "New York"
		if strings.ToLower(city) == "new york" {
			loc, err = time.LoadLocation("America/New_York")
			if err != nil {
				return map[string]string{
					"status":        "error",
					"error_message": fmt.Sprintf("Could not load timezone information for %s.", city),
				}
			}
		} else {
			return map[string]string{
				"status":        "error",
				"error_message": fmt.Sprintf("Sorry, I don't have timezone information for %s.", city),
			}
		}
	}

	report := fmt.Sprintf("The current time in %s is %s", city, time.Now().In(loc).Format("2006-01-02 15:04:05 MST"))
	return map[string]string{
		"status": "success",
		"report": report,
	}
}
