# Go Quickstart for ADK

This guide shows you how to get up and running with Agent Development Kit
for Go. Before you start, make sure you have the following installed:

*   Go 1.25 or later
*   ADK Go v2.0.0 or later

!!! tip "What's new in ADK Go 2.0"

    ADK Go 2.0 introduces graph-based workflow agents, parallel and loop
    execution primitives, and Human-in-the-Loop tool confirmation. See the
    [ADK 2.0 release page](/2.0/) for the full list of new features and
    migration guidance.

## Create an agent project

Create an agent project with the following files and directory structure:

```none
my_agent/
    agent.go    # main agent code
    .env        # macOS/Linux settings; Command Prompt uses env.bat
```

PowerShell users set the API key in the current terminal instead of a file.

??? tip "Create this project structure using the command line"

    === "Windows PowerShell"

        ```powershell
        New-Item -ItemType Directory -Path my_agent
        New-Item -ItemType File -Path my_agent\agent.go
        ```

    === "Windows Command Prompt"

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
[Google Search tool](/integrations/google-search/). Add the
following code to the `my_agent/agent.go` file in your project directory:

```go title="my_agent/agent.go"
package main

import (
	"context"
	"log"
	"os"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/llmagent"
	"google.golang.org/adk/v2/cmd/launcher"
	"google.golang.org/adk/v2/cmd/launcher/full"
	"google.golang.org/adk/v2/model/gemini"
	"google.golang.org/adk/v2/tool"
	"google.golang.org/adk/v2/tool/geminitool"
	"google.golang.org/genai"
)

func main() {
	ctx := context.Background()

	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
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

Initialize your module, add ADK Go 2.0 as a pinned dependency, then let `go mod
tidy` resolve the remaining packages based on the `import` statements in your
agent code file:

```console
cd my_agent
go mod init my-agent/main
go get google.golang.org/adk/v2
go mod tidy
```

### Set your API key

This project uses the Gemini API, which requires an API key. If you
don't already have Gemini API key, create a key in Google AI Studio on the
[API Keys](https://aistudio.google.com/app/apikey) page.

From the `my_agent` directory, set your API key using the instructions for
your terminal. Run the agent from the same terminal so it inherits the key.

=== "MacOS / Linux"

    ```bash title="Update: my_agent/.env"
    echo 'export GOOGLE_API_KEY="YOUR_API_KEY"' > .env
    source .env
    ```

=== "Windows PowerShell"

    ```powershell
    $env:GOOGLE_API_KEY = "YOUR_API_KEY"
    ```

    Set the variable directly in PowerShell. Running `env.bat` starts a
    separate process and does not set the variable in your PowerShell session.

=== "Windows Command Prompt"

    ```console title="Update: my_agent/env.bat"
    echo set "GOOGLE_API_KEY=YOUR_API_KEY" > env.bat
    call env.bat
    ```

If you open a new terminal, load the key again: run `source .env` in
macOS/Linux, repeat the assignment in PowerShell, or run `env.bat` in Command
Prompt from the `my_agent` directory.

??? tip "Using other AI models with ADK"
    ADK supports the use of many generative AI models. For more
    information on configuring other models in ADK agents, see
    [Models & Authentication](/agents/models).


## Run your agent

You can run your ADK agent using the interactive command-line interface
you defined or the ADK web user interface provided by
the ADK Go command line tool. Both these options allow you to test and
interact with your agent.

### Run with command-line interface

Run your agent using the following Go command:

```console title="Run from: my_agent/ directory"
go run agent.go
```

![adk-run.png](/assets/adk-run.png)

### Run with web interface

Run your agent with the ADK web interface using the following Go command:

```console title="Run from: my_agent/ directory"
go run agent.go web api webui
```

This command starts a web server with a chat interface for your agent. You can
access the web interface at `http://localhost:8080`. Select your agent at the
upper left corner and type a request.

![adk-web-dev-ui-chat.png](/assets/adk-web-dev-ui-chat.png)

!!! warning "Caution: ADK Web for development only"

    ADK Web is ***not meant for use in production deployments***. You should
    use ADK Web for development and debugging purposes only.

## Next: Build your agent

Now that you have ADK installed and your first agent running, try building
your own agent with our build guides:

*   [Build your agent](/tutorials/)
*   [Build graph-based workflows](/graphs/)
*   [ADK Go workflow agents](/agents/workflow-agents/)
