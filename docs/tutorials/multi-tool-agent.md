# Build a multi-tool agent

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

This quickstart guides you through installing Agent Development Kit (ADK),
setting up a basic agent with multiple tools, and running it locally either in
the terminal or in the interactive, browser-based dev UI.

<!-- <img src="../../assets/quickstart.png" alt="Quickstart setup"> -->

This quickstart assumes a local IDE (VS Code, PyCharm, IntelliJ IDEA, etc.) with
Python 3.10+ or Java 17+ and terminal access. This method runs the application
entirely on your machine and is recommended for internal development.

## 1. Set up Environment & Install ADK { #set-up-environment-install-adk }

=== "Python"

    Create & Activate Virtual Environment (Recommended):

    ```bash
    # Create
    python3 -m venv .venv
    # Activate (each new terminal)
    # macOS/Linux: source .venv/bin/activate
    # Windows CMD: .venv\Scripts\activate.bat
    # Windows PowerShell: .venv\Scripts\Activate.ps1
    ```

    Install ADK:

    ```bash
    pip install google-adk
    ```

=== "TypeScript"

    Create a new project directory, initialize it, and install dependencies:

    ```bash
    mkdir my-adk-agent
    cd my-adk-agent
    npm init -y
    npm install @google/adk @google/adk-devtools
    npm install -D typescript
    ```

    Create a `tsconfig.json` file with the following content. This configuration
    ensures your project correctly handles modern Node.js modules.

    ```json title="tsconfig.json"
    {
      "compilerOptions": {
        "target": "es2020",
        "module": "nodenext",
        "moduleResolution": "nodenext",
        "esModuleInterop": true,
        "strict": true,
        "skipLibCheck": true,
        // set to false to allow CommonJS module syntax:
        "verbatimModuleSyntax": false
      }
    }
    ```

=== "Go"

    ## Create a new Go module

    If you are starting a new project, you can create a new Go module:

    ```bash
    mkdir my-adk-agent
    cd my-adk-agent
    go mod init example.com/my-agent
    ```

    ## Install ADK

    To add the ADK to your project, run the following command:

    ```bash
    go get google.golang.org/adk/v2
    ```

    This will add the ADK as a dependency to your `go.mod` file.

=== "Java"

    To install ADK Java and set up the environment, see the [Java
    Quickstart](/get-started/java/).

=== "Kotlin"

    To install ADK Kotlin and set up the environment, see the [Kotlin
    Quickstart](/get-started/kotlin/).

## 2. Create Agent Project { #create-agent-project }

### Project structure

=== "Python"

    You will need to create the following project structure:

    ```console
    parent_folder/
        multi_tool_agent/
            __init__.py
            agent.py
            .env
    ```

    Create the folder `multi_tool_agent`:

    ```bash
    mkdir multi_tool_agent/
    ```

    !!! info "Note for Windows users"

        When using ADK on Windows for the next few steps, we recommend creating
        Python files using File Explorer or an IDE because the following commands
        (`mkdir`, `echo`) typically generate files with null bytes and/or incorrect
        encoding.

    ### `__init__.py`

    Now create an `__init__.py` file in the folder:

    ```shell
    echo "from . import agent" > multi_tool_agent/__init__.py
    ```

    Your `__init__.py` should now look like this:

    ```python title="multi_tool_agent/__init__.py"
    --8<-- "examples/python/snippets/get-started/multi_tool_agent/__init__.py"
    ```

    ### `agent.py`

    Create an `agent.py` file in the same folder:

    === "OS X &amp; Linux"
        ```shell
        touch multi_tool_agent/agent.py
        ```

    === "Windows"
        ```shell
        type nul > multi_tool_agent/agent.py
        ```

    Copy and paste the following code into `agent.py`:

    ```python title="multi_tool_agent/agent.py"
    --8<-- "examples/python/snippets/get-started/multi_tool_agent/agent.py"
    ```

    ### `.env`

    Create a `.env` file in the same folder:

    === "OS X &amp; Linux"
        ```shell
        touch multi_tool_agent/.env
        ```

    === "Windows"
        ```shell
        type nul > multi_tool_agent\.env
        ```

    More instructions about this file are described in the next section on [Set up the model](#set-up-the-model).

=== "TypeScript"

    You will need to create the following project structure in your `my-adk-agent` directory:

    ```console
    my-adk-agent/
        agent.ts
        .env
        package.json
        tsconfig.json
    ```

    ### `agent.ts`

    Create an `agent.ts` file in your project folder:

    === "OS X &amp; Linux"
        ```shell
        touch agent.ts
        ```

    === "Windows"
        ```shell
        type nul > agent.ts
        ```

    Copy and paste the following code into `agent.ts`:

    ```typescript title="agent.ts"
    --8<-- "examples/typescript/snippets/get-started/multi_tool_agent/agent.ts"
    ```

    ### `.env`

    Create a `.env` file in the same folder:

    === "OS X &amp; Linux"
        ```shell
        touch .env
        ```

    === "Windows"
        ```shell
        type nul > .env
        ```

    More instructions about this file are described in the next section on [Set up the model](#set-up-the-model).

=== "Go"

    You will need to create the following project structure:

    ```console
    my-adk-agent/
        agent.go
        .env
        go.mod
    ```

    ### `agent.go`

    Create an `agent.go` file in your project folder:

    === "OS X &amp; Linux"
        ```bash
        touch agent.go
        ```

    === "Windows"
        ```console
        type nul > agent.go
        ```

    Copy and paste the following code into `agent.go`:

    ```go title="agent.go"
    --8<-- "examples/go/snippets/get-started/multi_tool_agent/main.go:full_code"
    ```

    ### `.env`

    Create a `.env` file in the same folder:

    === "OS X &amp; Linux"
        ```bash
        touch .env
        ```

    === "Windows"
        ```console
        type nul > .env
        ```

=== "Java"

    Java projects generally feature the following project structure:

    ```console
    project_folder/
    ├── pom.xml (or build.gradle)
    ├── src/
    ├── └── main/
    │       └── java/
    │           └── agents/
    │               └── multitool/
    └── test/
    ```

    ### Create `MultiToolAgent.java`

    Create a `MultiToolAgent.java` source file in the `agents.multitool` package
    in the `src/main/java/agents/multitool/` directory.

    Copy and paste the following code into `MultiToolAgent.java`:

    ```java title="agents/multitool/MultiToolAgent.java"
    --8<-- "examples/java/cloud-run/src/main/java/agents/multitool/MultiToolAgent.java:full_code"
    ```

=== "Kotlin"

    Kotlin projects generally feature the following project structure:

    ```console
    project_folder/
    ├── build.gradle.kts
    ├── src/
    ├── └── main/
    │       └── kotlin/
    │           └── agents/
    │               └── multitool/
    ```

    ### Create `MultiToolAgent.kt`

    Create a `MultiToolAgent.kt` source file in the `src/main/kotlin/agents/multitool/` directory.

    Copy and paste the following code into `MultiToolAgent.kt`:

    ```kotlin title="src/main/kotlin/agents/multitool/MultiToolAgent.kt"
    --8<-- "examples/kotlin/snippets/get-started/multi_tool_agent/MultiToolAgent.kt"
    ```

![intro_components.png](../assets/quickstart-flow-tool.png)

## 3. Set up the model { #set-up-the-model }

Your agent's ability to understand user requests and generate responses is
powered by a generative AI model or Large Language Model (LLM). This guide uses Gemini models as
examples, but ADK is compatible with many AI models from Google and other
providers. For more information on available models and how to configure
them, see [AI Models for ADK agents](/agents/models/).

### Model connection and authentication

When using an AI model through a service, such as the Gemini API or Gemini
Enterprise Agent Platform on Google Cloud, you must provide an API key or
authenticate with the service. The most direct way to provide this information
is to use environment variables or an `.env` file. The following examples show
the most common way to configure an agent for use with the Gemini API or Gemini
Enterprise Agent Platform.

=== "Gemini API"

    ```
    # .env configuration file
    GOOGLE_API_KEY="PASTE_YOUR_GEMINI_API_KEY_HERE"
    ```

=== "Google Cloud Agent Platform"

    ```
    # .env configuration file
    GOOGLE_CLOUD_PROJECT=your-project-id
    GOOGLE_CLOUD_LOCATION=location-code        # example: us-central1
    GOOGLE_GENAI_USE_ENTERPRISE=True
    ```

For more details on connecting ADK agents to Google Cloud hosted models and services,
including Gemini Enterprise Agent Platform, see the
[Connect to Google Cloud and Agent Platform](/get-started/google-cloud/) guide.

## 4. Run Your Agent { #run-your-agent }

=== "Python"

    Using the terminal, navigate to the parent directory of your agent project
    (e.g. using `cd ..`):

    ```console
    parent_folder/      <-- navigate to this directory
        multi_tool_agent/
            __init__.py
            agent.py
            .env
    ```

    There are multiple ways to interact with your agent:

    === "Dev UI (adk web)"

        !!! success "Authentication Setup for Agent Platform Users"
            If you selected **"Gemini - Google Cloud Agent Platform"** in the previous step, you must authenticate with Google Cloud before launching the dev UI.

            Run this command and follow the prompts:
            ```bash
            gcloud auth application-default login
            ```

            **Note:** Skip this step if you're using "Gemini - Google AI Studio".

        Run the following command to launch the **dev UI**.

        ```shell
        adk web
        ```

        !!! warning "Caution: ADK Web for development only"

            ADK Web is ***not meant for use in production deployments***. You should
            use ADK Web for development and debugging purposes only.

        !!!info "Note for Windows users"

            When hitting the `_make_subprocess_transport NotImplementedError`, consider using `adk web --no-reload` instead.


        **Step 1:** Open the URL provided (usually `http://localhost:8000` or
        `http://127.0.0.1:8000`) directly in your browser.

        **Step 2.** In the top-left corner of the UI, you can select your agent in
        the dropdown. Select "multi_tool_agent".

        !!!note "Troubleshooting"

            If you do not see "multi_tool_agent" in the dropdown menu, make sure you
            are running `adk web` in the **parent folder** of your agent folder
            (i.e. the parent folder of multi_tool_agent).

        **Step 3.** Now you can chat with your agent using the textbox:

        ![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)


        **Step 4.**  By using the `Events` tab at the left, you can inspect
        individual function calls, responses and model responses by clicking on the
        actions:

        ![adk-web-dev-ui-function-call.png](../assets/adk-web-dev-ui-function-call.png)

        On the `Events` tab, you can also click the `Trace` button to see the trace logs for each event that shows the latency of each function calls:

        ![adk-web-dev-ui-trace.png](../assets/adk-web-dev-ui-trace.png)

        **Step 5.** You can also enable your microphone and talk to your agent:

        !!!note "Model support for voice/video streaming"

            In order to use voice/video streaming in ADK, you will need to use Gemini models that support the Live API. You can find the **model ID(s)** that supports the Gemini Live API in the documentation:

            - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
            - [Agent Platform: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

            You can then replace the `model` string in `root_agent` in the `agent.py` file you created earlier ([jump to section](#agentpy)). Your code should look something like:

            ```py
            root_agent = Agent(
                name="weather_time_agent",
                model="replace-me-with-model-id", #e.g. gemini-2.0-flash-live-001
                ...
            ```

        ![adk-web-dev-ui-audio.png](../assets/adk-web-dev-ui-audio.png)

    === "Terminal (adk run)"

        !!! tip

            When using `adk run` you can inject prompts into the agent to start by
            piping text to the command like so:

            ```shell
            echo "Please start by listing files" | adk run file_listing_agent
            ```

        Run the following command, to chat with your Weather agent.

        ```
        adk run multi_tool_agent
        ```

        ![adk-run.png](../assets/adk-run.png)

        To exit, use Cmd/Ctrl+C.

    === "API Server (adk api_server)"

        `adk api_server` enables you to create a local FastAPI server in a single
        command, enabling you to test local cURL requests before you deploy your
        agent.

        ![adk-api-server.png](../assets/adk-api-server.png)

        To learn how to use `adk api_server` for testing, refer to the
        [documentation on using the API server](/runtime/api-server/).

=== "TypeScript"

    Using the terminal, navigate to your agent project directory:

    ```console
    my-adk-agent/      <-- navigate to this directory
        agent.ts
        .env
        package.json
        tsconfig.json
    ```

    There are multiple ways to interact with your agent:

    === "Dev UI (adk web)"

        Run the following command to launch the **dev UI**.

        ```shell
        npx adk web
        ```

        **Step 1:** Open the URL provided (usually `http://localhost:8000` or
        `http://127.0.0.1:8000`) directly in your browser.

        **Step 2.** In the top-left corner of the UI, select your agent from the dropdown. The agents are listed by their filenames, so you should select "agent".

        !!!note "Troubleshooting"

            If you do not see "agent" in the dropdown menu, make sure you
            are running `npx adk web` in the directory containing your `agent.ts` file.

        **Step 3.** Now you can chat with your agent using the textbox:

        ![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)


        **Step 4.** By using the `Events` tab at the left, you can inspect
        individual function calls, responses and model responses by clicking on the
        actions:

        ![adk-web-dev-ui-function-call.png](../assets/adk-web-dev-ui-function-call.png)

        On the `Events` tab, you can also click the `Trace` button to see the trace logs for each event that shows the latency of each function calls:

        ![adk-web-dev-ui-trace.png](../assets/adk-web-dev-ui-trace.png)

    === "Terminal (adk run)"

        Run the following command to chat with your agent.

        ```
        npx adk run agent.ts
        ```

        ![adk-run.png](../assets/adk-run.png)

        To exit, use Cmd/Ctrl+C.

    === "API Server (adk api_server)"

        `npx adk api_server` enables you to create a local Express.js server in a single
        command, enabling you to test local cURL requests before you deploy your
        agent.

        ![adk-api-server.png](../assets/adk-api-server.png)

        To learn how to use `api_server` for testing, refer to the
        [documentation on testing](/runtime/api-server/).

=== "Go"

    Using the terminal, navigate to your agent project directory:

    ```console
    my-adk-agent/      <-- navigate to this directory
        agent.go
        .env
        go.mod
    ```

    There are multiple ways to interact with your agent:

    === "Dev UI (web)"

        Run the following command to launch the **dev UI**. You must specify which sub-launchers to activate (e.g., `webui`, `api`).

        ```bash
        go run agent.go web webui api
        ```

        **Step 1:** Open the URL provided (usually `http://localhost:8080`) directly in your browser.

        **Step 2.** In the top-left corner of the UI, select your agent from the dropdown. It should be "weather_time_agent".

        **Step 3.** Now you can chat with your agent using the textbox.

    === "Terminal (console)"

        Run the following command to chat with your agent in the terminal.

        ```bash
        go run agent.go console
        ```

        **Note:** If `console` is the first sublauncher in your code (as it is with `full.NewLauncher()`), you can also just run `go run agent.go`.

        To exit, use Cmd/Ctrl+C.

=== "Java"

    Using the terminal, navigate to the parent directory of your agent project
    (e.g. using `cd ..`):

    ```console
    project_folder/                <-- navigate to this directory
    ├── pom.xml (or build.gradle)
    ├── src/
    ├── └── main/
    │       └── java/
    │           └── agents/
    │               └── multitool/
    │                   └── MultiToolAgent.java
    └── test/
    ```

    === "Dev UI"

        Run the following command from the terminal to launch the Dev UI.

        **DO NOT change the main class name of the Dev UI server.**

        ```console title="terminal"
        mvn exec:java \
            -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
            -Dexec.args="--adk.agents.source-dir=src/main/java" \
            -Dexec.classpathScope="compile"
        ```

        **Step 1:** Open the URL provided (usually `http://localhost:8080` or
        `http://127.0.0.1:8080`) directly in your browser.

        **Step 2.** In the top-left corner of the UI, you can select your agent in
        the dropdown. Select "multi_tool_agent".

        !!!note "Troubleshooting"

            If you do not see "multi_tool_agent" in the dropdown menu, make sure you
            are running the `mvn` command at the location where your Java source code
            is located (usually `src/main/java`).

        **Step 3.** Now you can chat with your agent using the textbox:

        ![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)

        **Step 4.** You can also inspect individual function calls, responses and
        model responses by clicking on the actions:

        ![adk-web-dev-ui-function-call.png](../assets/adk-web-dev-ui-function-call.png)

        !!! warning "Caution: ADK Web for development only"

            ADK Web is ***not meant for use in production deployments***. You should
            use ADK Web for development and debugging purposes only.

    === "Maven"

        With Maven, run the `main()` method of your Java class
        with the following command:

        ```console title="terminal"
        mvn compile exec:java -Dexec.mainClass="agents.multitool.MultiToolAgent"
        ```

    === "Gradle"

        With Gradle, the `build.gradle` or `build.gradle.kts` build file
        should have the following Java plugin in its `plugins` section:

        ```groovy
        plugins {
            id('java')
            // other plugins
        }
        ```

        Then, elsewhere in the build file, at the top-level,
        create a new task to run the `main()` method of your agent:

        ```groovy
        tasks.register('runAgent', JavaExec) {
            classpath = sourceSets.main.runtimeClasspath
            mainClass = 'agents.multitool.MultiToolAgent'
        }
        ```

        Finally, on the command-line, run the following command:

        ```console
        gradle runAgent
        ```

=== "Kotlin"

    Using the terminal, navigate to your agent project directory:

    ```console
    project_folder/                <-- navigate to this directory
    ├── build.gradle.kts
    ├── src/
    ├── └── main/
    │       └── kotlin/
    │           └── agents/
    │               └── multitool/
    │                   └── MultiToolAgent.kt
    ```

    ### Run your Agent

    You can run the `main()` method of your Kotlin class using Gradle:

    ```console
    ./gradlew run
    ```

    Or if you are using IntelliJ IDEA, you can just click the green run arrow next to the `main()` function.

### 📝 Example prompts to try

* What is the weather in New York?
* What is the time in New York?
* What is the weather in Paris?
* What is the time in Paris?

## 🎉 Congratulations!

You've successfully created and interacted with your first agent using ADK!

---

## 🛣️ Next steps

* **Go to the tutorial**: Learn how to add memory, session, state to your agent:
  [tutorial](/tutorials/).
* **Delve into advanced configuration:** Explore the [setup](/get-started/installation/)
  section for deeper dives into project structure, configuration, and other
  interfaces.
* **Understand Core Concepts:** Learn about
  [agents concepts](/agents/).
