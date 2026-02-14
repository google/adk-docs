# Deploy to Cloud Run

Supported in ADKPythonTypeScriptGoJava

[Cloud Run](https://cloud.google.com/run) is a fully managed platform that enables you to run your code directly on top of Google's scalable infrastructure.

To deploy your agent, you can use either the `adk deploy cloud_run` command *(recommended for Python)*, or with `gcloud run deploy` command through Cloud Run.

## Agent sample

For each of the commands, we will reference the `Capital Agent` sample defined on the [LLM agent](https://google.github.io/adk-docs/agents/llm-agents/index.md) page. We will assume it's in a directory (eg: `capital_agent`).

To proceed, confirm that your agent code is configured as follows:

1. Agent code is in a file called `agent.py` within your agent directory.

1. Your agent variable is named `root_agent`.

1. `__init__.py` is within your agent directory and contains `from . import agent`.

1. Your `requirements.txt` file is present in the agent directory.

1. Agent code is in a file called `agent.ts` within your project directory.

1. Your agent variable is named `rootAgent` and is exported.

1. Your `package.json` file is present in the agent directory with `@google/adk` and other dependencies.

1. Your application's entry point (the main package and main() function) is in a single Go file. Using main.go is a strong convention.

1. Your agent instance is passed to a launcher configuration, typically using agent.NewSingleLoader(yourAgent). The adkgo tool uses this launcher to start your agent with the correct services.

1. Your go.mod and go.sum files are present in your project directory to manage dependencies.

Refer to the following section for more details. You can also find a [sample app](https://github.com/google/adk-docs/tree/main/examples/go/cloud-run) in the Github repo.

1. Agent code is in a file called `CapitalAgent.java` within your agent directory.
1. Your agent variable is global and follows the format `public static final BaseAgent ROOT_AGENT`.
1. Your agent definition is present in a static class method.

Refer to the following section for more details. You can also find a [sample app](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run) in the Github repo.

## Environment variables

Set your environment variables as described in the [Setup and Installation](https://google.github.io/adk-docs/get-started/installation/index.md) guide.

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # Or your preferred location
export GOOGLE_GENAI_USE_VERTEXAI=True
```

*(Replace `your-project-id` with your actual GCP project ID)*

Alternatively you can also use an API key from AI Studio

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # Or your preferred location
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY=your-api-key
```

*(Replace `your-project-id` with your actual GCP project ID and `your-api-key` with your actual API key from AI Studio)*

## Prerequisites

1. You should have a Google Cloud project. You need to know your:
   1. Project name (i.e. "my-project")
   1. Project location (i.e. "us-central1")
   1. Service account (i.e. "1234567890-compute@developer.gserviceaccount.com")
   1. GOOGLE_API_KEY

## Secret

Please make sure you have created a secret which can be read by your service account.

### Entry for GOOGLE_API_KEY secret

You can create your secret manually or use CLI:

```bash
echo "<<put your GOOGLE_API_KEY here>>" | gcloud secrets create GOOGLE_API_KEY --project=my-project --data-file=-
```

### Permissions to read

You should give appropriate permission for you service account to read this secret.

```bash
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY --member="serviceAccount:1234567890-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --project=my-project
```

## Deployment payload

When you deploy your ADK agent workflow to Google Cloud Run, the following content is uploaded to the service:

- Your ADK agent code
- Any dependencies declared in your ADK agent code
- ADK API server code version used by your agent

The default deployment *does not* include the ADK web user interface libraries, unless you specify it as deployment setting, such as the `--with_ui` option for `adk deploy cloud_run` command.

## Deployment commands

### adk CLI

The `adk deploy cloud_run` command deploys your agent code to Google Cloud Run.

Ensure you have authenticated with Google Cloud (`gcloud auth login` and `gcloud config set project <your-project-id>`).

#### Setup environment variables

Optional but recommended: Setting environment variables can make the deployment commands cleaner.

```bash
# Set your Google Cloud Project ID
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

# Set your desired Google Cloud Location
export GOOGLE_CLOUD_LOCATION="us-central1" # Example location

# Set the path to your agent code directory
export AGENT_PATH="./capital_agent" # Assuming capital_agent is in the current directory

# Set a name for your Cloud Run service (optional)
export SERVICE_NAME="capital-agent-service"

# Set an application name (optional)
export APP_NAME="capital_agent_app"
```

#### Command usage

##### Minimal command

```bash
adk deploy cloud_run \
--project=$GOOGLE_CLOUD_PROJECT \
--region=$GOOGLE_CLOUD_LOCATION \
$AGENT_PATH
```

##### Full command with optional flags

```bash
adk deploy cloud_run \
--project=$GOOGLE_CLOUD_PROJECT \
--region=$GOOGLE_CLOUD_LOCATION \
--service_name=$SERVICE_NAME \
--app_name=$APP_NAME \
--with_ui \
$AGENT_PATH
```

##### Arguments

- `AGENT_PATH`: (Required) Positional argument specifying the path to the directory containing your agent's source code (e.g., `$AGENT_PATH` in the examples, or `capital_agent/`). This directory must contain at least an `__init__.py` and your main agent file (e.g., `agent.py`).

##### Options

- `--project TEXT`: (Required) Your Google Cloud project ID (e.g., `$GOOGLE_CLOUD_PROJECT`).
- `--region TEXT`: (Required) The Google Cloud location for deployment (e.g., `$GOOGLE_CLOUD_LOCATION`, `us-central1`).
- `--service_name TEXT`: (Optional) The name for the Cloud Run service (e.g., `$SERVICE_NAME`). Defaults to `adk-default-service-name`.
- `--app_name TEXT`: (Optional) The application name for the ADK API server (e.g., `$APP_NAME`). Defaults to the name of the directory specified by `AGENT_PATH` (e.g., `capital_agent` if `AGENT_PATH` is `./capital_agent`).
- `--agent_engine_id TEXT`: (Optional) If you are using a managed session service via Vertex AI Agent Engine, provide its resource ID here.
- `--port INTEGER`: (Optional) The port number the ADK API server will listen on within the container. Defaults to 8000.
- `--with_ui`: (Optional) If included, deploys the ADK dev UI alongside the agent API server. By default, only the API server is deployed.
- `--temp_folder TEXT`: (Optional) Specifies a directory for storing intermediate files generated during the deployment process. Defaults to a timestamped folder in the system's temporary directory. *(Note: This option is generally not needed unless troubleshooting issues).*
- `--help`: Show the help message and exit.

##### Passing gcloud CLI Arguments

To pass specific gcloud flags through the `adk deploy cloud_run` command, use the double-dash separator (`--`) after the ADK arguments. Any flags (except ADK-managed) following the `--` will be passed directly to the underlying gcloud command.

###### Syntax Example:

```bash
adk deploy cloud_run [ADK_FLAGS] -- [GCLOUD_FLAGS]
```

###### Example:

```bash
adk deploy cloud_run --project=[PROJECT_ID] --region=[REGION] path/to/my_agent    -- --no-allow-unauthenticated --min-instances=2
```

##### Authenticated access

During the deployment process, you might be prompted: `Allow unauthenticated invocations to [your-service-name] (y/N)?`.

- Enter `y` to allow public access to your agent's API endpoint without authentication.
- Enter `N` (or press Enter for the default) to require authentication (e.g., using an identity token as shown in the "Testing your agent" section).

Upon successful execution, the command deploys your agent to Cloud Run and provide the URL of the deployed service.

### gcloud CLI for Python

Alternatively, you can deploy using the standard `gcloud run deploy` command with a `Dockerfile`. This method requires more manual setup compared to the `adk` command but offers flexibility, particularly if you want to embed your agent within a custom [FastAPI](https://fastapi.tiangolo.com/) application.

Ensure you have authenticated with Google Cloud (`gcloud auth login` and `gcloud config set project <your-project-id>`).

#### Project Structure

Organize your project files as follows:

```text
your-project-directory/
├── capital_agent/
│   ├── __init__.py
│   └── agent.py       # Your agent code (see "Agent sample" tab)
├── main.py            # FastAPI application entry point
├── requirements.txt   # Python dependencies
└── Dockerfile         # Container build instructions
```

Create the following files (`main.py`, `requirements.txt`, `Dockerfile`) in the root of `your-project-directory/`.

#### Code files

1. This file sets up the FastAPI application using `get_fast_api_app()` from ADK:

   main.py

   ```python
   import os

   import uvicorn
   from fastapi import FastAPI
   from google.adk.cli.fast_api import get_fast_api_app

   # Get the directory where main.py is located
   AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
   # Example session service URI (e.g., SQLite)
   # Note: Use 'sqlite+aiosqlite' instead of 'sqlite' because DatabaseSessionService requires an async driver
   SESSION_SERVICE_URI = "sqlite+aiosqlite:///./sessions.db"
   # Example allowed origins for CORS
   ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
   # Set web=True if you intend to serve a web interface, False otherwise
   SERVE_WEB_INTERFACE = True

   # Call the function to get the FastAPI app instance
   # Ensure the agent directory name ('capital_agent') matches your agent folder
   app: FastAPI = get_fast_api_app(
       agents_dir=AGENT_DIR,
       session_service_uri=SESSION_SERVICE_URI,
       allow_origins=ALLOWED_ORIGINS,
       web=SERVE_WEB_INTERFACE,
   )

   # You can add more FastAPI routes or configurations below if needed
   # Example:
   # @app.get("/hello")
   # async def read_root():
   #     return {"Hello": "World"}

   if __name__ == "__main__":
       # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
       uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
   ```

   *Note: We specify `agent_dir` to the directory `main.py` is in and use `os.environ.get("PORT", 8080)` for Cloud Run compatibility.*

1. List the necessary Python packages:

   requirements.txt

   ```text
   google-adk
   # Add any other dependencies your agent needs
   ```

1. Define the container image:

   Dockerfile

   ```dockerfile
   FROM python:3.13-slim
   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   RUN adduser --disabled-password --gecos "" myuser && \
       chown -R myuser:myuser /app

   COPY . .

   USER myuser

   ENV PATH="/home/myuser/.local/bin:$PATH"

   CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
   ```

#### Defining Multiple Agents

You can define and deploy multiple agents within the same Cloud Run instance by creating separate folders in the root of `your-project-directory/`. Each folder represents one agent and must define a `root_agent` in its configuration.

Example structure:

```text
your-project-directory/
├── capital_agent/
│   ├── __init__.py
│   └── agent.py       # contains `root_agent` definition
├── population_agent/
│   ├── __init__.py
│   └── agent.py       # contains `root_agent` definition
└── ...
```

#### Deploy using `gcloud`

Navigate to `your-project-directory` in your terminal.

```bash
gcloud run deploy capital-agent-service \
--source . \
--region $GOOGLE_CLOUD_LOCATION \
--project $GOOGLE_CLOUD_PROJECT \
--allow-unauthenticated \
--set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
# Add any other necessary environment variables your agent might need
```

- `capital-agent-service`: The name you want to give your Cloud Run service.
- `--source .`: Tells gcloud to build the container image from the Dockerfile in the current directory.
- `--region`: Specifies the deployment region.
- `--project`: Specifies the GCP project.
- `--allow-unauthenticated`: Allows public access to the service. Remove this flag for private services.
- `--set-env-vars`: Passes necessary environment variables to the running container. Ensure you include all variables required by ADK and your agent (like API keys if not using Application Default Credentials).

`gcloud` will build the Docker image, push it to Google Artifact Registry, and deploy it to Cloud Run. Upon completion, it will output the URL of your deployed service.

For a full list of deployment options, see the [`gcloud run deploy` reference documentation](https://cloud.google.com/sdk/gcloud/reference/run/deploy).

### adk CLI

The `adk deploy cloud_run` command deploys your agent code to Google Cloud Run.

Ensure you have authenticated with Google Cloud (`gcloud auth login` and `gcloud config set project <your-project-id>`).

#### Setup environment variables

Optional but recommended: Setting environment variables can make the deployment commands cleaner.

```bash
# Set your Google Cloud Project ID
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

# Set your desired Google Cloud Location
export GOOGLE_CLOUD_LOCATION="us-central1" # Example location

# Set a name for your Cloud Run service (optional)
export SERVICE_NAME="capital-agent-service"
```

#### Command usage

This deployment command should be run from the directory of your agent code, where your `package.json` file is located.

##### Minimal command

```bash
npx adk deploy cloud_run \
--project=$GOOGLE_CLOUD_PROJECT \
--region=$GOOGLE_CLOUD_LOCATION
```

##### Full command with optional flags

```bash
npx adk deploy cloud_run \
--project=$GOOGLE_CLOUD_PROJECT \
--region=$GOOGLE_CLOUD_LOCATION \
--service_name=$SERVICE_NAME \
--with_ui
```

##### Options

- `--project TEXT`: (Required) Your Google Cloud project ID (e.g., `$GOOGLE_CLOUD_PROJECT`).
- `--region TEXT`: (Required) The Google Cloud location for deployment (e.g., `$GOOGLE_CLOUD_LOCATION`, `us-central1`).
- `--service_name TEXT`: (Optional) The name for the Cloud Run service (e.g., `$SERVICE_NAME`). Defaults to `adk-default-service-name`.
- `--port INTEGER`: (Optional) The port number the ADK API server will listen on within the container. Defaults to 8000.
- `--with_ui`: (Optional) If included, deploys the ADK dev UI alongside the agent API server. By default, only the API server is deployed.
- `--temp_folder TEXT`: (Optional) Specifies a directory for storing intermediate files generated during the deployment process. Defaults to a timestamped folder in the system's temporary directory. *(Note: This option is generally not needed unless troubleshooting issues).*
- `--help`: Show the help message and exit.

##### Authenticated access

During the deployment process, you might be prompted: `Allow unauthenticated invocations to [your-service-name] (y/N)?`.

- Enter `y` to allow public access to your agent's API endpoint without authentication.
- Enter `N` (or press Enter for the default) to require authentication (e.g., using an identity token as shown in the "Testing your agent" section).

Upon successful execution, the command deploys your agent to Cloud Run and provides the URL of the deployed service.

### adk CLI

The adkgo command is located in the google/adk-go repository under cmd/adkgo. Before using it, you need to build it from the root of the adk-go repository:

`go build ./cmd/adkgo`

The adkgo deploy cloudrun command automates the deployment of your application. You do not need to provide your own Dockerfile.

#### Agent Code Structure

When using the adkgo tool, your main.go file must use the launcher framework. This is because the tool compiles your code and then runs the resulting executable with specific command-line arguments (like web, api, a2a) to start the required services. The launcher is designed to parse these arguments correctly.

Your main.go should look like this:

main.go

```go
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
    "os"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/cmd/launcher"
    "google.golang.org/adk/cmd/launcher/full"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)

type getCapitalCityArgs struct {
    Country string `json:"country" jsonschema:"The country for which to find the capital city."`
}

func getCapitalCity(ctx tool.Context, args getCapitalCityArgs) (string, error) {
    capitals := map[string]string{
        "united states": "Washington, D.C.",
        "canada":        "Ottawa",
        "france":        "Paris",
        "japan":         "Tokyo",
    }
    capital, ok := capitals[strings.ToLower(args.Country)]
    if !ok {
        return "", fmt.Errorf("couldn't find the capital for %s", args.Country)
    }

    return capital, nil
}

func main() {
    ctx := context.Background()

    model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{
        APIKey: os.Getenv("GOOGLE_API_KEY"),
    })
    if err != nil {
        log.Fatalf("Failed to create model: %v", err)
    }

    capitalTool, err := functiontool.New(
        functiontool.Config{
            Name:        "get_capital_city",
            Description: "Retrieves the capital city for a given country.",
        },
        getCapitalCity,
    )
    if err != nil {
        log.Fatalf("Failed to create function tool: %v", err)
    }

    geoAgent, err := llmagent.New(llmagent.Config{
        Name:        "capital_agent",
        Model:       model,
        Description: "Agent to find the capital city of a country.",
        Instruction: "I can answer your questions about the capital city of a country.",
        Tools:       []tool.Tool{capitalTool},
    })
    if err != nil {
        log.Fatalf("Failed to create agent: %v", err)
    }

    config := &launcher.Config{
        AgentLoader: agent.NewSingleLoader(geoAgent),
    }

    l := full.NewLauncher()
    err = l.Execute(ctx, config, os.Args[1:])
    if err != nil {
        log.Fatalf("run failed: %v\n\n%s", err, l.CommandLineSyntax())
    }
}
```

#### How it Works

1. The adkgo tool compiles your main.go into a statically linked binary for Linux.
1. It generates a Dockerfile that copies this binary into a minimal container.
1. It uses gcloud to build and deploy this container to Cloud Run.
1. After deployment, it starts a local proxy that securely connects to your new service.

Ensure you have authenticated with Google Cloud (`gcloud auth login` and `gcloud config set project <your-project-id>`).

#### Setup environment variables

Optional but recommended: Setting environment variables can make the deployment commands cleaner.

```bash
# Set your Google Cloud Project ID
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

# Set your desired Google Cloud Location
export GOOGLE_CLOUD_LOCATION="us-central1"

# Set the path to your agent's main Go file
export AGENT_PATH="./examples/go/cloud-run/main.go"

# Set a name for your Cloud Run service
export SERVICE_NAME="capital-agent-service"
```

#### Command usage

```bash
./adkgo deploy cloudrun \
    -p $GOOGLE_CLOUD_PROJECT \
    -r $GOOGLE_CLOUD_LOCATION \
    -s $SERVICE_NAME \
    --proxy_port=8081 \
    --server_port=8080 \
    -e $AGENT_PATH \
    --a2a --api --webui
```

##### Required

- `-p, --project_name`: Your Google Cloud project ID (e.g., $GOOGLE_CLOUD_PROJECT).
- `-r, --region`: The Google Cloud location for deployment (e.g., $GOOGLE_CLOUD_LOCATION, us-central1).
- `-s, --service_name`: The name for the Cloud Run service (e.g., $SERVICE_NAME).
- `-e, --entry_point_path`: Path to the main Go file containing your agent's source code (e.g., $AGENT_PATH).

##### Optional

- `--proxy_port`: The local port for the authenticating proxy to listen on. Defaults to 8081.
- `--server_port`: The port number the server will listen on within the Cloud Run container. Defaults to 8080.
- `--a2a`: If included, enables Agent2Agent communication. Enabled by default.
- `--a2a_agent_url`: A2A agent card URL as advertised in the public agent card. This flag is only valid when used with the --a2a flag.
- `--api`: If included, deploys the ADK API server. Enabled by default.
- `--webui`: If included, deploys the ADK dev UI alongside the agent API server. Enabled by default.
- `--temp_dir`: Temp directory for build artifacts. Defaults to os.TempDir().
- `--help`: Show the help message and exit.

##### Authenticated access

The service is deployed with --no-allow-unauthenticated by default.

Upon successful execution, the command deploys your agent to Cloud Run and provide a local URL to access the service through the proxy.

### gcloud CLI for Java

You can deploy Java Agents using the standard `gcloud run deploy` command and a `Dockerfile`. This is the current recommended way to deploy Java Agents to Google Cloud Run.

Ensure you are [authenticated](https://cloud.google.com/docs/authentication/gcloud) with Google Cloud. Specifically, run the commands `gcloud auth login` and `gcloud config set project <your-project-id>` from your terminal.

#### Project Structure

Organize your project files as follows:

```text
your-project-directory/
├── src/
│   └── main/
│       └── java/
│             └── agents/
│                 ├── capitalagent/
│                     └── CapitalAgent.java    # Your agent code
├── pom.xml                                    # Java adk and adk-dev dependencies
└── Dockerfile                                 # Container build instructions
```

Create the `pom.xml` and `Dockerfile` in the root of your project directory. Your Agent code file (`CapitalAgent.java`) inside a directory as shown above.

#### Code files

1. This is our Agent definition. This is the same code as present in [LLM agent](https://google.github.io/adk-docs/agents/llm-agents/index.md) with two caveats:

   - The Agent is now initialized as a **global public static final variable**.
   - The definition of the agent can be exposed in a static method or inlined during declaration.

   See the code for the `CapitalAgent` example in the [examples](https://github.com/google/adk-docs/blob/main/examples/java/cloud-run/src/main/java/agents/capitalagent/CapitalAgent.java) repository.

1. Add the following dependencies and plugin to the pom.xml file.

   pom.xml

   ```xml
   <dependencies>
     <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>0.5.0</version>
     </dependency>
     <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk-dev</artifactId>
        <version>0.5.0</version>
     </dependency>
   </dependencies>

   <plugin>
     <groupId>org.codehaus.mojo</groupId>
     <artifactId>exec-maven-plugin</artifactId>
     <version>3.2.0</version>
     <configuration>
       <mainClass>com.google.adk.web.AdkWebServer</mainClass>
       <classpathScope>compile</classpathScope>
     </configuration>
   </plugin>
   ```

1. Define the container image:

   Dockerfile

   ```dockerfile
   # Use an official Maven image with a JDK. Choose a version appropriate for your project.
   FROM maven:3.8-openjdk-17 AS builder

   WORKDIR /app

   COPY pom.xml .
   RUN mvn dependency:go-offline -B

   COPY src ./src

   # Expose the port your application will listen on.
   # Cloud Run will set the PORT environment variable, which your app should use.
   EXPOSE 8080

   # The command to run your application.
   # Use a shell so ${PORT} expands and quote exec.args so agent source-dir is passed correctly.
   ENTRYPOINT ["sh", "-c", "mvn compile exec:java \
       -Dexec.mainClass=com.google.adk.web.AdkWebServer \
       -Dexec.classpathScope=compile \
       -Dexec.args='--server.port=${PORT:-8080} --adk.agents.source-dir=target'"]
   ```

#### Deploy using `gcloud`

Navigate to `your-project-directory` in your terminal.

```bash
gcloud run deploy capital-agent-service \
--source . \
--region $GOOGLE_CLOUD_LOCATION \
--project $GOOGLE_CLOUD_PROJECT \
--allow-unauthenticated \
--set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
# Add any other necessary environment variables your agent might need
```

- `capital-agent-service`: The name you want to give your Cloud Run service.
- `--source .`: Tells gcloud to build the container image from the Dockerfile in the current directory.
- `--region`: Specifies the deployment region.
- `--project`: Specifies the GCP project.
- `--allow-unauthenticated`: Allows public access to the service. Remove this flag for private services.
- `--set-env-vars`: Passes necessary environment variables to the running container. Ensure you include all variables required by ADK and your agent (like API keys if not using Application Default Credentials).

`gcloud` will build the Docker image, push it to Google Artifact Registry, and deploy it to Cloud Run. Upon completion, it will output the URL of your deployed service.

For a full list of deployment options, see the [`gcloud run deploy` reference documentation](https://cloud.google.com/sdk/gcloud/reference/run/deploy).

## Testing your agent

Once your agent is deployed to Cloud Run, you can interact with it via the deployed UI (if enabled) or directly with its API endpoints using tools like `curl`. You'll need the service URL provided after deployment.

### UI Testing

If you deployed your agent with the UI enabled:

- **adk CLI:** You included the `--webui` flag during deployment.
- **gcloud CLI:** You set `SERVE_WEB_INTERFACE = True` in your `main.py`.

You can test your agent by simply navigating to the Cloud Run service URL provided after deployment in your web browser.

```bash
# Example URL format
# https://your-service-name-abc123xyz.a.run.app
```

The ADK dev UI allows you to interact with your agent, manage sessions, and view execution details directly in the browser.

To verify your agent is working as intended, you can:

1. Select your agent from the dropdown menu.
1. Type a message and verify that you receive an expected response from your agent.

If you experience any unexpected behavior, check the [Cloud Run](https://console.cloud.google.com/run) console logs.

### API Testing (curl)

You can interact with the agent's API endpoints using tools like `curl`. This is useful for programmatic interaction or if you deployed without the UI.

You'll need the service URL provided after deployment and potentially an identity token for authentication if your service isn't set to allow unauthenticated access.

#### Set the application URL

Replace the example URL with the actual URL of your deployed Cloud Run service.

```bash
export APP_URL="YOUR_CLOUD_RUN_SERVICE_URL"
# Example: export APP_URL="https://adk-default-service-name-abc123xyz.a.run.app"
```

#### Get an identity token (if needed)

If your service requires authentication (i.e., you didn't use `--allow-unauthenticated` with `gcloud` or answered 'N' to the prompt with `adk`), obtain an identity token.

```bash
export TOKEN=$(gcloud auth print-identity-token)
```

*If your service allows unauthenticated access, you can omit the `-H "Authorization: Bearer $TOKEN"` header from the `curl` commands below.*

#### List available apps

Verify the deployed application name.

```bash
curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
```

*(Adjust the `app_name` in the following commands based on this output if needed. The default is often the agent directory name, e.g., `capital_agent`)*.

#### Create or Update a Session

Initialize or update the state for a specific user and session. Replace `capital_agent` with your actual app name if different. The values `user_123` and `session_abc` are example identifiers; you can replace them with your desired user and session IDs.

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/apps/capital_agent/users/user_123/sessions/session_abc \
    -H "Content-Type: application/json" \
    -d '{"preferred_language": "English", "visit_count": 5}'
```

#### Run the Agent

Send a prompt to your agent. Replace `capital_agent` with your app name and adjust the user/session IDs and prompt as needed.

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/run_sse \
    -H "Content-Type: application/json" \
    -d '{
    "app_name": "capital_agent",
    "user_id": "user_123",
    "session_id": "session_abc",
    "new_message": {
        "role": "user",
        "parts": [{
        "text": "What is the capital of Canada?"
        }]
    },
    "streaming": false
    }'
```

- Set `"streaming": true` if you want to receive Server-Sent Events (SSE).
- The response will contain the agent's execution events, including the final answer.
