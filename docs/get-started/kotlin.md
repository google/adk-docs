# Kotlin Quickstart for ADK

This guide shows you how to get up and running with Agent Development Kit
for Kotlin. Before you start, make sure you have the following installed:

*   Java 17 or later
*   Gradle 8.0 or later

??? tip "Building for Android?"

    This quickstart covers Kotlin on the JVM. If you're building an
    Android app, complete this quickstart first to learn the agent API,
    then see [Using ADK Kotlin in Android projects](/get-started/installation/#kotlin)
    for Android-specific project setup and on-device models.

## Create an agent project

Create an agent project with the following files and directory structure:

```none
my_agent/
    src/main/kotlin/com/example/agent/
                        HelloTimeAgent.kt   # agent definition + tool
                        Main.kt             # entry point
    build.gradle.kts                        # project configuration
    .env                                    # API keys or project IDs
```

??? tip "Create this project structure using the command line"

    === "Windows"

        ```console
        mkdir my_agent\src\main\kotlin\com\example\agent
        type nul > my_agent\src\main\kotlin\com\example\agent\HelloTimeAgent.kt
        type nul > my_agent\src\main\kotlin\com\example\agent\Main.kt
        type nul > my_agent\build.gradle.kts
        type nul > my_agent\.env
        ```

    === "MacOS / Linux"

        ```bash
        mkdir -p my_agent/src/main/kotlin/com/example/agent && \
            touch my_agent/src/main/kotlin/com/example/agent/HelloTimeAgent.kt && \
            touch my_agent/src/main/kotlin/com/example/agent/Main.kt && \
            touch my_agent/build.gradle.kts my_agent/.env
        ```

### Define the agent code

Create the code for a basic agent, including a simple implementation of an ADK
[Function Tool](/tools-custom/function-tools/), called `getCurrentTime()`.
Add the following code to the `HelloTimeAgent.kt` file in your project
directory:

```kotlin title="my_agent/src/main/kotlin/com/example/agent/HelloTimeAgent.kt"
--8<-- "examples/kotlin/snippets/get-started/HelloTimeAgent.kt:full_code"
```

!!! note "About `@Tool` and KSP"

    The `@Tool` annotation marks a function as a tool that the agent can
    call. At compile time, a KSP (Kotlin Symbol Processing) annotation
    processor generates the `.generatedTools()` extension function used above.
    This is a zero-reflection approach to function tool registration. The
    required KSP plugin and processor dependency are included in the
    `build.gradle.kts` configuration below.

### Configure project and dependencies

An ADK Kotlin agent project requires the following dependencies in your
`build.gradle.kts` project file:

```kotlin title="my_agent/build.gradle.kts (partial)"
dependencies {
    implementation("com.google.adk:google-adk-kotlin-core:0.1.0")
    ksp("com.google.adk:google-adk-kotlin-processor:0.1.0")
}
```

??? info "Complete `build.gradle.kts` configuration for project"
    The following code shows a complete `build.gradle.kts` configuration for
    this project:

    ```kotlin title="my_agent/build.gradle.kts"
    plugins {
        kotlin("jvm") version "2.3.21"
        id("com.google.devtools.ksp") version "2.3.7"
        application
    }

    repositories {
        mavenCentral()
    }

    dependencies {
        implementation("com.google.adk:google-adk-kotlin-core:0.1.0")
        implementation("com.google.adk:google-adk-kotlin-webserver:0.1.0")
        ksp("com.google.adk:google-adk-kotlin-processor:0.1.0")
    }

    kotlin {
        jvmToolchain(17)
    }

    application {
        mainClass.set(
            project.findProperty("mainClass") as? String
                ?: "com.example.agent.MainKt"
        )
    }
    ```

### Set your API key

This project uses the Gemini API, which requires an API key. If you
don't already have Gemini API key, create a key in Google AI Studio on the
[API Keys](https://aistudio.google.com/app/apikey) page.

In a terminal window, write your API key into your `.env` file of your project
to set environment variables:

=== "MacOS / Linux"

    ```bash title="Update: my_agent/.env"
    echo 'export GOOGLE_API_KEY="YOUR_API_KEY"' > .env
    ```

=== "Windows PowerShell"

    ```console title="Update: my_agent/env.bat"
    echo 'set GOOGLE_API_KEY="YOUR_API_KEY"' > env.bat
    ```

=== "Windows Command Prompt"

    ```console title="Update: my_agent/env.bat"
    echo set GOOGLE_API_KEY="YOUR_API_KEY" > env.bat
    ```

??? tip "Using other AI models with ADK"
    ADK supports the use of many generative AI models. For more
    information on configuring other models in ADK agents, see
    [Models & Authentication](/agents/models).

### Create an entry point

Create a `Main.kt` file to run and interact with `HelloTimeAgent` from the
command line. The `InMemoryRunner` lets you invoke the agent programmatically
and collect responses from a coroutine.

```kotlin title="my_agent/src/main/kotlin/com/example/agent/Main.kt"
package com.example.agent

import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Role
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    val runner = InMemoryRunner(agent = HelloTimeAgent.rootAgent)

    print("You > ")
    val input = readlnOrNull() ?: return@runBlocking
    runner.runAsync(
        userId = "user",
        sessionId = "session",
        newMessage = Content(
            role = Role.USER,
            parts = listOf(Part(text = input)),
        ),
    ).collect { event ->
        val text = event.content?.parts?.firstOrNull()?.text
        if (event.turnComplete && !text.isNullOrBlank()) {
            println("\n${event.author} > $text")
        }
    }
}
```

## Run your agent

You can run your ADK agent using the interactive command-line interface
the command-line entry point above or the ADK web user interface provided by
`AdkWebServer`. Both options allow you to test and interact with your agent.

### Run with command-line interface

Run your agent with the command-line interface using the Gradle `run` task:

```console
# Remember to load keys and settings: source .env OR env.bat
gradle run
```

The agent starts an interactive session. Type a message and press Enter:

```
Agent hello_time_agent is ready. Type 'exit' to quit.

You > What time is it in New York?

hello_time_agent > The current time in New York is 10:30am.

You > exit
Exiting agent.
```

![adk-run.png](/assets/adk-run.png)

### Run with web interface

To run your agent with the ADK web interface, add the webserver dependency
to your `build.gradle.kts`:

```kotlin title="my_agent/build.gradle.kts (add to dependencies)"
dependencies {
    implementation("com.google.adk:google-adk-kotlin-core:0.1.0")
    implementation("com.google.adk:google-adk-kotlin-webserver:0.1.0")
    ksp("com.google.adk:google-adk-kotlin-processor:0.1.0")
}
```

Then create a `WebMain.kt` file alongside your `Main.kt`:

```kotlin title="my_agent/src/main/kotlin/com/example/agent/WebMain.kt"
package com.example.agent

import com.google.adk.kt.artifacts.InMemoryArtifactService
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.webserver.AdkWebServer
import com.google.adk.kt.webserver.loaders.SingleAgentLoader
import com.google.adk.kt.webserver.telemetry.ApiServerSpanExporter

fun main() {
    val agent = HelloTimeAgent.rootAgent
    val sessionService = InMemorySessionService()
    val artifactService = InMemoryArtifactService()

    val server = AdkWebServer(
        port = 8080,
        sessionService = sessionService,
        artifactService = artifactService,
        agentLoader = SingleAgentLoader(agent),
        runner = InMemoryRunner(
            agent = agent,
            sessionService = sessionService,
            artifactService = artifactService,
        ),
        apiServerSpanExporter = ApiServerSpanExporter(),
    )

    println("Starting ADK web server on http://localhost:8080...")
    server.start(wait = true)
}
```

Run the web server using the `-PmainClass` property to select the web
entry point:

```console
# Remember to load keys and settings: source .env OR env.bat
gradle run -PmainClass=com.example.agent.WebMainKt
```

This command starts a web server with a chat interface for your agent. You can
access the web interface at (http://localhost:8080). Select your agent at the
upper left corner and type a request.

![adk-web-dev-ui-chat.png](/assets/adk-web-dev-ui-chat.png)

!!! warning "Caution: ADK Web for development only"

    ADK Web is ***not meant for use in production deployments***. You should
    use ADK Web for development and debugging purposes only.

## Next: Build your agent

Now that you have ADK installed and your first agent running, try building
your own agent with our build guides:

*  [Build your agent](/tutorials/)
*  [Use ADK Kotlin in Android projects](/get-started/installation/#kotlin)
