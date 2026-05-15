# ADK Demo App Sample

This is a sample Android application demonstrating the use of the Google ADK (Agent Development Kit) to create a fun facts agent.

## Setup Instructions

To run this sample app, you need to provide a Gemini API key. This key is used by the `FunFactsAgent` to communicate with the Gemini model.

### 1. Get a Gemini API Key

If you don't have one already, you can obtain an API key from the [Google AI Studio](https://aistudio.google.com/).

### 2. Configure the API Key

The project is configured to read the API key during the build process. You can provide it in one of the following ways:

#### Option A: Using an Environment Variable (Recommended)

Set an environment variable named `GEMINI_API_KEY` or `GOOGLE_API_KEY` on your development machine:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

#### Option B: Using local.properties

Alternatively, you can add the key to your `local.properties` file in the project root:

1. Open `local.properties` (create it if it doesn't exist).
2. Add the following line:

```properties
GEMINI_API_KEY=your_api_key_here
```

### 3. Build and Run

Once the key is configured, you can build and run the app from Android Studio or using Gradle:

```bash
./gradlew :app:assembleDebug
```

## How it Works

- **Agent Definition**: See `FunFactsAgent.kt` for how the `LlmAgent` is configured.
- **Business Logic**: `ChatViewModel.kt` handles the interaction with the agent using `InMemoryRunner`.
- **UI**: `MainActivity.kt` provides a simple Compose-based chat interface.
