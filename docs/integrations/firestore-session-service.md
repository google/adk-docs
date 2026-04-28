---
catalog_title: Firestore Session Service
catalog_description: Session state management for ADK agents using Firestore
catalog_icon: /integrations/assets/firestore-session.jpg
catalog_tags: ["data", "google"]
---

# Session State Management using Firestore

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-java">Java</span>
</div>

[Google Cloud Firestore](https://cloud.google.com/firestore) is a flexible, scalable NoSQL cloud database to store and sync data for client- and server-side development. 
ADK provides a native integration for managing persistent agent session states using Firestore, allowing continuous multi-turn conversations without losing conversation history.

## Use cases

- **Customer Support Agents**: Maintain context across long-running support tickets, allowing the agent to remember past troubleshooting steps and preferences across multiple sessions.
- **Personalized Assistants**: Build agents that accumulate knowledge about the user over time, personalizing future interactions based on historical conversations.
- **Multi-modal Workflows**: Seamlessly handle complex use cases involving images, videos, and audio alongside text conversations, leveraging the built-in GCS artifact storage.
- **Enterprise Chatbots**: Deploy highly reliable, conversational AI applications with production-grade persistence suitable for large-scale enterprise environments.

## Prerequisites

- A [Google Cloud Project](https://cloud.google.com/) with Firestore enabled
- A [Firestore database](https://cloud.google.com/firestore/native/docs/create-database-server-client-library) in your Google Cloud Project
- Appropriate [Google Cloud credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc) configured in your environment

## Install dependencies

!!! note

    Ensure you use the same version for both `google-adk` and `google-adk-firestore-session-service` to guarantee compatibility.

Add the following dependencies to your `pom.xml` (Maven) or `build.gradle` (Gradle), replacing `1.2.0` with your target ADK version:

### Maven

```xml
<dependencies>
    <!-- ADK Core -->
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>1.2.0</version>
    </dependency>
    <!-- Firestore Session Service -->
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk-firestore-session-service</artifactId>
        <version>1.2.0</version>
    </dependency>
</dependencies>
```

### Gradle

```gradle
dependencies {
    // ADK Core
    implementation 'com.google.adk:google-adk:1.2.0'
    // Firestore Session Service
    implementation 'com.google.adk:google-adk-firestore-session-service:1.2.0'
}
```

## Example: Agent with Firestore Session Management

Use `FirestoreDatabaseRunner` to encapsulate your agent and Firestore-backed session management. Here is a complete example of setting up a simple assistant agent that remembers conversation context across turns using a custom session ID.

```java
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.runner.FirestoreDatabaseRunner;
import com.google.cloud.firestore.Firestore;
import com.google.cloud.firestore.FirestoreOptions;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Map;
import com.google.adk.sessions.FirestoreSessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import com.google.adk.events.Event;
import java.util.Scanner;
import static java.nio.charset.StandardCharsets.UTF_8;

public class YourAgentApplication {

    public static void main(String[] args) {
        System.out.println("Starting YourAgentApplication...");

        RunConfig runConfig = RunConfig.builder().build();
        String appName = "hello-time-agent";

        BaseAgent timeAgent = initAgent();
        
        // Initialize Firestore
        FirestoreOptions firestoreOptions = FirestoreOptions.getDefaultInstance();
        Firestore firestore = firestoreOptions.getService();

        // Use FirestoreDatabaseRunner to persist session state
        FirestoreDatabaseRunner runner = new FirestoreDatabaseRunner(
                timeAgent,
                appName,
                firestore
        );

        // Create a new session or load an existing one
        Session session = new FirestoreSessionService(firestore)
                .createSession(appName, "user1234", null, "12345")
                .blockingGet();

        // Start interactive CLI
        try (Scanner scanner = new Scanner(System.in, UTF_8)) {
            while (true) {
                System.out.print("\\nYou > ");
                String userInput = scanner.nextLine();
                if ("quit".equalsIgnoreCase(userInput)) {
                    break;
                }

                Content userMsg = Content.fromParts(Part.fromText(userInput));
                Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg, runConfig);

                System.out.print("\\nAgent > ");
                events.blockingForEach(event -> {
                    if (event.finalResponse()) {
                        System.out.println(event.stringifyContent());
                    }
                });
            }
        }
    }

    /** Mock tool implementation */
    @Schema(description = "Get the current time for a given city")
    public static Map<String, String> getCurrentTime(
        @Schema(name = "city", description = "Name of the city to get the time for") String city) {
        return Map.of(
            "city", city,
            "time", "The time is 10:30am."
        );
    }
    
    private static BaseAgent initAgent() {
        return LlmAgent.builder()
            .name("hello-time-agent")
            .description("Tells the current time in a specified city")
            .instruction(\"""
                You are a helpful assistant that tells the current time in a city.
                Use the 'getCurrentTime' tool for this purpose.
                \""")
            .model("gemini-flash-latest")
            .tools(FunctionTool.create(YourAgentApplication.class, "getCurrentTime"))
            .build();
    }
}
```

## Configuration

!!! note

    The Firestore Session Service supports properties file configuration. This allows you to easily target a dedicated Firestore database and define custom collection names for storing your agent session data.

You can customize your ADK application to use the Firestore session service by providing your own Firestore property settings, otherwise the library will use the default settings. 

### Environment-Specific Configuration

The library prioritizes environment-specific property files over the default settings using the following resolution order:

1. **Environment Variable Override**: It first checks for an environment variable named `env`. If this variable is set (e.g., `env=dev`), it will attempt to load a properties file matching the template: `adk-firestore-{env}.properties` (e.g., `adk-firestore-dev.properties`).
2. **Default Fallback**: If the `env` variable is not set, or the environment-specific file cannot be found, the library defaults to loading `adk-firestore.properties`.

Sample Property Settings:

```properties
# Firestore collection name for storing session data
firebase.root.collection.name=adk-session
# Google Cloud Storage bucket name for artifact storage
gcs.adk.bucket.name=your-gcs-bucket-name
# stop words for keyword extraction
keyword.extraction.stopwords=a,about,above,after,again,against,all,am,an,and,any,are,aren't,as,at,be,because,been,before,being,below,between,both,but,by,can't,cannot,could,couldn't,did,didn't,do,does,doesn't,doing,don't,down,during,each,few,for,from,further,had,hadn't,has,hasn't,have,haven't,having,he,he'd,he'll,he's,her,here,here's,hers,herself,him,himself,his,how,i,i'd,i'll,i'm,i've,if,in,into,is
```

!!! important

    `FirestoreDatabaseRunner` requires the `gcs.adk.bucket.name` property to be defined. This is because the runner internally initializes the `GcsArtifactService` to handle multi-modal artifact storage. If this property is missing or empty, the application will throw a `RuntimeException` during startup. This is used for storing artifacts like images, videos, audio files, etc. that are generated or processed by the agent. 


## Resources

- [Firestore Session Service](https://github.com/google/adk-java/tree/main/contrib/firestore-session-service): 
  Source code for the Firestore Session Service.
- [Spring Boot Google ADK + Firestore Example](https://github.com/mohan-ganesh/spring-boot-google-adk-firestore): 
  An example project demonstrating how to build a Java-based Google ADK agent application using Cloud Firestore for session management.
- [Firestore Session Service - DeepWiki](https://deepwiki.com/google/adk-java/4.3-firestore-session-service): 
  Detailed description of Firestore integration in the Google ADK for Java.
