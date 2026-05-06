# Kotlin Quickstart for ADK

This guide shows you how to get up and running with Agent Development Kit
for Kotlin. Before you start, make sure you have the following installed:

*   Java 17 or later
*   Gradle 8.0 or later

## Create an agent project

Create an agent project with the following files and directory structure:

```none
my_agent/
    src/main/kotlin/com/example/agent/
                        HelloTimeAgent.kt   # main agent code
    build.gradle.kts                        # project configuration
    .env                                    # API keys or project IDs
```

??? tip "Create this project structure using the command line"

    === "Windows"

        ```console
        mkdir my_agent\src\main\kotlin\com\example\agent
        type nul > my_agent\src\main\kotlin\com\example\agent\HelloTimeAgent.kt
        type nul > my_agent\build.gradle.kts
        type nul > my_agent\.env
        ```

    === "MacOS / Linux"

        ```bash
        mkdir -p my_agent/src/main/kotlin/com/example/agent && \
            touch my_agent/src/main/kotlin/com/example/agent/HelloTimeAgent.kt && \
            touch my_agent/build.gradle.kts my_agent/.env
        ```

### Define the agent code

Create the code for a basic agent, including a simple implementation of an ADK
[Function Tool](/tools-custom/function-tools/), called `getCurrentTime()`.
Add the following code to the `HelloTimeAgent.kt` file in your project
directory:

```kotlin title="my_agent/src/main/kotlin/com/example/agent/HelloTimeAgent.kt"
package com.example.agent

import com.google.adk.kt.agents.AgentConfig
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.agents.LlmAgentConfig
import com.google.adk.kt.models.GeminiModel
import com.google.adk.kt.tools.AdkParam
import com.google.adk.kt.tools.AdkTool

class TimeService {
    /** Mock tool implementation */
    @AdkTool
    fun getCurrentTime(
        @AdkParam("Name of the city to get the time for") city: String
    ): Map<String, String> {
        return mapOf("city" to city, "time" to "The time is 10:30am.")
    }
}

object HelloTimeAgent {
    @JvmField
    val rootAgent = LlmAgent(
        config = LlmAgentConfig(
            agentConfig = AgentConfig(
                name = "hello_time_agent",
                description = "Tells the current time in a specified city."
            ),
            model = GeminiModel(
                System.getenv("GEMINI_API_KEY")
                    ?: error("GEMINI_API_KEY environment variable not set."),
                name = "gemini-2.5-flash",
            ),
            instruction = Instruction(
                "You are a helpful assistant that tells the current time in a city. "
                    + "Use the 'getCurrentTime' tool for this purpose."
            ),
            tools = TimeService().adkTools(),
        )
    )
}
```

### Configure project and dependencies

An ADK Kotlin agent project requires the following dependency in your
`build.gradle.kts` project file:

```kotlin title="my_agent/build.gradle.kts (partial)"
dependencies {
    implementation("com.google.adk:google-adk-kotlin-core:0.1.0")
}
```

??? info "Complete `build.gradle.kts` configuration for project"
    The following code shows a complete `build.gradle.kts` configuration for
    this project:

    ```kotlin title="my_agent/build.gradle.kts"
    plugins {
        kotlin("jvm") version "2.1.0"
        application
    }

    repositories {
        mavenCentral()
    }

    dependencies {
        implementation("com.google.adk:google-adk-kotlin-core:0.1.0")
    }

    kotlin {
        jvmToolchain(17)
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
    echo 'export GEMINI_API_KEY="YOUR_API_KEY"' > .env
    ```

=== "Windows PowerShell"

    ```console title="Update: my_agent/env.bat"
    echo 'set GEMINI_API_KEY="YOUR_API_KEY"' > env.bat
    ```

=== "Windows Command Prompt"

    ```console title="Update: my_agent/env.bat"
    echo set GEMINI_API_KEY="YOUR_API_KEY" > env.bat
    ```

??? tip "Using other AI models with ADK"
    ADK supports the use of many generative AI models. For more
    information on configuring other models in ADK agents, see
    [Models & Authentication](/agents/models).

## Run your agent

<!-- TODO: Add CLI runner instructions for Kotlin ADK -->
<!-- TODO: Add web UI runner instructions for Kotlin ADK -->

### Run with command-line interface

TODO: Add instructions for running a Kotlin ADK agent from the command line.

### Run with web interface

TODO: Add instructions for running a Kotlin ADK agent with the ADK web UI.

![adk-web-dev-ui-chat.png](/assets/adk-web-dev-ui-chat.png)

!!! warning "Caution: ADK Web for development only"

    ADK Web is ***not meant for use in production deployments***. You should
    use ADK Web for development and debugging purposes only.

## Next: Build your agent

Now that you have ADK installed and your first agent running, try building
your own agent with our build guides:

*  [Build your agent](/tutorials/)
