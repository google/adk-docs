# Gemini API Google Search tool for ADK

Supported in ADKPython v0.1.0TypeScript v0.2.0Go v0.1.0Java v0.2.0

The `google_search` tool allows the agent to perform web searches using Google Search. The `google_search` tool is only compatible with Gemini 2 models. For further details of the tool, see [Understanding Google Search grounding](/adk-docs/grounding/google_search_grounding/).

Additional requirements when using the `google_search` tool

When you use grounding with Google Search, and you receive Search suggestions in your response, you must display the Search suggestions in production and in your applications. For more information on grounding with Google Search, see Grounding with Google Search documentation for [Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) or [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions). The UI code (HTML) is returned in the Gemini response as `renderedContent`, and you will need to show the HTML in your app, in accordance with the policy.

Warning: Single tool per agent limitation

This tool can only be used ***by itself*** within an agent instance. For more information about this limitation and workarounds, see [Limitations for ADK tools](/adk-docs/tools/limitations/#one-tool-one-agent).

```py
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

APP_NAME="google_search_agent"
USER_ID="user1234"
SESSION_ID="1234"


root_agent = Agent(
    name="basic_search_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions using Google Search.",
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    # google_search is a pre-built tool which allows the agent to perform Google searches.
    tools=[google_search]
)

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("what's the latest ai news?")
```

```typescript
import {GOOGLE_SEARCH, LlmAgent} from '@google/adk';

export const rootAgent = new LlmAgent({
  model: 'gemini-2.5-flash',
  name: 'root_agent',
  description:
      'an agent whose job it is to perform Google search queries and answer questions about the results.',
  instruction:
      'You are an agent whose job is to perform Google search queries and answer questions about the results.',
  tools: [GOOGLE_SEARCH],
});
```

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

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/geminitool"
    "google.golang.org/genai"
)

func createSearchAgent(ctx context.Context) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
    if err != nil {
        return nil, fmt.Errorf("failed to create model: %v", err)
    }

    return llmagent.New(llmagent.Config{
        Name:        "basic_search_agent",
        Model:       model,
        Description: "Agent to answer questions using Google Search.",
        Instruction: "I can answer your questions by searching the web. Just ask me anything!",
        Tools:       []tool.Tool{geminitool.GoogleSearch{}},
    })
}

const (
    userID  = "user1234"
    appName = "Google Search_agent"
)

func callAgent(ctx context.Context, a agent.Agent, prompt string) error {
    sessionService := session.InMemoryService()
    session, err := sessionService.Create(ctx, &session.CreateRequest{
        AppName: appName,
        UserID:  userID,
    })
    if err != nil {
        return fmt.Errorf("failed to create the session service: %v", err)
    }

    config := runner.Config{
        AppName:        appName,
        Agent:          a,
        SessionService: sessionService,
    }
    r, err := runner.New(config)
    if err != nil {
        return fmt.Errorf("failed to create the runner: %v", err)
    }

    sessionID := session.Session.ID()
    userMsg := &genai.Content{
        Parts: []*genai.Part{{Text: prompt}},
        Role:  string(genai.RoleUser),
    }

    // The r.Run method streams events and errors.
    // The loop iterates over the results, handling them as they arrive.
    for event, err := range r.Run(ctx, userID, sessionID, userMsg, agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
    }) {
        if err != nil {
            fmt.Printf("\nAGENT_ERROR: %v\n", err)
        } else if event.Partial {
            for _, p := range event.LLMResponse.Content.Parts {
                fmt.Print(p.Text)
            }
        }
    }
    return nil
}

func main() {
    agent, err := createSearchAgent(context.Background())
    if err != nil {
        log.Fatalf("Failed to create agent: %v", err)
    }
    fmt.Println("Agent created:", agent.Name())
    prompt := "what's the latest ai news?"
    fmt.Printf("\nPrompt: %s\nResponse: ", prompt)
    if err := callAgent(context.Background(), agent, prompt); err != nil {
        log.Fatalf("Error calling agent: %v", err)
    }
    fmt.Println("\n---")
}
```

```java
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.GoogleSearchTool;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Part;

public class GoogleSearchAgentApp {

  private static final String APP_NAME = "Google Search_agent";
  private static final String USER_ID = "user1234";
  private static final String SESSION_ID = "1234";

  /**
   * Calls the agent with the given query and prints the final response.
   *
   * @param runner The runner to use.
   * @param query The query to send to the agent.
   */
  public static void callAgent(Runner runner, String query) {
    Content content =
        Content.fromParts(Part.fromText(query));

    InMemorySessionService sessionService = (InMemorySessionService) runner.sessionService();
    Session session =
        sessionService
            .createSession(APP_NAME, USER_ID, /* state= */ null, SESSION_ID)
            .blockingGet();

    runner
        .runAsync(session.userId(), session.id(), content)
        .forEach(
            event -> {
              if (event.finalResponse()
                  && event.content().isPresent()
                  && event.content().get().parts().isPresent()
                  && !event.content().get().parts().get().isEmpty()
                  && event.content().get().parts().get().get(0).text().isPresent()) {
                String finalResponse = event.content().get().parts().get().get(0).text().get();
                System.out.println("Agent Response: " + finalResponse);
              }
            });
  }

  public static void main(String[] args) {
    // Google Search is a pre-built tool which allows the agent to perform Google searches.
    GoogleSearchTool googleSearchTool = new GoogleSearchTool();

    BaseAgent rootAgent =
        LlmAgent.builder()
            .name("basic_search_agent")
            .model("gemini-2.0-flash") // Ensure to use a Gemini 2.0 model for Google Search Tool
            .description("Agent to answer questions using Google Search.")
            .instruction(
                "I can answer your questions by searching the internet. Just ask me anything!")
            .tools(ImmutableList.of(googleSearchTool))
            .build();

    // Session and Runner
    InMemorySessionService sessionService = new InMemorySessionService();
    Runner runner = new Runner(rootAgent, APP_NAME, null, sessionService);

    // Agent Interaction
    callAgent(runner, "what's the latest ai news?");
  }
}
```
