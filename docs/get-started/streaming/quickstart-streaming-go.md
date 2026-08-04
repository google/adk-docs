# Build a streaming agent with Go

With this quickstart, you'll learn to create a simple agent and use ADK Streaming to enable voice and video communication with it that is low-latency and bidirectional. We will install ADK, set up a basic "Google Search" agent, and run a local server to interact with it using the embedded ADK Web UI.

**Note:** This guide assumes you have experience using a terminal in Linux, Mac, or Windows environments.

## Supported models for voice/video streaming

In order to use voice/video streaming in ADK, you will need to use Gemini models that support the Live API. 

You can find the complete **model ID(s)** that support the Gemini Live API in the documentation:

- [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
- [Agent Platform: Gemini Live API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/2-5-flash-live-api)


## 1. Set up the platform

Choose a platform from either Google AI Studio or Google Cloud Agent Platform (Vertex AI):

### Option 1: Google AI Studio

1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Set the environment variables in your terminal:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
```

### Option 2: Vertex AI / Agent Platform

1. Set up a [Google Cloud project](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp).
2. Set up the [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local) and authenticate via terminal:

```bash
gcloud auth login
```

3. Find your active Google Cloud Project ID with:

```bash
gcloud config get-value project
```

4. [Enable the Agent Platform API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com).
5. Set the environment variables in your terminal, updating your project ID and location:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
export GOOGLE_CLOUD_LOCATION=us-central1
```

## 2. Setup Environment & Install ADK

Create a new directory for your project and initialize a Go module:

```bash
mkdir adk-streaming
cd adk-streaming
go mod init adk-streaming
```

Install the ADK Go SDK:

```bash
go get google.golang.org/adk@latest
```

## 3. Project Structure

Create a single `main.go` file. You do **not** need to copy or host static assets manually since the ADK launcher packages the Web UI for you.

```text
adk-streaming/
└── main.go
```

## 4. Create the Agent and Launcher

Copy-paste the following code into your `main.go` file.

```go
package main

import (
	"context"
	"log"
	"os"

	"google.golang.org/genai"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/cmd/launcher"
	"google.golang.org/adk/cmd/launcher/full"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/geminitool"
)

func main() {
	ctx := context.Background()

	// Initialize the Gemini model
	// Configured to dynamically support Google AI Studio or Vertex AI backends
	var cfg *genai.ClientConfig
	if apiKey := os.Getenv("GOOGLE_API_KEY"); apiKey != "" {
		cfg = &genai.ClientConfig{APIKey: apiKey}
	}

	// Set model ID dynamically based on the platform option chosen:
	// - For Google AI Studio (Gemini API), use "gemini-2.5-flash-native-audio-preview-12-2025"
	// - For Vertex AI (Agent Platform), use "gemini-live-2.5-flash-native-audio"
	modelID := "gemini-2.5-flash-native-audio-preview-12-2025"
	if os.Getenv("GOOGLE_GENAI_USE_VERTEXAI") == "TRUE" {
		modelID = "gemini-live-2.5-flash-native-audio"
	}
	model, err := gemini.NewModel(ctx, modelID, cfg)
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	// Define the agent
	a, err := llmagent.New(llmagent.Config{
		Name:        "bidi-demo",
		Model:       model,
		Description: "Agent optimized for real-time bidirectional streaming.",
		Instruction: "You are a helpful voice assistant. Answer questions concisely.",
		Tools: []tool.Tool{
			geminitool.GoogleSearch{},
		},
	})
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	// Configure the launcher with the agent loader
	config := &launcher.Config{
		AgentLoader: agent.NewSingleLoader(a),
	}

	// Create a full launcher with built-in web and console capabilities
	l := full.NewLauncher()
	if err = l.Execute(ctx, config, os.Args[1:]); err != nil {
		log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
	}
}
```

## 5. Try the agent

Run the application with the `web`, `api`, and `webui` arguments. This boots up the web server, registers the REST API backend, and serves the ADK Web UI dashboard simultaneously:

```bash
go run main.go web api webui
```

Once the server starts, open the Web UI in your browser:

```text
http://localhost:8080/ui/
```

### Try with voice and video

Click the microphone button to enable voice input, and ask questions. The agent will respond in real-time via audio.
If you have a camera enabled, you can also stream video and ask "What do you see?".

### Caveat

- You cannot use text chat with the native-audio models if the model is configured for audio-only input/output in the connection. However, the live API supports both.
- Ensure you use earphones to prevent echo when using voice input/output.

Congratulations! You've successfully created and interacted with your first Streaming agent using ADK in Go!
