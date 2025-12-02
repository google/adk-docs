# Go Quickstart for ADK

This guide shows you how to get up and running with Agent Development Kit
for Go. Before you start, make sure you have the following installed:

*   Go 1.24.4 or later
*   ADK Go v0.2.0 or later

## Create an agent project

Create an agent project with the following files and directory structure:

```none
my_agent/
    agent.go    # main agent code
    .env        # API keys or project IDs
```

??? tip "Create this project structure using the command line"

    === "Windows"

        ```console
        mkdir my_agent\
        type nul > my_agent\agent.go
        type nul > my_agent\env.bat
        ```

    === "MacOS / Linux"

        ```bash
        mkdir -p my_agent/ && \
            touch my_agent/agent.go && \
            touch my_agent/.env
        ```

### Define the agent code

Create the code for a basic agent that uses the built-in
[Google Search tool](/adk-docs/tools/built-in-tools/#google-search). Add the
following code to the `my_agent/agent.go` file in your project directory:

```go title="my_agent/agent.go"
package main

import (
	"context"
	"log"
	"os"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/cmd/launcher"
	"google.golang.org/adk/cmd/launcher/full"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/geminitool"
	"google.golang.org/genai"
)

func main() {
	ctx := context.Background()

	model, err := gemini.NewModel(ctx, "gemini-3-pro-preview", &genai.ClientConfig{
		APIKey: os.Getenv("GOOGLE_API_KEY"),
	})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	timeAgent, err := llmagent.New(llmagent.Config{
		Name:        "hello_time_agent",
		Model:       model,
		Description: "Tells the current time in a specified city.",
		Instruction: "You are a helpful assistant that tells the current time in a city.",
		Tools: []tool.Tool{
			geminitool.GoogleSearch{},
		},
	})
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	config := &launcher.Config{
		AgentLoader: agent.NewSingleLoader(timeAgent),
	}

	l := full.NewLauncher()
	if err = l.Execute(ctx, config, os.Args[1:]); err != nil {
		log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
	}
}
```

### Configure project and dependencies

Use the `go mod` command to initialize the project modules and install the
required packages based on the `import` statement in your agent code file:

```console
go mod init my-agent/main
go mod tidy
```

### Set your API key

This project uses the Gemini API, which requires an API key. If you
don't already have Gemini API key, create a key in Google AI Studio on the
[API Keys](https://aistudio.google.com/app/apikey) page.

In a terminal window, write your API key into the `.env` or `env.bat` file of
your project to set environment variables:

=== "MacOS / Linux"

    ```bash title="Update: my_agent/.env"
    echo 'export GOOGLE_API_KEY="YOUR_API_KEY"' > .env
    ```

=== "Windows"

    ```console title="Update: my_agent/env.bat"
    echo 'set GOOGLE_API_KEY="YOUR_API_KEY"' > env.bat
    ```

??? tip "Using other AI models with ADK"
    ADK supports the use of many generative AI models. For more
    information on configuring other models in ADK agents, see
    [Models & Authentication](/adk-docs/agents/models).


## Run your agent

You can run your ADK agent using the interactive command-line interface
you defined or the ADK web user interface provided by
the ADK Go command line tool. Both these options allow you to test and
interact with your agent.

### Run with command-line interface

Run your agent using the following Go command:

```console title="Run from: my_agent/ directory"
# Remember to load keys and settings: source .env OR env.bat
go run agent.go
```

![adk-run.png](/adk-docs/assets/adk-run.png)

### Run with web interface

Run your agent with the ADK web interface using the following Go command:

```console title="Run from: my_agent/ directory"
# Remember to load keys and settings: source .env OR env.bat
go run agent.go web api webui
```

This command starts a web server with a chat interface for your agent. You can
access the web interface at (http://localhost:8080). Select your agent at the
upper left corner and type a request.

![adk-web-dev-ui-chat.png](/adk-docs/assets/adk-web-dev-ui-chat.png)

!!! warning "Caution: ADK Web for development only"

    ADK Web is ***not meant for use in production deployments***. You should
    use ADK Web for development and debugging purposes only.

## Next: Build your agent

Now that you have ADK installed and your first agent running, try building
your own agent with our build guides:

*  [Build your agent](/adk-docs/tutorials/)
