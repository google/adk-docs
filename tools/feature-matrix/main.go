package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/google/generative-ai-go/genai"
	"google.golang.org/api/option"

	"github.com/charmbracelet/log"
)

func extractLocal(root string) (string, error) {
	var content strings.Builder
	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() && strings.HasSuffix(info.Name(), ".md") {
			fileContent, err := os.ReadFile(path)
			if err != nil {
				// log error but continue
				return nil
			}
			content.Write(fileContent)
			content.WriteString("\n\n")
		}
		return nil
	})
	if err != nil {
		return "", err
	}
	return content.String(), nil
}

func main() {
	ctx := context.Background()
	// Access your API key as an environment variable (see "Set up your API key" above)
	client, err := genai.NewClient(ctx, option.WithAPIKey(os.Getenv("GEMINI_API_KEY")))
	if err != nil {
		log.Fatal(err)
	}
	defer client.Close()

	// For text-only input, use the gemini-pro model
	model := client.GenerativeModel("gemini-2.5-pro")
	model.SetTemperature(0.9)
	model.SetTopP(0.95)
	model.SetTopK(40)

	log.Infof("reading prompt")
	promptBytes, err := os.ReadFile("prompt.md")
	if err != nil {
		log.Fatalf("cannot read prompt from filesystem: %s", err)
	}

	log.Infof("reading starting matrix starting place")
	outputBytes, err := os.ReadFile("start.md")
	if err != nil {
		log.Fatalf("cannot read example from filesystem: %s", err)
	}

	command := string(promptBytes) + string(outputBytes)

	log.Infof("Retrieving adk-docs")
	documentationContent, err := extractLocal("../../docs")
	if err != nil {
		log.Fatalf("cannot retrieve and process content from adk-docs repo: %s", err)
	}

	prompt := command + "\n\n" + documentationContent

	log.Infof("sending the request to the model")
	resp, err := model.GenerateContent(ctx, genai.Text(prompt))
	if err != nil {
		log.Fatalf("did not get a valid response back from teh model", err)
	}

	for i, cand := range resp.Candidates {
		if cand.Content != nil {
			for _, part := range cand.Content.Parts {
				if txt, ok := part.(genai.Text); ok {
					if i == 0 { // Only process the first candidate for the PR
						outputDir := "../../docs/features"
						if err := os.MkdirAll(outputDir, 0755); err != nil {
							log.Fatalf("failed to create output directory: %v", err)
						}
						filename := fmt.Sprintf("%s/index.md", outputDir)
						err := os.WriteFile(filename, []byte(txt), 0644)
						if err != nil {
							log.Fatalf("failed to write output file: %v", err)
						}
						log.Infof("wrote output to %s", filename)
					}
				}
			}
		}
	}
}
