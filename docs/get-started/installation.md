---
hide:
  - toc
---

# Advanced setup

This page provides detailed installation and configuration instructions for ADK
across supported languages. For a guided introduction, start with the
[quickstart for your language](/get-started/).

=== "Python"

    **Create & activate virtual environment**

    We recommend creating a virtual Python environment using
    [venv](https://docs.python.org/3/library/venv.html):

    ```shell
    python3 -m venv .venv
    ```

    Now, you can activate the virtual environment using the appropriate command
    for your operating system and environment:

    ```
    # Mac / Linux
    source .venv/bin/activate

    # Windows CMD:
    .venv\Scripts\activate.bat

    # Windows PowerShell:
    .venv\Scripts\Activate.ps1
    ```

    **Install ADK**

    ```bash
    pip install google-adk
    ```

    (Optional) Verify your installation:

    ```bash
    pip show google-adk
    ```

=== "TypeScript"

    **Install ADK and ADK DevTools**

    ```bash
    npm install @google/adk @google/adk-devtools
    ```

=== "Go"

    **Create a new Go module**

    If you are starting a new project, you can create a new Go module:

    ```shell
    go mod init example.com/my-agent
    ```

    **Install ADK**

    To add the ADK to your project, run the following command:

    ```shell
    go get google.golang.org/adk
    ```

    This will add the ADK as a dependency to your `go.mod` file.

    (Optional) Verify your installation by checking your `go.mod` file for the
    `google.golang.org/adk` entry.

=== "Java"

    You can either use maven or gradle to add the `google-adk` and
    `google-adk-dev` package.

    `google-adk` is the core Java ADK library. Java ADK also comes with a
    pluggable example SpringBoot server to run your agents seamlessly. This
    optional package is present as part of `google-adk-dev`.

    If you are using maven, add the following to your `pom.xml`:

    ```xml title="pom.xml"
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion>

        <groupId>com.example.agent</groupId>
        <artifactId>adk-agents</artifactId>
        <version>1.0-SNAPSHOT</version>

        <!-- Specify the version of Java you'll be using -->
        <properties>
            <maven.compiler.source>17</maven.compiler.source>
            <maven.compiler.target>17</maven.compiler.target>
            <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        </properties>

        <dependencies>
            <!-- The ADK core dependency -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk</artifactId>
                <version>1.2.0</version>
            </dependency>
            <!-- The ADK dev web UI to debug your agent -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk-dev</artifactId>
                <version>1.2.0</version>
            </dependency>
        </dependencies>

    </project>
    ```

    Here's a [complete
    pom.xml](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run/pom.xml)
    file for reference.

    If you are using gradle, add the dependency to your build.gradle:

    ```title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:1.2.0'
        implementation 'com.google.adk:google-adk-dev:1.2.0'
    }
    ```

    You should also configure Gradle to pass `-parameters` to `javac`.
    (Alternatively, use `@Schema(name = "...")`).

=== "Kotlin"

    **Use ADK Kotlin on the JVM**

    For Kotlin on the JVM, add the ADK core library and the KSP annotation
    processor to your `build.gradle.kts`:

    ```kotlin title="build.gradle.kts"
    plugins {
        kotlin("jvm") version "2.3.21"
        id("com.google.devtools.ksp") version "2.3.7"
    }

    dependencies {
        implementation("com.google.adk:google-adk-kotlin-core:0.1.0")
        ksp("com.google.adk:google-adk-kotlin-processor:0.1.0")
    }
    ```

    The KSP processor generates code for the `@Tool` annotation used to
    register function tools. See the [Kotlin Quickstart](/get-started/kotlin/)
    for a complete project setup.

    **Use ADK Kotlin in Android projects**

    You can use the ADK Kotlin agent API to build AI agents that run inside
    Android apps. The agent code you write (defining `LlmAgent`, tools, and
    sub-agents) is identical to the [Kotlin Quickstart](/get-started/kotlin/).
    The differences are the Gradle dependency, the project configuration, and
    how you invoke the agent at runtime.

    **Prerequisites**

    - [Android Studio](https://developer.android.com/studio)
    - Android SDK (compileSdk 34 or later, minSdk 26 or later)

    **Configure your Android project**

    In your Android project's `build.gradle.kts`, add the ADK Android dependency
    and the KSP annotation processor:

    ```kotlin title="app/build.gradle.kts (partial)"
    plugins {
        id("com.android.application")
        kotlin("android")
        id("com.google.devtools.ksp") version "2.3.7"
    }

    dependencies {
        implementation("com.google.adk:google-adk-kotlin-core-android:0.1.0")
        ksp("com.google.adk:google-adk-kotlin-processor:0.1.0")
    }
    ```

    ??? info "Complete `build.gradle.kts` for an Android project"

        ```kotlin title="app/build.gradle.kts"
        plugins {
            id("com.android.application")
            kotlin("android")
            id("com.google.devtools.ksp") version "2.3.7"
        }

        android {
            namespace = "com.example.agent"
            compileSdk = 34

            defaultConfig {
                applicationId = "com.example.agent"
                minSdk = 26
                targetSdk = 34
            }
        }

        dependencies {
            implementation("com.google.adk:google-adk-kotlin-core-android:0.1.0")
            ksp("com.google.adk:google-adk-kotlin-processor:0.1.0")
        }

        kotlin {
            jvmToolchain(17)
        }
        ```

    !!! note "This replaces the JVM dependency"

        Android projects use `google-adk-kotlin-core-android` instead of
        `google-adk-kotlin-core`. Do not add both. The Android artifact includes
        the full ADK agent API along with Android-specific model support.

    **Define your agent**

    The agent code is identical to the
    [Kotlin Quickstart](/get-started/kotlin/#define-the-agent-code). The
    same `HelloTimeAgent` with `@Tool`, `@Param`, and `.generatedTools()`
    works unchanged on Android:

    ```kotlin title="HelloTimeAgent.kt"
    --8<-- "examples/kotlin/snippets/get-started/HelloTimeAgent.kt:full_code"
    ```

    !!! warning "Do not embed API keys in client apps"

        Do not include your API key directly in a published application.
        This quickstart is intended for prototyping only. For production
        use cases, call cloud models through your own backend service or
        through
        [Firebase AI Logic](https://firebase.google.com/docs/ai-logic)
        so that API keys are never exposed in client code.

    **Run the agent from your Android app**

    On Android, `AdkWebServer` is not available. Instead, use
    `InMemoryRunner` to invoke the agent and collect responses from a coroutine:

    ```kotlin title="Call an ADK agent from Android code"
    import com.google.adk.kt.runners.InMemoryRunner
    import com.google.adk.kt.sessions.InMemorySessionService
    import com.google.adk.kt.types.Content
    import com.google.adk.kt.types.Part
    import com.google.adk.kt.types.Role
    import kotlinx.coroutines.CoroutineScope
    import kotlinx.coroutines.launch

    // Create a runner and session service
    val sessionService = InMemorySessionService()
    val runner = InMemoryRunner(
        agent = HelloTimeAgent.rootAgent,
        sessionService = sessionService,
    )

    // Call the agent from a coroutine (e.g. in a ViewModel or Activity)
    scope.launch {
        runner.runAsync(
            userId = "user-123",
            sessionId = "session-123",
            newMessage = Content(
                role = Role.USER,
                parts = listOf(Part(text = "What time is it in New York?")),
            ),
        ).collect { event ->
            val text = event.content?.parts?.firstOrNull()?.text
            if (!text.isNullOrBlank()) {
                // Update your UI with the agent's response
            }
        }
    }
    ```

    ??? info "On-device models with Gemini Nano"

        The ADK Android artifact includes support for on-device inference
        using [Gemini Nano](https://developer.android.com/ai/gemini-nano)
        through ML Kit GenAI. This allows agents to run without network
        access, keeping data on the device.

        To use an on-device model, create a `GenaiPrompt` model instead
        of `Gemini`:

        ```kotlin
        import com.google.adk.kt.models.mlkit.GenaiPrompt
        import com.google.mlkit.genai.prompt.GenerativeModel

        // Create an ML Kit GenerativeModel for on-device inference
        val generativeModel: GenerativeModel = // ... initialize via ML Kit

        val onDeviceModel = GenaiPrompt.create(
            generativeModel = generativeModel,
            name = "gemini-nano",
        )

        val agent = LlmAgent(
            name = "on_device_agent",
            model = onDeviceModel,
            instruction = Instruction("You are a helpful assistant."),
        )
        ```

        You can also combine cloud and on-device models in a multi-agent
        system: use a cloud-based `Gemini` for the root orchestrator
        and on-device `GenaiPrompt` models for sub-agents that handle
        privacy-sensitive tasks.

    For a complete working Activity and more examples, see the
    [ADK Kotlin examples on GitHub](https://github.com/google/adk-kotlin/tree/main/internal/examples).
