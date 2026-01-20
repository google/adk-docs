# Part 1: Introduction to ADK Bidi-streaming

Google's Agent Development Kit ([ADK](https://google.github.io/adk-docs/)) provides a production-ready framework for building Bidi-streaming applications with Gemini models. This guide introduces ADK's streaming architecture, which enables real-time, two-way communication between users and AI agents through multimodal channels (text, audio, video).

**What you'll learn**: This part covers the fundamentals of Bidi-streaming, the underlying Live API technology (Gemini Live API and Vertex AI Live API), ADK's architectural components (`LiveRequestQueue`, `Runner`, `Agent`), and a complete FastAPI implementation example. You'll understand how ADK handles session management, tool orchestration, and platform abstraction—reducing months of infrastructure development to declarative configuration.

## ADK Bidi-streaming Demo

To help you understand the concepts in this guide, we provide a working demo application that showcases ADK bidirectional streaming in action. This FastAPI-based demo implements the complete streaming lifecycle with a practical, real-world architecture.

**Demo Repository**: [adk-samples/python/agents/bidi-demo](https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo)

![ADK Bidi-streaming Demo](assets/bidi-demo-screen.png)

The demo features:

- **WebSocket Communication**: Real-time bidirectional streaming with concurrent upstream/downstream tasks
- **Multimodal Requests**: Text, audio, and image/video input with automatic transcription
- **Flexible Responses**: Text or audio output based on model capabilities
- **Interactive UI**: Web interface with event console for monitoring Live API events
- **Google Search Integration**: Agent equipped with tool calling capabilities

**We strongly recommend installing and running this demo** before diving into the guide. Hands-on experimentation will help you understand the concepts more deeply, and the demo code serves as a practical reference throughout all parts of this guide.

For installation instructions and usage details, see the [demo README](https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo).

## 1.1 What is Bidi-streaming?

Bidi-streaming (Bidirectional streaming) represents a fundamental shift from traditional AI interactions. Instead of the rigid "ask-and-wait" pattern, it enables **real-time, two-way communication** where both human and AI can speak, listen, and respond simultaneously. This creates natural, human-like conversations with immediate responses and the revolutionary ability to interrupt ongoing interactions.

Think of the difference between sending emails and having a phone conversation. Traditional AI interactions are like emails—you send a complete message, wait for a complete response, then send another complete message. Bidi-streaming is like a phone conversation—fluid, natural, with the ability to interrupt, clarify, and respond in real-time.

### Key Characteristics

These characteristics distinguish Bidi-streaming from traditional AI interactions and make it uniquely powerful for creating engaging user experiences:

- **Two-way Communication**: Continuous data exchange without waiting for complete responses. Users can interrupt the AI mid-response with new input, creating a natural conversational flow. The AI responds after detecting the user has finished speaking (via automatic voice activity detection or explicit activity signals).

- **Responsive Interruption**: Perhaps the most important feature for the natural user experience—users can interrupt the agent mid-response with new input, just like in human conversation. If an AI is explaining quantum physics and you suddenly ask "wait, what's an electron?", the AI stops immediately and addresses your question.

- **Best for Multimodal**: Bidi-streaming excels at multimodal interactions because it can process different input types simultaneously through a single connection. Users can speak while showing documents, type follow-up questions during voice calls, or seamlessly switch between communication modes without losing context. This unified approach eliminates the complexity of managing separate channels for each modality.

```mermaid
sequenceDiagram
    participant Client as User
    participant Agent

    Client->>Agent: "Hi!"
    Client->>Agent: "Explain the history of Japan"
    Agent->>Client: "Hello!"
    Agent->>Client: "Sure! Japan's history is a..." (partial content)
    Client->>Agent: "Ah, wait."

    Agent->>Client: "OK, how can I help?" [interrupted: true]
```

### Difference from Other Streaming Types

Understanding how Bidi-streaming differs from other approaches is crucial for appreciating its unique value. The streaming landscape includes several distinct patterns, each serving different use cases:

!!! note "Streaming Types Comparison"

    **Bidi-streaming** differs fundamentally from other streaming approaches:

    - **Server-Side Streaming**: One-way data flow from server to client. Like watching a live video stream—you receive continuous data but can't interact with it in real-time. Useful for dashboards or live feeds, but not for conversations.

    - **Token-Level Streaming**: Sequential text token delivery without interruption. The AI generates response word-by-word, but you must wait for completion before sending new input. Like watching someone type a message in real-time—you see it forming, but can't interrupt.

    - **Bidi-streaming**: Full two-way communication with interruption support. True conversational AI where both parties can speak, listen, and respond simultaneously. This is what enables natural dialogue where you can interrupt, clarify, or change topics mid-conversation.

### Real-World Applications

Bidi-streaming revolutionizes agentic AI applications by enabling agents to operate with human-like responsiveness and intelligence. These applications showcase how streaming transforms static AI interactions into dynamic, agent-driven experiences that feel genuinely intelligent and proactive.

In a video of the [Shopper's Concierge demo](https://www.youtube.com/watch?v=LwHPYyw7u6U), the multimodal Bidi-streaming feature significantly improve the user experience of e-commerce by enabling a faster and more intuitive shopping experience. The combination of conversational understanding and rapid, parallelized searching culminates in advanced capabilities like virtual try-on, boosting buyer confidence and reducing the friction of online shopping.

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/LwHPYyw7u6U?si=xxIEhnKBapzQA6VV" title="Shopper's Concierge" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>
</div>

Also, there are many possible real-world applications for Bidi-streaming:

#### Customer Service & Contact Centers

This is the most direct application. The technology can create sophisticated virtual agents that go far beyond traditional chatbots.

- Use case: A customer calls a retail company's support line about a defective product.
- Multimodality (video): The customer can say, "My coffee machine is leaking from the bottom, let me show you." They can then use their phone's camera to stream live video of the issue. The AI agent can use its vision capabilities to identify the model and the specific point of failure.
- Live Interaction & Interruption: If the agent says, "Okay, I'm processing a return for your Model X coffee maker," the customer can interrupt with, "No, wait, it's the Model Y Pro," and the agent can immediately correct its course without restarting the conversation.

#### E-commerce & Personalized Shopping

The agent can act as a live, interactive personal shopper, enhancing the online retail experience.

- Use Case: A user is browsing a fashion website and wants styling advice.
- Multimodality (Voice & Image): The user can hold up a piece of clothing to their webcam and ask, "Can you find me a pair of shoes that would go well with these pants?" The agent analyzes the color and style of the pants.
- Live Interaction: The conversation can be a fluid back-and-forth: "Show me something more casual." ... "Okay, how about these sneakers?" ... "Perfect, add the blue ones in size 10 to my cart."

#### Field Service & Technical Assistance

Technicians working on-site can use a hands-free, voice-activated assistant to get real-time help.

- Use Case: An HVAC technician is on-site trying to diagnose a complex commercial air conditioning unit.
- Multimodality (Video & Voice): The technician, wearing smart glasses or using a phone, can stream their point-of-view to the AI agent. They can ask, "I'm hearing a strange noise from this compressor. Can you identify it and pull up the diagnostic flowchart for this model?"
- Live Interaction: The agent can guide the technician step-by-step, and the technician can ask clarifying questions or interrupt at any point without taking their hands off their tools.

#### Healthcare & Telemedicine

The agent can serve as a first point of contact for patient intake, triage, and basic consultations.

- Use Case: A patient uses a provider's app for a preliminary consultation about a skin condition.
- Multimodality (Video/Image): The patient can securely share a live video or high-resolution image of a rash. The AI can perform a preliminary analysis and ask clarifying questions.

#### Financial Services & Wealth Management

An agent can provide clients with a secure, interactive, and data-rich way to manage their finances.

- Use Case: A client wants to review their investment portfolio and discuss market trends.
- Multimodality (Screen Sharing): The agent can share its screen to display charts, graphs, and portfolio performance data. The client could also share their screen to point to a specific news article and ask, "What is the potential impact of this event on my tech stocks?"
- Live Interaction: Analyze the client's current portfolio allocation by accessing their account data.Simulate the impact of a potential trade on the portfolio's risk profile.

## 1.2 Gemini Live API and Vertex AI Live API

ADK's Bidi-streaming capabilities are powered by Live API technology, available through two platforms: **[Gemini Live API](https://ai.google.dev/gemini-api/docs/live)** (via Google AI Studio) and **[Vertex AI Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)** (via Google Cloud). Both provide real-time, low-latency streaming conversations with Gemini models, but serve different development and deployment needs.

Throughout this guide, we use **"Live API"** to refer to both platforms collectively, specifying "Gemini Live API" or "Vertex AI Live API" only when discussing platform-specific features or differences.

### What is the Live API?

Live API is Google's real-time conversational AI technology that enables **low-latency Bidi-streaming** with Gemini models. Unlike traditional request-response APIs, Live API establishes persistent WebSocket connections that support:

**Core Capabilities:**

- **Multimodal streaming**: Processes continuous streams of audio, video, and text in real-time
- **Voice Activity Detection (VAD)**: Automatically detects when users finish speaking, enabling natural turn-taking without explicit signals. The AI knows when to start responding and when to wait for more input
- **Immediate responses**: Delivers human-like spoken or text responses with minimal latency
- **Intelligent interruption**: Enables users to interrupt the AI mid-response, just like human conversations
- **Audio Transcription**: Real-time transcription of both user input and model output, enabling accessibility features and conversation logging without separate transcription services
- **Session Management**: Long conversations can span multiple connections through session resumption, with the API preserving full conversation history and context across reconnections
- **Tool Integration**: Function calling works seamlessly in streaming mode, with tools executing in the background while conversation continues

**Native Audio Model Features:**

- **Proactive Audio**: The model can initiate responses based on context awareness, creating more natural interactions where the AI offers help or clarification proactively (Native Audio models only)
- **Affective Dialog**: Advanced models understand tone of voice and emotional context, adapting responses to match the conversational mood and user sentiment (Native Audio models only)

!!! note "Learn More"

    For detailed information about Native Audio models and these features, see [Part 5: Audio and Video - Proactivity and Affective Dialog](part5.md#proactivity-and-affective-dialog).

**Technical Specifications:**

- **Audio input**: 16-bit PCM at 16kHz (mono)
- **Audio output**: 16-bit PCM at 24kHz (native audio models)
- **Video input**: 1 frame per second, recommended 768x768 resolution
- **Context windows**: Varies by model (typically 32k-128k tokens for Live API models). See [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini) for specific limits.
- **Languages**: 24+ languages supported with automatic detection

### Gemini Live API vs Vertex AI Live API

Both APIs provide the same core Live API technology, but differ in deployment platform, authentication, and enterprise features:

| **Aspect** | **Gemini Live API** | **Vertex AI Live API** |
|--------|-----------------|-------------------|
| **Access** | Google AI Studio | Google Cloud |
| **Authentication** | API key (`GOOGLE_API_KEY`) | Google Cloud credentials (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) |
| **Best for** | Rapid prototyping, development, experimentation | Production deployments, enterprise applications |
| **Session Duration** | Audio-only: 15 min<br>Audio+video: 2 min<br>With [Part 4: Context Window Compression](part4.md#live-api-context-window-compression): Unlimited | Both: 10 min<br>With [Part 4: Context Window Compression](part4.md#live-api-context-window-compression): Unlimited |
| **Concurrent Sessions** | Tier-based quotas (see [API quotas](https://ai.google.dev/gemini-api/docs/quota)) | Up to 1,000 per project (configurable via quota requests) |
| **Enterprise Features** | Basic | Advanced monitoring, logging, SLAs, session resumption (24h) |
| **Setup Complexity** | Minimal (API key only) | Requires Google Cloud project setup |
| **API Version** | `v1beta` | `v1beta1` |
| **API Endpoint** | `generativelanguage.googleapis.com` | `{location}-aiplatform.googleapis.com` |
| **Billing** | Usage tracked via API key | Google Cloud project billing |

!!! note "Live API Reference Notes"

    **Concurrent session limits**: Quota-based and may vary by account tier or configuration. Check your current quotas in Google AI Studio or Google Cloud Console.

    **Official Documentation**: [Gemini Live API Guide](https://ai.google.dev/gemini-api/docs/live-guide) | [Vertex AI Live API Overview](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## 1.3 ADK Bidi-streaming: For Building Realtime Agent Applications

Building realtime Agent applications from scratch presents significant engineering challenges. While Live API provides the underlying streaming technology, integrating it into production applications requires solving complex problems: managing WebSocket connections and reconnection logic, orchestrating tool execution and response handling, persisting conversation state across sessions, coordinating concurrent data flows for multimodal inputs, and handling platform differences between development and production environments.

ADK transforms these challenges into simple, declarative APIs. Instead of spending months building infrastructure for session management, tool orchestration, and state persistence, developers can focus on defining agent behavior and creating user experiences. This section explores what ADK handles automatically and why it's the recommended path for building production-ready streaming applications.

**Raw Live API v. ADK Bidi-streaming:**

| Feature | Raw Live API (`google-genai` SDK) | ADK Bidi-streaming (`adk-python` and `adk-java` SDK) |
|---------|-----------------------------------|------------------------------------------------------|
| **Agent Framework** | ❌ Not available | ✅ Single agent, multi-agent with sub-agents, and sequential workflow agents, Tool ecosystem, Deployment ready, Evaluation, Security and more (see [ADK Agent docs](https://google.github.io/adk-docs/agents/)) |
| **Tool Execution** | ❌ Manual tool execution and response handling | ✅ Automatic tool execution (see [Part 3: Tool Call Events](part3.md#tool-call-events)) |
| **Connection Management** | ❌ Manual reconnection and session resumption | ✅ Automatic reconnection and session resumption (see [Part 4: Live API Session Resumption](part4.md#live-api-session-resumption)) |
| **Event Model** | ❌ Custom event structures and serialization | ✅ Unified event model with metadata (see [Part 3: Event Handling](part3.md)) |
| **Async Event Processing Framework** | ❌ Manual async coordination and stream handling | ✅ `LiveRequestQueue`, `run_live()` async generator, automatic bidirectional flow coordination (see [Part 2](part2.md) and [Part 3](part3.md)) |
| **App-level Session Persistence** | ❌ Manual implementation | ✅ SQL databases (PostgreSQL, MySQL, SQLite), Vertex AI, in-memory (see [ADK Session docs](https://google.github.io/adk-docs/sessions/)) |

### Platform Flexibility

One of ADK's most powerful features is its transparent support for both [Gemini Live API](https://ai.google.dev/gemini-api/docs/live) and [Vertex AI Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api). This platform flexibility enables a seamless development-to-production workflow: develop locally with Gemini API using free API keys, then deploy to production with Vertex AI using enterprise Google Cloud infrastructure—all **without changing application code**, only environment configuration.

#### How Platform Selection Works

ADK uses the `GOOGLE_GENAI_USE_VERTEXAI` environment variable to determine which Live API platform to use:

- `GOOGLE_GENAI_USE_VERTEXAI=FALSE` (or not set): Uses Gemini Live API via Google AI Studio
- `GOOGLE_GENAI_USE_VERTEXAI=TRUE`: Uses Vertex AI Live API via Google Cloud

This environment variable is read by the underlying `google-genai` SDK when ADK creates the LLM connection. No code changes are needed when switching platforms—only environment configuration changes.

##### Development Phase: Gemini Live API (Google AI Studio)

```bash
# .env.development
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_api_key_here
```

**Benefits:**

- Rapid prototyping with free API keys from Google AI Studio
- No Google Cloud setup required
- Instant experimentation with streaming features
- Zero infrastructure costs during development

##### Production Phase: Vertex AI Live API (Google Cloud)

```bash
# .env.production
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

**Benefits:**

- Enterprise-grade infrastructure via Google Cloud
- Advanced monitoring, logging, and cost controls
- Integration with existing Google Cloud services
- Production SLAs and support
- **No code changes required** - just environment configuration

By handling the complexity of session management, tool orchestration, state persistence, and platform differences, ADK lets you focus on building intelligent agent experiences rather than wrestling with streaming infrastructure. The same code works seamlessly across development and production environments, giving you the full power of Bidi-streaming without the implementation burden.

## 1.4 ADK Bidi-streaming Architecture Overview

Now that you understand Live API technology and why ADK adds value, let's explore how ADK actually works. This section maps the complete data flow from your application through ADK's pipeline to Live API and back, showing which components handle which responsibilities.

You'll see how key components like `LiveRequestQueue`, `Runner`, and `Agent` orchestrate streaming conversations without requiring you to manage WebSocket connections, coordinate async flows, or handle platform-specific API differences.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Application"
        subgraph "Client"
            C1["Web / Mobile"]
        end

        subgraph "Transport Layer"
            T1["WebSocket / SSE (e.g. FastAPI)"]
        end
    end

    subgraph "ADK"
        subgraph "ADK Bidi-streaming"
            L1[LiveRequestQueue]
            L2[Runner]
            L3[Agent]
            L4[LLM Flow]
        end

        subgraph "LLM Integration"
            G1[GeminiLlmConnection]
            G2[Gemini Live API / Vertex AI Live API]
        end
    end

    C1 <--> T1
    T1 -->|"live_request_queue.send()"| L1
    L1 -->|"runner.run_live(queue)"| L2
    L2 -->|"agent.run_live()"| L3
    L3 -->|"_llm_flow.run_live()"| L4
    L4 -->|"llm.connect()"| G1
    G1 <--> G2
    G1 -->|"yield LlmResponse"| L4
    L4 -->|"yield Event"| L3
    L3 -->|"yield Event"| L2
    L2 -->|"yield Event"| T1

    classDef external fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef adk fill:#f3e5f5,stroke:#4a148c,stroke-width:2px

    class C1,T1 external
    class L1,L2,L3,L4,G1,G2 adk
```

| Developer provides: | ADK provides: | Live API provide: |
|---------------------|---------------|------------------|
| **Web / Mobile**: Frontend applications that users interact with, handling UI/UX, user input capture, and response display<br><br>**[WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) / [SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) Server**: Real-time communication server (such as [FastAPI](https://fastapi.tiangolo.com/)) that manages client connections, handles streaming protocols, and routes messages between clients and ADK<br><br>**`Agent`**: Custom AI agent definition with specific instructions, tools, and behavior tailored to your application's needs | **[LiveRequestQueue](https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/agents/live_request_queue.py)**: Message queue that buffers and sequences incoming user messages (text content, audio blobs, control signals) for orderly processing by the agent<br><br>**[Runner](https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/runners.py)**: Execution engine that orchestrates agent sessions, manages conversation state, and provides the `run_live()` streaming interface<br><br>**[RunConfig](https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/agents/run_config.py)**: Configuration for streaming behavior, modalities, and advanced features<br><br>**Internal components** (managed automatically, not directly used by developers): [LLM Flow](https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/flows/llm_flows/base_llm_flow.py) for processing pipeline and [GeminiLlmConnection](https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/models/gemini_llm_connection.py) for protocol translation | **[Gemini Live API](https://ai.google.dev/gemini-api/docs/live)** (via Google AI Studio) and **[Vertex AI Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)** (via Google Cloud): Google's real-time language model services that process streaming input, generate responses, handle interruptions, support multimodal content (text, audio, video), and provide advanced AI capabilities like function calling and contextual understanding |

This architecture demonstrates ADK's clear separation of concerns: your application handles user interaction and transport protocols, ADK manages the streaming orchestration and state, and Live API provide the AI intelligence. By abstracting away the complexity of LLM-side streaming connection management, event loops, and protocol translation, ADK enables you to focus on building agent behavior and user experiences rather than streaming infrastructure.

## 1.5 ADK Bidi-streaming Application Lifecycle

ADK Bidi-streaming integrates Live API session into the ADK framework's application lifecycle. This integration creates a four-phase lifecycle that combines ADK's agent management with Live API's real-time streaming capabilities:

- **Phase 1: Application Initialization** (Once at Startup)
  - ADK Application initialization
    - Create an [Agent](https://google.github.io/adk-docs/agents/): for interacting with users, utilize external tools, and coordinate with other agents.
    - Create a [SessionService](https://google.github.io/adk-docs/sessions/session/#managing-sessions-with-a-sessionservice): for getting or creating ADK `Session`
    - Create a [Runner](https://google.github.io/adk-docs/runtime/): for providing a runtime for the Agent

- **Phase 2: Session Initialization** (Once per User Session)
  - ADK `Session` initialization:
    - Get or Create an ADK `Session` using the `SessionService`
  - ADK Bidi-streaming initialization:
    - Create a [RunConfig](part4.md) for configuring ADK Bidi-streaming
    - Create a [LiveRequestQueue](part2.md) for sending user messages to the `Agent`
    - Start a [run_live()](part3.md) event loop

- **Phase 3: Bidi-streaming with `run_live()` event loop** (One or More Times per User Session)
  - Upstream: User sends message to the agent with `LiveRequestQueue`
  - Downstream: Agent responds to the user with `Event`

- **Phase 4: Terminate Live API session** (One or More Times per User Session)
  - `LiveRequestQueue.close()`

**Lifecycle Flow Overview:**

```mermaid
graph TD
    A[Phase 1: Application Init<br/>Once at Startup] --> B[Phase 2: Session Init<br/>Per User Connection]
    B --> C[Phase 3: Bidi-streaming<br/>Active Communication]
    C --> D[Phase 4: Terminate<br/>Close Session]
    D -.New Connection.-> B

    style A fill:#e3f2fd
    style B fill:#e8f5e9
    style C fill:#fff3e0
    style D fill:#ffebee
```

This flowchart shows the high-level lifecycle phases and how they connect. The detailed sequence diagram below illustrates the specific components and interactions within each phase.

```mermaid
sequenceDiagram
    participant Client
    participant App as Application Server
    participant Queue as LiveRequestQueue
    participant Runner
    participant Agent
    participant API as Live API

    rect rgb(230, 240, 255)
        Note over App: Phase 1: Application Initialization (Once at Startup)
        App->>Agent: 1. Create Agent(model, tools, instruction)
        App->>App: 2. Create SessionService()
        App->>Runner: 3. Create Runner(app_name, agent, session_service)
    end

    rect rgb(240, 255, 240)
        Note over Client,API: Phase 2: Session Initialization (Every Time a User Connected)
        Client->>App: 1. WebSocket connect(user_id, session_id)
        App->>App: 2. get_or_create_session(app_name, user_id, session_id)
        App->>App: 3. Create RunConfig(streaming_mode, modalities)
        App->>Queue: 4. Create LiveRequestQueue()
        App->>Runner: 5. Start run_live(user_id, session_id, queue, config)
        Runner->>API: Connect to Live API session
    end

    rect rgb(255, 250, 240)
        Note over Client,API: Phase 3: Bidi-streaming with run_live() Event Loop

        par Upstream: User sends messages via LiveRequestQueue
            Client->>App: User message (text/audio/video)
            App->>Queue: send_content() / send_realtime()
            Queue->>Runner: Buffered request
            Runner->>Agent: Process request
            Agent->>API: Stream to Live API
        and Downstream: Agent responds via Events
            API->>Agent: Streaming response
            Agent->>Runner: Process response
            Runner->>App: yield Event (text/audio/tool/turn)
            App->>Client: Forward Event via WebSocket
        end

        Note over Client,API: (Event loop continues until close signal)
    end

    rect rgb(255, 240, 240)
        Note over Client,API: Phase 4: Terminate Live API session
        Client->>App: WebSocket disconnect
        App->>Queue: close()
        Queue->>Runner: Close signal
        Runner->>API: Disconnect from Live API
        Runner->>App: run_live() exits
    end
```

In the following sections, you'll see each phase detailed, showing exactly when to create each component and how they work together. Understanding this lifecycle pattern is essential for building robust streaming applications that can handle multiple concurrent sessions efficiently.


### Phase 1: Application Initialization

These components are created once when your application starts and shared across all streaming sessions. They define your agent's capabilities, manage conversation history, and orchestrate the streaming execution.

#### Define Your Agent

The `Agent` is the core of your streaming application—it defines what your AI can do, how it should behave, and which AI model powers it. You configure your agent with a specific model, tools it can use (like Google Search or custom APIs), and instructions that shape its personality and behavior.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/google_search_agent/agent.py#L10-L15" target="_blank">agent.py:10-15</a>'
"""Google Search Agent definition for ADK Bidi-streaming demo."""

import os
from google.adk.agents import Agent
from google.adk.tools import google_search

# Default models for Live API with native audio support:
# - Gemini Live API: gemini-2.5-flash-native-audio-preview-12-2025
# - Vertex AI Live API: gemini-live-2.5-flash-native-audio
agent = Agent(
    name="google_search_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[google_search],
    instruction="You are a helpful assistant that can search the web."
)
```

The agent instance is **stateless and reusable**—you create it once and use it for all streaming sessions. Agent configuration is covered in the [ADK Agent documentation](https://google.github.io/adk-docs/agents/).

!!! note "Model Availability"

    For the latest supported models and their capabilities, see [Part 5: Understanding Audio Model Architectures](part5.md#understanding-audio-model-architectures).

!!! note "Agent vs LlmAgent"

    `Agent` is the recommended shorthand for `LlmAgent` (both are imported from `google.adk.agents`). They are identical - use whichever you prefer. This guide uses `Agent` for brevity, but you may see `LlmAgent` in other ADK documentation and examples.

#### Define Your SessionService

The ADK [Session](https://google.github.io/adk-docs/sessions/session/) manages conversation state and history across streaming sessions. It stores and retrieves session data, enabling features like conversation resumption and context persistence.

To create a `Session`, or get an existing one for a specified `session_id`, every ADK application needs to have a [SessionService](https://google.github.io/adk-docs/sessions/session/#managing-sessions-with-a-sessionservice). For development purpose, ADK provides a simple `InMemorySessionService` that will lose the `Session` state when the application shuts down.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L37" target="_blank">main.py:37</a>'
from google.adk.sessions import InMemorySessionService

# Define your session service
session_service = InMemorySessionService()
```

For production applications, choose a persistent session service based on your infrastructure:

**Use `DatabaseSessionService` if:**

- You need persistent storage with SQLite, PostgreSQL, or MySQL
- You're building single-server apps (SQLite) or multi-server deployments (PostgreSQL/MySQL)
- You want full control over data storage and backups
- Examples:
    - SQLite: `DatabaseSessionService(db_url="sqlite:///./sessions.db")`
    - PostgreSQL: `DatabaseSessionService(db_url="postgresql://user:pass@host/db")`

**Use `VertexAiSessionService` if:**

- You're already using Google Cloud Platform
- You want managed storage with built-in scalability
- You need tight integration with Vertex AI features
- Example: `VertexAiSessionService(project="my-project")`

Both provide session persistence capabilities—choose based on your infrastructure and scale requirements. With persistent session services, the state of the `Session` will be preserved even after application shutdown. See the [ADK Session Management documentation](https://google.github.io/adk-docs/sessions/) for more details.

#### Define Your Runner

The [Runner](https://google.github.io/adk-docs/runtime/) provides the runtime for the `Agent`. It manages the conversation flow, coordinates tool execution, handles events, and integrates with session storage. You create one runner instance at application startup and reuse it for all streaming sessions.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L50" target="_blank">main.py:50,53</a>'
from google.adk.runners import Runner

APP_NAME = "bidi-demo"

# Define your runner
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service
)
```

The `app_name` parameter is required and identifies your application in session storage. All sessions for your application are organized under this name.

### Phase 2: Session Initialization

#### Get or Create Session

ADK `Session` provides a "conversation thread" of the Bidi-streaming application. Just like you wouldn't start every text message from scratch, agents need context regarding the ongoing interaction. `Session` is the ADK object designed specifically to track and manage these individual conversation threads.

##### ADK `Session` vs Live API session

ADK `Session` (managed by SessionService) provides **persistent conversation storage** across multiple Bidi-streaming sessions (can spans hours, days or even months), while Live API session (managed by Live API backend) is **a transient streaming context** that exists only during single Bidi-streaming event loop (spans minutes or hours typically) that we will discuss later. When the loop starts, ADK initializes the Live API session with history from the ADK `Session`, then updates the ADK `Session` as new events occur.

!!! note "Learn More"

    For a detailed comparison with sequence diagrams, see [Part 4: ADK `Session` vs Live API session](part4.md#adk-session-vs-live-api-session).

##### Session Identifiers Are Application-Defined

Sessions are identified by three parameters: `app_name`, `user_id`, and `session_id`. This three-level hierarchy enables multi-tenant applications where each user can have multiple concurrent sessions.

Both `user_id` and `session_id` are **arbitrary string identifiers** that you define based on your application's needs. ADK performs no format validation beyond `.strip()` on `session_id`—you can use any string values that make sense for your application:

- **`user_id` examples**: User UUIDs (`"550e8400-e29b-41d4-a716-446655440000"`), email addresses (`"alice@example.com"`), database IDs (`"user_12345"`), or simple identifiers (`"demo-user"`)
- **`session_id` examples**: Custom session tokens, UUIDs, timestamp-based IDs (`"session_2025-01-27_143022"`), or simple identifiers (`"demo-session"`)

**Auto-generation**: If you pass `session_id=None` or an empty string to `create_session()`, ADK automatically generates a UUID for you (e.g., `"550e8400-e29b-41d4-a716-446655440000"`).

**Organizational hierarchy**: These identifiers organize sessions in a three-level structure:

```text
app_name → user_id → session_id → Session
```

This design enables scenarios like:

- Multi-tenant applications where different users have isolated conversation spaces
- Single users with multiple concurrent chat threads (e.g., different topics)
- Per-device or per-browser session isolation

##### Recommended Pattern: Get-or-Create

The recommended production pattern is to check if a session exists first, then create it only if needed. This approach safely handles both new sessions and conversation resumption:

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L155-L161" target="_blank">main.py:155-161</a>'
# Get or create session (handles both new sessions and reconnections)
session = await session_service.get_session(
    app_name=APP_NAME,
    user_id=user_id,
    session_id=session_id
)
if not session:
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
```

This pattern works correctly in all scenarios:

- **New conversations**: If the session doesn't exist, it's created automatically
- **Resuming conversations**: If the session already exists (e.g., reconnection after network interruption), the existing session is reused with full conversation history
- **Idempotent**: Safe to call multiple times without errors

**Important**: The session must exist before calling `runner.run_live()` with the same identifiers. If the session doesn't exist, `run_live()` will raise `ValueError: Session not found`.

#### Create RunConfig

[RunConfig](part4.md) defines the streaming behavior for this specific session—which modalities to use (text or audio), whether to enable transcription, voice activity detection, proactivity, and other advanced features.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L110-L124" target="_blank">main.py:110-124</a>'
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

# Native audio models require AUDIO response modality with audio transcription
response_modalities = ["AUDIO"]
run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=response_modalities,
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
    session_resumption=types.SessionResumptionConfig()
)
```

`RunConfig` is **session-specific**—each streaming session can have different configuration. For example, one user might prefer text-only responses while another uses voice mode. See [Part 4: Understanding RunConfig](part4.md) for complete configuration options.

#### Create LiveRequestQueue

`LiveRequestQueue` is the communication channel for sending messages to the agent during streaming. It's a thread-safe async queue that buffers user messages (text content, audio blobs, activity signals) for orderly processing.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L163" target="_blank">main.py:163</a>'
from google.adk.agents.live_request_queue import LiveRequestQueue

live_request_queue = LiveRequestQueue()
```

`LiveRequestQueue` is **session-specific and stateful**—you create a new queue for each streaming session and close it when the session ends. Unlike `Agent` and `Runner`, queues cannot be reused across sessions.

!!! warning "One Queue Per Session"

    Never reuse a `LiveRequestQueue` across multiple streaming sessions. Each call to `run_live()` requires a fresh queue. Reusing queues can cause message ordering issues and state corruption.

    The close signal persists in the queue (see [`live_request_queue.py:59-60`](https://github.com/google/adk-python/blob/fd2c0f556b786417a9f6add744827b07e7a06b7d/src/google/adk/agents/live_request_queue.py#L66-L67)) and terminates the sender loop (see [`base_llm_flow.py:264-266`](https://github.com/google/adk-python/blob/fd2c0f556b786417a9f6add744827b07e7a06b7d/src/google/adk/flows/llm_flows/base_llm_flow.py#L260-L262)). Reusing a queue would carry over this signal and any remaining messages from the previous session.

### Phase 3: Bidi-streaming with `run_live()` event loop

Once the streaming loop is running, you can send messages to the agent and receive responses **concurrently**—this is Bidi-streaming in action. The agent can be generating a response while you're sending new input, enabling natural interruption-based conversation.

#### Send Messages to the Agent

Use `LiveRequestQueue` methods to send different types of messages to the agent during the streaming session:

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L169-L217" target="_blank">main.py:169-217</a>'
from google.genai import types

# Send text content
content = types.Content(parts=[types.Part(text=json_message["text"])])
live_request_queue.send_content(content)

# Send audio blob
audio_blob = types.Blob(
    mime_type="audio/pcm;rate=16000",
    data=audio_data
)
live_request_queue.send_realtime(audio_blob)
```

These methods are **non-blocking**—they immediately add messages to the queue without waiting for processing. This enables smooth, responsive user experiences even during heavy AI processing.

See [Part 2: Sending messages with LiveRequestQueue](part2.md) for detailed API documentation.

#### Receive and Process Events

The `run_live()` async generator continuously yields `Event` objects as the agent processes input and generates responses. Each event represents a discrete occurrence—partial text generation, audio chunks, tool execution, transcription, interruption, or turn completion.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L219-L234" target="_blank">main.py:219-234</a>'
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config
):
    event_json = event.model_dump_json(exclude_none=True, by_alias=True)
    await websocket.send_text(event_json)
```

Events are designed for **streaming delivery**—you receive partial responses as they're generated, not just complete messages. This enables real-time UI updates and responsive user experiences.

See [Part 3: Event handling with run_live()](part3.md) for comprehensive event handling patterns.

### Phase 4: Terminate Live API session

When the streaming session should end (user disconnects, conversation completes, timeout occurs), close the queue gracefully to signal termination to terminate the Live API session.

#### Close the Queue

Send a close signal through the queue to terminate the streaming loop:

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L253" target="_blank">main.py:253</a>'
live_request_queue.close()
```

This signals `run_live()` to stop yielding events and exit the async generator loop. The agent completes any in-progress processing and the streaming session ends cleanly.

### FastAPI Application Example

Here's a complete FastAPI WebSocket application showing all four phases integrated with proper Bidi-streaming. The key pattern is **upstream/downstream tasks**: the upstream task receives messages from WebSocket and sends them to `LiveRequestQueue`, while the downstream task receives `Event` objects from `run_live()` and sends them to WebSocket.

!!! note "Complete Demo Implementation"

    For the production-ready implementation with multimodal support (text, audio, image), see the complete [`main.py`](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py) file.

**Complete Implementation:**

```python
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google_search_agent.agent import agent

# ========================================
# Phase 1: Application Initialization (once at startup)
# ========================================

APP_NAME = "bidi-demo"

app = FastAPI()

# Define your session service
session_service = InMemorySessionService()

# Define your runner
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service
)

# ========================================
# WebSocket Endpoint
# ========================================

@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str) -> None:
    await websocket.accept()

    # ========================================
    # Phase 2: Session Initialization (once per streaming session)
    # ========================================

    # Create RunConfig
    response_modalities = ["AUDIO"]
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=response_modalities,
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        session_resumption=types.SessionResumptionConfig()
    )

    # Get or create session
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

    # Create LiveRequestQueue
    live_request_queue = LiveRequestQueue()

    # ========================================
    # Phase 3: Active Session (concurrent bidirectional communication)
    # ========================================

    async def upstream_task() -> None:
        """Receives messages from WebSocket and sends to LiveRequestQueue."""
        try:
            while True:
                # Receive text message from WebSocket
                data: str = await websocket.receive_text()

                # Send to LiveRequestQueue
                content = types.Content(parts=[types.Part(text=data)])
                live_request_queue.send_content(content)
        except WebSocketDisconnect:
            # Client disconnected - signal queue to close
            pass

    async def downstream_task() -> None:
        """Receives Events from run_live() and sends to WebSocket."""
        async for event in runner.run_live(
            user_id=user_id,
            session_id=session_id,
            live_request_queue=live_request_queue,
            run_config=run_config
        ):
            # Send event as JSON to WebSocket
            await websocket.send_text(
                event.model_dump_json(exclude_none=True, by_alias=True)
            )

    # Run both tasks concurrently
    try:
        await asyncio.gather(
            upstream_task(),
            downstream_task(),
            return_exceptions=True
        )
    finally:
        # ========================================
        # Phase 4: Session Termination
        # ========================================

        # Always close the queue, even if exceptions occurred
        live_request_queue.close()
```

!!! note "Async Context Required"

    All ADK bidirectional streaming applications **must run in an async context**. This requirement comes from multiple components:

    - **`run_live()`**: ADK's streaming method is an async generator with no synchronous wrapper (unlike `run()`)
    - **Session operations**: `get_session()` and `create_session()` are async methods
    - **WebSocket operations**: FastAPI's `websocket.accept()`, `receive_text()`, and `send_text()` are all async
    - **Concurrent tasks**: The upstream/downstream pattern requires `asyncio.gather()` for concurrent execution

    All code examples in this guide assume you're running in an async context (e.g., within an async function or coroutine). For consistency with ADK's official documentation patterns, examples show the core logic without boilerplate wrapper functions.

### Key Concepts

**Upstream Task (WebSocket → LiveRequestQueue)**

The upstream task continuously receives messages from the WebSocket client and forwards them to the `LiveRequestQueue`. This enables the user to send messages to the agent at any time, even while the agent is generating a response.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L169-L217" target="_blank">main.py:169-217</a>'
async def upstream_task() -> None:
    """Receives messages from WebSocket and sends to LiveRequestQueue."""
    try:
        while True:
            data: str = await websocket.receive_text()
            content = types.Content(parts=[types.Part(text=data)])
            live_request_queue.send_content(content)
    except WebSocketDisconnect:
        pass  # Client disconnected
```

**Downstream Task (run_live() → WebSocket)**

The downstream task continuously receives `Event` objects from `run_live()` and sends them to the WebSocket client. This streams the agent's responses, tool executions, transcriptions, and other events to the user in real-time.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L219-L234" target="_blank">main.py:219-234</a>'
async def downstream_task() -> None:
    """Receives Events from run_live() and sends to WebSocket."""
    async for event in runner.run_live(
        user_id=user_id,
        session_id=session_id,
        live_request_queue=live_request_queue,
        run_config=run_config
    ):
        await websocket.send_text(
            event.model_dump_json(exclude_none=True, by_alias=True)
        )
```

**Concurrent Execution with Cleanup**

Both tasks run concurrently using `asyncio.gather()`, enabling true Bidi-streaming. The `try/finally` block ensures `LiveRequestQueue.close()` is called even if exceptions occur, minimizing the session resource usage.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L238-L253" target="_blank">main.py:238-253</a>'
try:
    await asyncio.gather(
        upstream_task(),
        downstream_task(),
        return_exceptions=True
    )
finally:
    live_request_queue.close()  # Always cleanup
```

This pattern—concurrent upstream/downstream tasks with guaranteed cleanup—is the foundation of production-ready streaming applications. The lifecycle pattern (initialize once, stream many times) enables efficient resource usage and clean separation of concerns, with application components remaining stateless and reusable while session-specific state is isolated in `LiveRequestQueue`, `RunConfig`, and session records.

#### Production Considerations

This example shows the core pattern. For production applications, consider:

- **Error handling (ADK)**: Add proper error handling for ADK streaming events. For details on error event handling, see [Part 3: Error Events](part3.md#error-events).
    - Handle task cancellation gracefully by catching `asyncio.CancelledError` during shutdown
    - Check exceptions from `asyncio.gather()` with `return_exceptions=True` - exceptions don't propagate automatically
- **Error handling (Web)**: Handle web application-specific errors in upstream/downstream tasks. For example, with FastAPI you would need to:
    - Catch `WebSocketDisconnect` (client disconnected), `ConnectionClosedError` (connection lost), and `RuntimeError` (sending to closed connection)
    - Validate WebSocket connection state before sending with `websocket.client_state` to prevent errors when the connection is closed
- **Authentication and authorization**: Implement authentication and authorization for your endpoints
- **Rate limiting and quotas**: Add rate limiting and timeout controls. For guidance on concurrent sessions and quota management, see [Part 4: Concurrent Live API Sessions and Quota Management](part4.md#concurrent-live-api-sessions-and-quota-management).
- **Structured logging**: Use structured logging for debugging.
- **Persistent session services**: Consider using persistent session services (`DatabaseSessionService` or `VertexAiSessionService`). See the [ADK Session Services documentation](https://google.github.io/adk-docs/sessions/) for more details.

## 1.6 What We Will Learn

This guide takes you through ADK's Bidi-streaming architecture step by step, following the natural flow of streaming applications: how messages travel upstream from users to agents, how events flow downstream from agents to users, how to configure session behaviors, and how to implement multimodal features. Each part focuses on a specific component of the streaming architecture with practical patterns you can apply immediately:

- **[Part 2: Sending messages with LiveRequestQueue](part2.md)** - Learn how ADK's `LiveRequestQueue` provides a unified interface for handling text, audio, and control messages. You'll understand the `LiveRequest` message model, how to send different types of content, manage user activity signals, and handle graceful session termination through a single, elegant API.

- **[Part 3: Event handling with run_live()](part3.md)** - Master event handling in ADK's streaming architecture. Learn how to process different event types (text, audio, transcriptions, tool calls), manage conversation flow with interruption and turn completion signals, serialize events for network transport, and leverage ADK's automatic tool execution. Understanding event handling is essential for building responsive streaming applications.

- **[Part 4: Understanding RunConfig](part4.md)** - Configure sophisticated streaming behaviors including multimodal interactions, intelligent proactivity, session resumption, and cost controls. Learn which features are available on different models and how to declaratively control your streaming sessions through RunConfig.

- **[Part 5: How to Use Audio, Image and Video](part5.md)** - Implement voice and video features with ADK's multimodal capabilities. Understand audio specifications, streaming architectures, voice activity detection, audio transcription, and best practices for building natural voice-enabled AI experiences.

### Prerequisites and Learning Resources

For building an ADK Bidi-streaming application in production, we recommend having basic knowledge of the following technologies:

**[ADK (Agent Development Kit)](https://google.github.io/adk-docs/)**

Google's production-ready framework for building AI agents with streaming capabilities. ADK provides high-level abstractions for session management, tool orchestration, and state persistence, eliminating the need to implement low-level streaming infrastructure from scratch.

**Live API ([Gemini Live API](https://ai.google.dev/gemini-api/docs/live) and [Vertex AI Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api))**

Google's real-time conversational AI technology that enables low-latency bidirectional streaming with Gemini models. The Live API provides the underlying WebSocket-based protocol that powers ADK's streaming capabilities, handling multimodal input/output and natural conversation flow.

**[Python Async Programming](https://docs.python.org/3/library/asyncio.html)**

Python's built-in support for asynchronous programming using `async`/`await` syntax and the `asyncio` library. ADK streaming is built on async generators and coroutines, requiring familiarity with concepts like async functions, awaiting tasks, and concurrent execution with `asyncio.gather()`.

**[Pydantic](https://docs.pydantic.dev/)**

A Python library for data validation and settings management using Python type annotations. ADK uses Pydantic models extensively for structured data (like `Event`, `RunConfig`, and `Content`), providing type safety, automatic validation, and JSON serialization via `.model_dump_json()`.

**[FastAPI](https://fastapi.tiangolo.com/)**

A modern, high-performance Python web framework for building APIs with automatic OpenAPI documentation. FastAPI's native support for WebSockets and async request handling makes it ideal for building ADK streaming endpoints. FastAPI is included in the `adk-python` package and used by ADK's `adk web` tool for rapid prototyping. Alternative frameworks with WebSocket support (like Flask-SocketIO or Starlette) can also be used.

**[WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)**

A protocol providing full-duplex (two-way) communication channels over a single TCP connection. WebSockets enable real-time bidirectional data flow between clients and servers, making them the standard transport for streaming applications. Unlike HTTP request-response, WebSocket connections persist, allowing both parties to send messages at any time.

**[SSE (Server-Sent Events)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)**

A standard for servers to push data to web clients over HTTP. Unlike WebSockets, SSE is unidirectional (server-to-client only), making it simpler but less flexible. SSE is useful for streaming agent responses when you don't need client-to-server streaming, such as when user input comes through separate HTTP POST requests.

While this guide covers ADK-specific concepts thoroughly, familiarity with these underlying technologies will help you build more robust production applications.

## Summary

In this introduction, you learned how ADK transforms complex real-time streaming infrastructure into a developer-friendly framework. We covered the fundamentals of Live API's bidirectional streaming capabilities, examined how ADK simplifies the streaming complexity through abstractions like `LiveRequestQueue`, `Runner`, and `run_live()`, and explored the complete application lifecycle from initialization through session termination. You now understand how ADK handles the heavy lifting—LLM-side streaming connection management, state persistence, platform differences, and event coordination—so you can focus on building intelligent agent experiences. With this foundation in place, you're ready to dive into the specifics of sending messages, handling events, configuring sessions, and implementing multimodal features in the following parts.

---

[Next: Part 2: Sending Messages with LiveRequestQueue](part2.md) →
