# Function tools

Supported in ADKPython v0.1.0Typescript v0.2.0Go v0.1.0Java v0.1.0

When pre-built ADK tools don't meet your requirements, you can create custom *function tools*. Building function tools allows you to create tailored functionality, such as connecting to proprietary databases or implementing unique algorithms. For example, a function tool, `myfinancetool`, might be a function that calculates a specific financial metric. ADK also supports long-running functions, so if that calculation takes a while, the agent can continue working on other tasks.

ADK offers several ways to create functions tools, each suited to different levels of complexity and control:

- [Function Tools](#function-tool)
- [Long Running Function Tools](#long-run-tool)
- [Agents-as-a-Tool](#agent-tool)

## Function Tools

Transforming a Python function into a tool is a straightforward way to integrate custom logic into your agents. When you assign a function to an agent’s `tools` list, the framework automatically wraps it as a `FunctionTool`.

### How it Works

The ADK framework automatically inspects your Python function's signature—including its name, docstring, parameters, type hints, and default values—to generate a schema. This schema is what the LLM uses to understand the tool's purpose, when to use it, and what arguments it requires.

### Defining Function Signatures

A well-defined function signature is crucial for the LLM to use your tool correctly.

#### Parameters

##### Required Parameters

A parameter is considered **required** if it has a type hint but **no default value**. The LLM must provide a value for this argument when it calls the tool. The parameter's description is taken from the function's docstring.

Example: Required Parameters

```python
def get_weather(city: str, unit: str):
    """
    Retrieves the weather for a city in the specified unit.

    Args:
        city (str): The city name.
        unit (str): The temperature unit, either 'Celsius' or 'Fahrenheit'.
    """
    # ... function logic ...
    return {"status": "success", "report": f"Weather for {city} is sunny."}
```

In this example, both `city` and `unit` are mandatory. If the LLM tries to call `get_weather` without one of them, the ADK will return an error to the LLM, prompting it to correct the call.

In Go, you use struct tags to control the JSON schema. The two primary tags are `json` and `jsonschema`.

A parameter is considered **required** if its struct field does **not** have the `omitempty` or `omitzero` option in its `json` tag.

The `jsonschema` tag is used to provide the argument's description. This is crucial for the LLM to understand what the argument is for.

Example: Required Parameters

```go
// GetWeatherParams defines the arguments for the getWeather tool.
type GetWeatherParams struct {
    // This field is REQUIRED (no "omitempty").
    // The jsonschema tag provides the description.
    Location string `json:"location" jsonschema:"The city and state, e.g., San Francisco, CA"`

    // This field is also REQUIRED.
    Unit     string `json:"unit" jsonschema:"The temperature unit, either 'celsius' or 'fahrenheit'"`
}
```

In this example, both `location` and `unit` are mandatory.

##### Optional Parameters

A parameter is considered **optional** if you provide a **default value**. This is the standard Python way to define optional arguments. You can also mark a parameter as optional using `typing.Optional[SomeType]` or the `| None` syntax (Python 3.10+).

Example: Optional Parameters

```python
def search_flights(destination: str, departure_date: str, flexible_days: int = 0):
    """
    Searches for flights.

    Args:
        destination (str): The destination city.
        departure_date (str): The desired departure date.
        flexible_days (int, optional): Number of flexible days for the search. Defaults to 0.
    """
    # ... function logic ...
    if flexible_days > 0:
        return {"status": "success", "report": f"Found flexible flights to {destination}."}
    return {"status": "success", "report": f"Found flights to {destination} on {departure_date}."}
```

Here, `flexible_days` is optional. The LLM can choose to provide it, but it's not required.

A parameter is considered **optional** if its struct field has the `omitempty` or `omitzero` option in its `json` tag.

Example: Optional Parameters

```go
// GetWeatherParams defines the arguments for the getWeather tool.
type GetWeatherParams struct {
    // Location is required.
    Location string `json:"location" jsonschema:"The city and state, e.g., San Francisco, CA"`

    // Unit is optional.
    Unit string `json:"unit,omitempty" jsonschema:"The temperature unit, either 'celsius' or 'fahrenheit'"`

    // Days is optional.
    Days int `json:"days,omitzero" jsonschema:"The number of forecast days to return (defaults to 1)"`
}
```

Here, `unit` and `days` are optional. The LLM can choose to provide them, but they are not required.

##### Optional Parameters with `typing.Optional`

You can also mark a parameter as optional using `typing.Optional[SomeType]` or the `| None` syntax (Python 3.10+). This signals that the parameter can be `None`. When combined with a default value of `None`, it behaves as a standard optional parameter.

Example: `typing.Optional`

```python
from typing import Optional

def create_user_profile(username: str, bio: Optional[str] = None):
    """
    Creates a new user profile.

    Args:
        username (str): The user's unique username.
        bio (str, optional): A short biography for the user. Defaults to None.
    """
    # ... function logic ...
    if bio:
        return {"status": "success", "message": f"Profile for {username} created with a bio."}
    return {"status": "success", "message": f"Profile for {username} created."}
```

##### Variadic Parameters (`*args` and `**kwargs`)

While you can include `*args` (variable positional arguments) and `**kwargs` (variable keyword arguments) in your function signature for other purposes, they are **ignored by the ADK framework** when generating the tool schema for the LLM. The LLM will not be aware of them and cannot pass arguments to them. It's best to rely on explicitly defined parameters for all data you expect from the LLM.

#### Return Type

The preferred return type for a Function Tool is a **dictionary** in Python, a **Map** in Java, or an **object** in TypeScript. This allows you to structure the response with key-value pairs, providing context and clarity to the LLM. If your function returns a type other than a dictionary, the framework automatically wraps it into a dictionary with a single key named **"result"**.

Strive to make your return values as descriptive as possible. *For example,* instead of returning a numeric error code, return a dictionary with an "error_message" key containing a human-readable explanation. **Remember that the LLM**, not a piece of code, needs to understand the result. As a best practice, include a "status" key in your return dictionary to indicate the overall outcome (e.g., "success", "error", "pending"), providing the LLM with a clear signal about the operation's state.

#### Docstrings

The docstring of your function serves as the tool's **description** and is sent to the LLM. Therefore, a well-written and comprehensive docstring is crucial for the LLM to understand how to use the tool effectively. Clearly explain the purpose of the function, the meaning of its parameters, and the expected return values.

### Passing Data Between Tools

When an agent calls multiple tools in a sequence, you might need to pass data from one tool to another. The recommended way to do this is by using the `temp:` prefix in the session state.

A tool can write data to a `temp:` variable, and a subsequent tool can read it. This data is only available for the current invocation and is discarded afterwards.

Shared Invocation Context

All tool calls within a single agent turn share the same `InvocationContext`. This means they also share the same temporary (`temp:`) state, which is how data can be passed between them.

### Example

Example

This tool is a python function which obtains the Stock price of a given Stock ticker/ symbol.

Note: You need to `pip install yfinance` library before using this tool.

```python
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
from google.genai import types

import yfinance as yf


APP_NAME = "stock_app"
USER_ID = "1234"
SESSION_ID = "session1234"

def get_stock_price(symbol: str):
    """
    Retrieves the current stock price for a given symbol.

    Args:
        symbol (str): The stock symbol (e.g., "AAPL", "GOOG").

    Returns:
        float: The current stock price, or None if an error occurs.
    """
    try:
        stock = yf.Ticker(symbol)
        historical_data = stock.history(period="1d")
        if not historical_data.empty:
            current_price = historical_data['Close'].iloc[-1]
            return current_price
        else:
            return None
    except Exception as e:
        print(f"Error retrieving stock price for {symbol}: {e}")
        return None


stock_price_agent = Agent(
    model='gemini-2.0-flash',
    name='stock_agent',
    instruction= 'You are an agent who retrieves stock prices. If a ticker symbol is provided, fetch the current price. If only a company name is given, first perform a Google search to find the correct ticker symbol before retrieving the stock price. If the provided ticker symbol is invalid or data cannot be retrieved, inform the user that the stock price could not be found.',
    description='This agent specializes in retrieving real-time stock prices. Given a stock ticker symbol (e.g., AAPL, GOOG, MSFT) or the stock name, use the tools and reliable data sources to provide the most up-to-date price.',
    tools=[get_stock_price], # You can add Python functions directly to the tools list; they will be automatically wrapped as FunctionTools.
)


# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=stock_price_agent, app_name=APP_NAME, session_service=session_service)
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
await call_agent_async("stock price of GOOG")
```

The return value from this tool will be wrapped into a dictionary.

```json
{"result": "$123"}
```

This tool retrieves the mocked value of a stock price.

```typescript
/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import {Content, Part, createUserContent} from '@google/genai';
import {
  stringifyContent,
  FunctionTool,
  InMemoryRunner,
  LlmAgent,
} from '@google/adk';
import {z} from 'zod';

// Define the function to get the stock price
async function getStockPrice({ticker}: {ticker: string}): Promise<Record<string, unknown>> {
  console.log(`Getting stock price for ${ticker}`);
  // In a real-world scenario, you would fetch the stock price from an API
  const price = (Math.random() * 1000).toFixed(2);
  return {price: `$${price}`};
}

async function main() {
  // Define the schema for the tool's parameters using Zod
  const getStockPriceSchema = z.object({
    ticker: z.string().describe('The stock ticker symbol to look up.'),
  });

  // Create a FunctionTool from the function and schema
  const stockPriceTool = new FunctionTool({
    name: 'getStockPrice',
    description: 'Gets the current price of a stock.',
    parameters: getStockPriceSchema,
    execute: getStockPrice,
  });

  // Define the agent that will use the tool
  const stockAgent = new LlmAgent({
    name: 'stock_agent',
    model: 'gemini-2.5-flash',
    instruction: 'You can get the stock price of a company.',
    tools: [stockPriceTool],
  });

  // Create a runner for the agent
  const runner = new InMemoryRunner({agent: stockAgent});

  // Create a new session
  const session = await runner.sessionService.createSession({
    appName: runner.appName,
    userId: 'test-user',
  });

  const userContent: Content = createUserContent('What is the stock price of GOOG?');

  // Run the agent and get the response
  const response = [];
  for await (const event of runner.runAsync({
    userId: session.userId,
    sessionId: session.id,
    newMessage: userContent,
  })) {
    response.push(event);
  }

  // Print the final response from the agent
  const finalResponse = response[response.length - 1];
  if (finalResponse?.content?.parts?.length) {
    console.log(stringifyContent(finalResponse));
  }
}

main();
```

The return value from this tool will be an object.

```json
For input `GOOG`: {"price": 2800.0, "currency": "USD"}
```

This tool retrieves the mocked value of a stock price.

```go
import (
    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)

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
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/agenttool"
    "google.golang.org/adk/tool/functiontool"

    "google.golang.org/genai"
)

// mockStockPrices provides a simple in-memory database of stock prices
// to simulate a real-world stock data API. This allows the example to
// demonstrate tool functionality without making external network calls.
var mockStockPrices = map[string]float64{
    "GOOG": 300.6,
    "AAPL": 123.4,
    "MSFT": 234.5,
}

// getStockPriceArgs defines the schema for the arguments passed to the getStockPrice tool.
// Using a struct is the recommended approach in the Go ADK as it provides strong
// typing and clear validation for the expected inputs.
type getStockPriceArgs struct {
    Symbol string `json:"symbol" jsonschema:"The stock ticker symbol, e.g., GOOG"`
}

// getStockPriceResults defines the output schema for the getStockPrice tool.
type getStockPriceResults struct {
    Symbol string  `json:"symbol"`
    Price  float64 `json:"price,omitempty"`
    Error  string  `json:"error,omitempty"`
}

// getStockPrice is a tool that retrieves the stock price for a given ticker symbol
// from the mockStockPrices map. It demonstrates how a function can be used as a
// tool by an agent. If the symbol is found, it returns a struct containing the
// symbol and its price. Otherwise, it returns a struct with an error message.
func getStockPrice(ctx tool.Context, input getStockPriceArgs) (getStockPriceResults, error) {
    symbolUpper := strings.ToUpper(input.Symbol)
    if price, ok := mockStockPrices[symbolUpper]; ok {
        fmt.Printf("Tool: Found price for %s: %f\n", input.Symbol, price)
        return getStockPriceResults{Symbol: input.Symbol, Price: price}, nil
    }
    return getStockPriceResults{}, fmt.Errorf("no data found for symbol")
}

// createStockAgent initializes and configures an LlmAgent.
// This agent is equipped with the getStockPrice tool and is instructed
// on how to respond to user queries about stock prices. It uses the
// Gemini model to understand user intent and decide when to use its tools.
func createStockAgent(ctx context.Context) (agent.Agent, error) {
    stockPriceTool, err := functiontool.New(
        functiontool.Config{
            Name:        "get_stock_price",
            Description: "Retrieves the current stock price for a given symbol.",
        },
        getStockPrice)
    if err != nil {
        return nil, err
    }

    model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})

    if err != nil {
        log.Fatalf("Failed to create model: %v", err)
    }

    return llmagent.New(llmagent.Config{
        Name:        "stock_agent",
        Model:       model,
        Instruction: "You are an agent who retrieves stock prices. If a ticker symbol is provided, fetch the current price. If only a company name is given, first perform a Google search to find the correct ticker symbol before retrieving the stock price. If the provided ticker symbol is invalid or data cannot be retrieved, inform the user that the stock price could not be found.",
        Description: "This agent specializes in retrieving real-time stock prices. Given a stock ticker symbol (e.g., AAPL, GOOG, MSFT) or the stock name, use the tools and reliable data sources to provide the most up-to-date price.",
        Tools: []tool.Tool{
            stockPriceTool,
        },
    })
}

// userID and appName are constants used to identify the user and application
// throughout the session. These values are important for logging, tracking,
// and managing state across different agent interactions.
const (
    userID  = "example_user_id"
    appName = "example_app"
)

// callAgent orchestrates the execution of the agent for a given prompt.
// It sets up the necessary services, creates a session, and uses a runner
// to manage the agent's lifecycle. It streams the agent's responses and
// prints them to the console, handling any potential errors during the run.
func callAgent(ctx context.Context, a agent.Agent, prompt string) {
    sessionService := session.InMemoryService()
    // Create a new session for the agent interactions.
    session, err := sessionService.Create(ctx, &session.CreateRequest{
        AppName: appName,
        UserID:  userID,
    })
    if err != nil {
        log.Fatalf("Failed to create the session service: %v", err)
    }
    config := runner.Config{
        AppName:        appName,
        Agent:          a,
        SessionService: sessionService,
    }

    // Create the runner to manage the agent execution.
    r, err := runner.New(config)

    if err != nil {
        log.Fatalf("Failed to create the runner: %v", err)
    }

    sessionID := session.Session.ID()

    userMsg := &genai.Content{
        Parts: []*genai.Part{
            genai.NewPartFromText(prompt),
        },
        Role: string(genai.RoleUser),
    }

    for event, err := range r.Run(ctx, userID, sessionID, userMsg, agent.RunConfig{
        StreamingMode: agent.StreamingModeNone,
    }) {
        if err != nil {
            fmt.Printf("\nAGENT_ERROR: %v\n", err)
        } else {
            for _, p := range event.Content.Parts {
                fmt.Print(p.Text)
            }
        }
    }
}

// RunAgentSimulation serves as the entry point for this example.
// It creates the stock agent and then simulates a series of user interactions
// by sending different prompts to the agent. This function showcases how the
// agent responds to various queries, including both successful and unsuccessful
// attempts to retrieve stock prices.
func RunAgentSimulation() {
    // Create the stock agent
    agent, err := createStockAgent(context.Background())
    if err != nil {
        panic(err)
    }

    fmt.Println("Agent created:", agent.Name())

    prompts := []string{
        "stock price of GOOG",
        "What's the price of MSFT?",
        "Can you find the stock price for an unknown company XYZ?",
    }

    // Simulate running the agent with different prompts
    for _, prompt := range prompts {
        fmt.Printf("\nPrompt: %s\nResponse: ", prompt)
        callAgent(context.Background(), agent, prompt)
        fmt.Println("\n---")
    }
}

// createSummarizerAgent creates an agent whose sole purpose is to summarize text.
func createSummarizerAgent(ctx context.Context) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
    if err != nil {
        return nil, err
    }
    return llmagent.New(llmagent.Config{
        Name:        "SummarizerAgent",
        Model:       model,
        Instruction: "You are an expert at summarizing text. Take the user's input and provide a concise summary.",
        Description: "An agent that summarizes text.",
    })
}

// createMainAgent creates the primary agent that will use the summarizer agent as a tool.
func createMainAgent(ctx context.Context, tools ...tool.Tool) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
    if err != nil {
        return nil, err
    }
    return llmagent.New(llmagent.Config{
        Name:  "MainAgent",
        Model: model,
        Instruction: "You are a helpful assistant. If you are asked to summarize a long text, use the 'summarize' tool. " +
            "After getting the summary, present it to the user by saying 'Here is a summary of the text:'.",
        Description: "The main agent that can delegate tasks.",
        Tools:       tools,
    })
}

func RunAgentAsToolSimulation() {
    ctx := context.Background()

    // 1. Create the Tool Agent (Summarizer)
    summarizerAgent, err := createSummarizerAgent(ctx)
    if err != nil {
        log.Fatalf("Failed to create summarizer agent: %v", err)
    }

    // 2. Wrap the Tool Agent in an AgentTool
    summarizeTool := agenttool.New(summarizerAgent, &agenttool.Config{
        SkipSummarization: true,
    })

    // 3. Create the Main Agent and provide it with the AgentTool
    mainAgent, err := createMainAgent(ctx, summarizeTool)
    if err != nil {
        log.Fatalf("Failed to create main agent: %v", err)
    }

    // 4. Run the main agent
    prompt := `
        Please summarize this text for me:
        Quantum computing represents a fundamentally different approach to computation,
        leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers
        that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively
        being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled,
        meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and
        interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such
        as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far
        faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages.
    `
    fmt.Printf("\nPrompt: %s\nResponse: ", prompt)
    callAgent(context.Background(), mainAgent, prompt)
    fmt.Println("\n---")
}


func main() {
    fmt.Println("Attempting to run the agent simulation...")
    RunAgentSimulation()
    fmt.Println("\nAttempting to run the agent-as-a-tool simulation...")
    RunAgentAsToolSimulation()
}
```

The return value from this tool will be a `getStockPriceResults` instance.

```json
For input `{"symbol": "GOOG"}`: {"price":300.6,"symbol":"GOOG"}
```

This tool retrieves the mocked value of a stock price.

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.HashMap;
import java.util.Map;

public class StockPriceAgent {

  private static final String APP_NAME = "stock_agent";
  private static final String USER_ID = "user1234";

  // Mock data for various stocks functionality
  // NOTE: This is a MOCK implementation. In a real Java application,
  // you would use a financial data API or library.
  private static final Map<String, Double> mockStockPrices = new HashMap<>();

  static {
    mockStockPrices.put("GOOG", 1.0);
    mockStockPrices.put("AAPL", 1.0);
    mockStockPrices.put("MSFT", 1.0);
  }

  @Schema(description = "Retrieves the current stock price for a given symbol.")
  public static Map<String, Object> getStockPrice(
      @Schema(description = "The stock symbol (e.g., \"AAPL\", \"GOOG\")",
        name = "symbol")
      String symbol) {

    try {
      if (mockStockPrices.containsKey(symbol.toUpperCase())) {
        double currentPrice = mockStockPrices.get(symbol.toUpperCase());
        System.out.println("Tool: Found price for " + symbol + ": " + currentPrice);
        return Map.of("symbol", symbol, "price", currentPrice);
      } else {
        return Map.of("symbol", symbol, "error", "No data found for symbol");
      }
    } catch (Exception e) {
      return Map.of("symbol", symbol, "error", e.getMessage());
    }
  }

  public static void callAgent(String prompt) {
    // Create the FunctionTool from the Java method
    FunctionTool getStockPriceTool = FunctionTool.create(StockPriceAgent.class, "getStockPrice");

    LlmAgent stockPriceAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("stock_agent")
            .instruction(
                "You are an agent who retrieves stock prices. If a ticker symbol is provided, fetch the current price. If only a company name is given, first perform a Google search to find the correct ticker symbol before retrieving the stock price. If the provided ticker symbol is invalid or data cannot be retrieved, inform the user that the stock price could not be found.")
            .description(
                "This agent specializes in retrieving real-time stock prices. Given a stock ticker symbol (e.g., AAPL, GOOG, MSFT) or the stock name, use the tools and reliable data sources to provide the most up-to-date price.")
            .tools(getStockPriceTool) // Add the Java FunctionTool
            .build();

    // Create an InMemoryRunner
    InMemoryRunner runner = new InMemoryRunner(stockPriceAgent, APP_NAME);
    // InMemoryRunner automatically creates a session service. Create a session using the service
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();
    Content userMessage = Content.fromParts(Part.fromText(prompt));

    // Run the agent
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    // Stream event response
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }

  public static void main(String[] args) {
    callAgent("stock price of GOOG");
    callAgent("What's the price of MSFT?");
    callAgent("Can you find the stock price for an unknown company XYZ?");
  }
}
```

The return value from this tool will be wrapped into a Map.

```json
For input `GOOG`: {"symbol": "GOOG", "price": "1.0"}
```

### Best Practices

While you have considerable flexibility in defining your function, remember that simplicity enhances usability for the LLM. Consider these guidelines:

- **Fewer Parameters are Better:** Minimize the number of parameters to reduce complexity.
- **Simple Data Types:** Favor primitive data types like `str` and `int` over custom classes whenever possible.
- **Meaningful Names:** The function's name and parameter names significantly influence how the LLM interprets and utilizes the tool. Choose names that clearly reflect the function's purpose and the meaning of its inputs. Avoid generic names like `do_stuff()` or `beAgent()`.
- **Build for Parallel Execution:** Improve function calling performance when multiple tools are run by building for asynchronous operation. For information on enabling parallel execution for tools, see [Increase tool performance with parallel execution](/adk-docs/tools-custom/performance/).

## Long Running Function Tools

This tool is designed to help you start and manage tasks that are handled outside the operation of your agent workflow, and require a significant amount of processing time, without blocking the agent's execution. This tool is a subclass of `FunctionTool`.

When using a `LongRunningFunctionTool`, your function can initiate the long-running operation and optionally return an **initial result**, such as a long-running operation id. Once a long running function tool is invoked the agent runner pauses the agent run and lets the agent client to decide whether to continue or wait until the long-running operation finishes. The agent client can query the progress of the long-running operation and send back an intermediate or final response. The agent can then continue with other tasks. An example is the human-in-the-loop scenario where the agent needs human approval before proceeding with a task.

Warning: Execution handling

Long Running Function Tools are designed to help you start and *manage* long running tasks as part of your agent workflow, but ***not perform*** the actual, long task. For tasks that require significant time to complete, you should implement a separate server to do the task.

Tip: Parallel execution

Depending on the type of tool you are building, designing for asynchronous operation may be a better solution than creating a long running tool. For more information, see [Increase tool performance with parallel execution](/adk-docs/tools-custom/performance/).

### How it Works

In Python, you wrap a function with `LongRunningFunctionTool`. In Java, you pass a Method name to `LongRunningFunctionTool.create()`. In TypeScript, you instantiate the `LongRunningFunctionTool` class.

1. **Initiation:** When the LLM calls the tool, your function starts the long-running operation.
1. **Initial Updates:** Your function should optionally return an initial result (e.g. the long-running operation id). The ADK framework takes the result and sends it back to the LLM packaged within a `FunctionResponse`. This allows the LLM to inform the user (e.g., status, percentage complete, messages). And then the agent run is ended / paused.
1. **Continue or Wait:** After each agent run is completed. Agent client can query the progress of the long-running operation and decide whether to continue the agent run with an intermediate response (to update the progress) or wait until a final response is retrieved. Agent client should send the intermediate or final response back to the agent for the next run.
1. **Framework Handling:** The ADK framework manages the execution. It sends the intermediate or final `FunctionResponse` sent by agent client to the LLM to generate a user friendly message.

### Creating the Tool

Define your tool function and wrap it using the `LongRunningFunctionTool` class:

```python
# 1. Define the long running function
def ask_for_approval(
    purpose: str, amount: float
) -> dict[str, Any]:
    """Ask for approval for the reimbursement."""
    # create a ticket for the approval
    # Send a notification to the approver with the link of the ticket
    return {'status': 'pending', 'approver': 'Sean Zhou', 'purpose' : purpose, 'amount': amount, 'ticket-id': 'approval-ticket-1'}

def reimburse(purpose: str, amount: float) -> str:
    """Reimburse the amount of money to the employee."""
    # send the reimbrusement request to payment vendor
    return {'status': 'ok'}

# 2. Wrap the function with LongRunningFunctionTool
long_running_tool = LongRunningFunctionTool(func=ask_for_approval)
```

```typescript
// 1. Define the long-running function
function askForApproval(args: {purpose: string; amount: number}) {
  /**
   * Ask for approval for the reimbursement.
   */
  // create a ticket for the approval
  // Send a notification to the approver with the link of the ticket
  return {
    "status": "pending",
    "approver": "Sean Zhou",
    "purpose": args.purpose,
    "amount": args.amount,
    "ticket-id": "approval-ticket-1",
  };
}

// 2. Instantiate the LongRunningFunctionTool class with the long-running function
const longRunningTool = new LongRunningFunctionTool({
  name: "ask_for_approval",
  description: "Ask for approval for the reimbursement.",
  parameters: z.object({
    purpose: z.string().describe("The purpose of the reimbursement."),
    amount: z.number().describe("The amount to reimburse."),
  }),
  execute: askForApproval,
});
```

```go
import (
    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)

// CreateTicketArgs defines the arguments for our long-running tool.
type CreateTicketArgs struct {
    Urgency string `json:"urgency" jsonschema:"The urgency level of the ticket."`
}

// CreateTicketResults defines the *initial* output of our long-running tool.
type CreateTicketResults struct {
    Status   string `json:"status"`
    TicketId string `json:"ticket_id"`
}

// createTicketAsync simulates the *initiation* of a long-running ticket creation task.
func createTicketAsync(ctx tool.Context, args CreateTicketArgs) (CreateTicketResults, error) {
    log.Printf("TOOL_EXEC: 'create_ticket_long_running' called with urgency: %s (Call ID: %s)\n", args.Urgency, ctx.FunctionCallID())

    // "Generate" a ticket ID and return it in the initial response.
    ticketID := "TICKET-ABC-123"
    log.Printf("ACTION: Generated Ticket ID: %s for Call ID: %s\n", ticketID, ctx.FunctionCallID())

    // In a real application, you would save the association between the
    // FunctionCallID and the ticketID to handle the async response later.
    return CreateTicketResults{
        Status:   "started",
        TicketId: ticketID,
    }, nil
}

func createTicketAgent(ctx context.Context) (agent.Agent, error) {
    ticketTool, err := functiontool.New(
        functiontool.Config{
            Name:        "create_ticket_long_running",
            Description: "Creates a new support ticket with a specified urgency level.",
        },
        createTicketAsync,
    )
    if err != nil {
        return nil, fmt.Errorf("failed to create long running tool: %w", err)
    }

    model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
    if err != nil {
        return nil, fmt.Errorf("failed to create model: %v", err)
    }

    return llmagent.New(llmagent.Config{
        Name:        "ticket_agent",
        Model:       model,
        Instruction: "You are a helpful assistant for creating support tickets. Provide the status of the ticket at each interaction.",
        Tools:       []tool.Tool{ticketTool},
    })
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.LongRunningFunctionTool;
import java.util.HashMap;
import java.util.Map;

public class ExampleLongRunningFunction {

  // Define your Long Running function.
  // Ask for approval for the reimbursement.
  public static Map<String, Object> askForApproval(String purpose, double amount) {
    // Simulate creating a ticket and sending a notification
    System.out.println(
        "Simulating ticket creation for purpose: " + purpose + ", amount: " + amount);

    // Send a notification to the approver with the link of the ticket
    Map<String, Object> result = new HashMap<>();
    result.put("status", "pending");
    result.put("approver", "Sean Zhou");
    result.put("purpose", purpose);
    result.put("amount", amount);
    result.put("ticket-id", "approval-ticket-1");
    return result;
  }

  public static void main(String[] args) throws NoSuchMethodException {
    // Pass the method to LongRunningFunctionTool.create
    LongRunningFunctionTool approveTool =
        LongRunningFunctionTool.create(ExampleLongRunningFunction.class, "askForApproval");

    // Include the tool in the agent
    LlmAgent approverAgent =
        LlmAgent.builder()
            // ...
            .tools(approveTool)
            .build();
  }
}
```

### Intermediate / Final result Updates

Agent client received an event with long running function calls and check the status of the ticket. Then Agent client can send the intermediate or final response back to update the progress. The framework packages this value (even if it's None) into the content of the `FunctionResponse` sent back to the LLM.

Note: Long running function response with Resume feature

If your ADK agent workflow is configured with the [Resume](/adk-docs/runtime/resume/) feature, you also must include the Invocation ID (`invocation_id`) parameter with the long running function response. The Invocation ID you provide must be the same invocation that generated the long running function request, otherwise the system starts a new invocation with the response. If your agent uses the Resume feature, consider including the Invocation ID as a parameter with your long running function request, so it can be included with the response. For more details on using the Resume feature, see [Resume stopped agents](/adk-docs/runtime/resume/).

Applies to only Java ADK

When passing `ToolContext` with Function Tools, ensure that one of the following is true:

- The Schema is passed with the ToolContext parameter in the function signature, like:

  ```text
  @com.google.adk.tools.Annotations.Schema(name = "toolContext") ToolContext toolContext
  ```

  OR

- The following `-parameters` flag is set to the mvn compiler plugin

```text
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.14.0</version> <!-- or newer -->
            <configuration>
                <compilerArgs>
                    <arg>-parameters</arg>
                </compilerArgs>
            </configuration>
        </plugin>
    </plugins>
</build>
```

This constraint is temporary and will be removed.

```python
# Agent Interaction
async def call_agent_async(query):

    def get_long_running_function_call(event: Event) -> types.FunctionCall:
        # Get the long running function call from the event
        if not event.long_running_tool_ids or not event.content or not event.content.parts:
            return
        for part in event.content.parts:
            if (
                part
                and part.function_call
                and event.long_running_tool_ids
                and part.function_call.id in event.long_running_tool_ids
            ):
                return part.function_call

    def get_function_response(event: Event, function_call_id: str) -> types.FunctionResponse:
        # Get the function response for the fuction call with specified id.
        if not event.content or not event.content.parts:
            return
        for part in event.content.parts:
            if (
                part
                and part.function_response
                and part.function_response.id == function_call_id
            ):
                return part.function_response

    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()

    print("\nRunning agent...")
    events_async = runner.run_async(
        session_id=session.id, user_id=USER_ID, new_message=content
    )


    long_running_function_call, long_running_function_response, ticket_id = None, None, None
    async for event in events_async:
        # Use helper to check for the specific auth request event
        if not long_running_function_call:
            long_running_function_call = get_long_running_function_call(event)
        else:
            _potential_response = get_function_response(event, long_running_function_call.id)
            if _potential_response: # Only update if we get a non-None response
                long_running_function_response = _potential_response
                ticket_id = long_running_function_response.response['ticket-id']
        if event.content and event.content.parts:
            if text := ''.join(part.text or '' for part in event.content.parts):
                print(f'[{event.author}]: {text}')


    if long_running_function_response:
        # query the status of the correpsonding ticket via tciket_id
        # send back an intermediate / final response
        updated_response = long_running_function_response.model_copy(deep=True)
        updated_response.response = {'status': 'approved'}
        async for event in runner.run_async(
          session_id=session.id, user_id=USER_ID, new_message=types.Content(parts=[types.Part(function_response = updated_response)], role='user')
        ):
            if event.content and event.content.parts:
                if text := ''.join(part.text or '' for part in event.content.parts):
                    print(f'[{event.author}]: {text}')
```

```typescript
/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {
  LlmAgent,
  Runner,
  FunctionTool,
  LongRunningFunctionTool,
  InMemorySessionService,
  Event,
  stringifyContent,
} from "@google/adk";
import {z} from "zod";
import {Content, FunctionCall, FunctionResponse, createUserContent} from "@google/genai";

// 1. Define the long-running function
function askForApproval(args: {purpose: string; amount: number}) {
  /**
   * Ask for approval for the reimbursement.
   */
  // create a ticket for the approval
  // Send a notification to the approver with the link of the ticket
  return {
    "status": "pending",
    "approver": "Sean Zhou",
    "purpose": args.purpose,
    "amount": args.amount,
    "ticket-id": "approval-ticket-1",
  };
}

// 2. Instantiate the LongRunningFunctionTool class with the long-running function
const longRunningTool = new LongRunningFunctionTool({
  name: "ask_for_approval",
  description: "Ask for approval for the reimbursement.",
  parameters: z.object({
    purpose: z.string().describe("The purpose of the reimbursement."),
    amount: z.number().describe("The amount to reimburse."),
  }),
  execute: askForApproval,
});

function reimburse(args: {purpose: string; amount: number}) {
  /**
   * Reimburse the amount of money to the employee.
   */
  // send the reimbursement request to payment vendor
  return {status: "ok"};
}

const reimburseTool = new FunctionTool({
  name: "reimburse",
  description: "Reimburse the amount of money to the employee.",
  parameters: z.object({
    purpose: z.string().describe("The purpose of the reimbursement."),
    amount: z.number().describe("The amount to reimburse."),
  }),
  execute: reimburse,
});

// 3. Use the tool in an Agent
const reimbursementAgent = new LlmAgent({
  model: "gemini-2.5-flash",
  name: "reimbursement_agent",
  instruction: `
      You are an agent whose job is to handle the reimbursement process for
      the employees. If the amount is less than $100, you will automatically
      approve the reimbursement.

      If the amount is greater than $100, you will
      ask for approval from the manager. If the manager approves, you will
      call reimburse() to reimburse the amount to the employee. If the manager
      rejects, you will inform the employee of the rejection.
    `,
  tools: [reimburseTool, longRunningTool],
});

const APP_NAME = "human_in_the_loop";
const USER_ID = "1234";
const SESSION_ID = "session1234";

// Session and Runner
async function setupSessionAndRunner() {
  const sessionService = new InMemorySessionService();
  const session = await sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID,
  });
  const runner = new Runner({
    agent: reimbursementAgent,
    appName: APP_NAME,
    sessionService: sessionService,
  });
  return {session, runner};
}

function getLongRunningFunctionCall(event: Event): FunctionCall | undefined {
  // Get the long-running function call from the event
  if (
    !event.longRunningToolIds ||
    !event.content ||
    !event.content.parts?.length
  ) {
    return;
  }
  for (const part of event.content.parts) {
    if (
      part &&
      part.functionCall &&
      event.longRunningToolIds &&
      part.functionCall.id &&
      event.longRunningToolIds.includes(part.functionCall.id)
    ) {
      return part.functionCall;
    }
  }
}

function getFunctionResponse(
  event: Event,
  functionCallId: string
): FunctionResponse | undefined {
  // Get the function response for the function call with specified id.
  if (!event.content || !event.content.parts?.length) {
    return;
  }
  for (const part of event.content.parts) {
    if (
      part &&
      part.functionResponse &&
      part.functionResponse.id === functionCallId
    ) {
      return part.functionResponse;
    }
  }
}

// Agent Interaction
async function callAgentAsync(query: string) {
  let longRunningFunctionCall: FunctionCall | undefined;
  let longRunningFunctionResponse: FunctionResponse | undefined;
  let ticketId: string | undefined;
  const content: Content = createUserContent(query);
  const {session, runner} = await setupSessionAndRunner();

  console.log("\nRunning agent...");
  const events = runner.runAsync({
    sessionId: session.id,
    userId: USER_ID,
    newMessage: content,
  });

  for await (const event of events) {
    // Use helper to check for the specific auth request event
    if (!longRunningFunctionCall) {
      longRunningFunctionCall = getLongRunningFunctionCall(event);
    } else {
      const _potentialResponse = getFunctionResponse(
        event,
        longRunningFunctionCall.id!
      );
      if (_potentialResponse) {
        // Only update if we get a non-None response
        longRunningFunctionResponse = _potentialResponse;
        ticketId = (
          longRunningFunctionResponse.response as {[key: string]: any}
        )[`ticket-id`];
      }
    }
    const text = stringifyContent(event);
    if (text) {
      console.log(`[${event.author}]: ${text}`);
    }
  }

  if (longRunningFunctionResponse) {
    // query the status of the corresponding ticket via ticket_id
    // send back an intermediate / final response
    const updatedResponse = JSON.parse(
      JSON.stringify(longRunningFunctionResponse)
    );
    updatedResponse.response = {status: "approved"};
    for await (const event of runner.runAsync({
      sessionId: session.id,
      userId: USER_ID,
      newMessage: createUserContent(JSON.stringify({functionResponse: updatedResponse})),
    })) {
      const text = stringifyContent(event);
      if (text) {
        console.log(`[${event.author}]: ${text}`);
      }
    }
  }
}

async function main() {
  // reimbursement that doesn't require approval
  await callAgentAsync("Please reimburse 50$ for meals");
  // reimbursement that requires approval
  await callAgentAsync("Please reimburse 200$ for meals");
}

main();
```

The following example demonstrates a multi-turn workflow. First, the user asks the agent to create a ticket. The agent calls the long-running tool and the client captures the `FunctionCall` ID. The client then simulates the asynchronous work completing by sending subsequent `FunctionResponse` messages back to the agent to provide the ticket ID and final status.

```go
// runTurn executes a single turn with the agent and returns the captured function call ID.
func runTurn(ctx context.Context, r *runner.Runner, sessionID, turnLabel string, content *genai.Content) string {
    var funcCallID atomic.Value // Safely store the found ID.

    fmt.Printf("\n--- %s ---\n", turnLabel)
    for event, err := range r.Run(ctx, userID, sessionID, content, agent.RunConfig{
        StreamingMode: agent.StreamingModeNone,
    }) {
        if err != nil {
            fmt.Printf("\nAGENT_ERROR: %v\n", err)
            continue
        }
        // Print a summary of the event for clarity.
        printEventSummary(event, turnLabel)

        // Capture the function call ID from the event.
        for _, part := range event.Content.Parts {
            if fc := part.FunctionCall; fc != nil {
                if fc.Name == "create_ticket_long_running" {
                    funcCallID.Store(fc.ID)
                }
            }
        }
    }

    if id, ok := funcCallID.Load().(string); ok {
        return id
    }
    return ""
}

func main() {
    ctx := context.Background()
    ticketAgent, err := createTicketAgent(ctx)
    if err != nil {
        log.Fatalf("Failed to create agent: %v", err)
    }

    // Setup the runner and session.
    sessionService := session.InMemoryService()
    session, err := sessionService.Create(ctx, &session.CreateRequest{AppName: appName, UserID: userID})
    if err != nil {
        log.Fatalf("Failed to create session: %v", err)
    }
    r, err := runner.New(runner.Config{AppName: appName, Agent: ticketAgent, SessionService: sessionService})
    if err != nil {
        log.Fatalf("Failed to create runner: %v", err)
    }

    // --- Turn 1: User requests to create a ticket. ---
    initialUserMessage := genai.NewContentFromText("Create a high urgency ticket for me.", genai.RoleUser)
    funcCallID := runTurn(ctx, r, session.Session.ID(), "Turn 1: User Request", initialUserMessage)
    if funcCallID == "" {
        log.Fatal("ERROR: Tool 'create_ticket_long_running' not called in Turn 1.")
    }
    fmt.Printf("ACTION: Captured FunctionCall ID: %s\n", funcCallID)

    // --- Turn 2: App provides the final status of the ticket. ---
    // In a real application, the ticketID would be retrieved from a database
    // using the funcCallID. For this example, we'll use the same ID.
    ticketID := "TICKET-ABC-123"
    willContinue := false // Signal that this is the final response.
    ticketStatusResponse := &genai.FunctionResponse{
        Name: "create_ticket_long_running",
        ID:   funcCallID,
        Response: map[string]any{
            "status":    "approved",
            "ticket_id": ticketID,
        },
        WillContinue: &willContinue,
    }
    appResponseWithStatus := &genai.Content{
        Role:  string(genai.RoleUser),
        Parts: []*genai.Part{{FunctionResponse: ticketStatusResponse}},
    }
    runTurn(ctx, r, session.Session.ID(), "Turn 2: App provides ticket status", appResponseWithStatus)
    fmt.Println("Long running function completed successfully.")
}

// printEventSummary provides a readable log of agent and LLM interactions.
func printEventSummary(event *session.Event, turnLabel string) {
    for _, part := range event.Content.Parts {
        // Check for a text part.
        if part.Text != "" {
            fmt.Printf("[%s][%s_TEXT]: %s\n", turnLabel, event.Author, part.Text)
        }
        // Check for a function call part.
        if fc := part.FunctionCall; fc != nil {
            fmt.Printf("[%s][%s_CALL]: %s(%v) ID: %s\n", turnLabel, event.Author, fc.Name, fc.Args, fc.ID)
        }
    }
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.LongRunningFunctionTool;
import com.google.adk.tools.ToolContext;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.genai.types.Content;
import com.google.genai.types.FunctionCall;
import com.google.genai.types.FunctionResponse;
import com.google.genai.types.Part;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;

public class LongRunningFunctionExample {

  private static String USER_ID = "user123";

  @Schema(
      name = "create_ticket_long_running",
      description = """
          Creates a new support ticket with a specified urgency level.
          Examples of urgency are 'high', 'medium', or 'low'.
          The ticket creation is a long-running process, and its ID will be provided when ready.
      """)
  public static void createTicketAsync(
      @Schema(
              name = "urgency",
              description =
                  "The urgency level for the new ticket, such as 'high', 'medium', or 'low'.")
          String urgency,
      @Schema(name = "toolContext") // Ensures ADK injection
          ToolContext toolContext) {
    System.out.printf(
        "TOOL_EXEC: 'create_ticket_long_running' called with urgency: %s (Call ID: %s)%n",
        urgency, toolContext.functionCallId().orElse("N/A"));
  }

  public static void main(String[] args) {
    LlmAgent agent =
        LlmAgent.builder()
            .name("ticket_agent")
            .description("Agent for creating tickets via a long-running task.")
            .model("gemini-2.0-flash")
            .tools(
                ImmutableList.of(
                    LongRunningFunctionTool.create(
                        LongRunningFunctionExample.class, "createTicketAsync")))
            .build();

    Runner runner = new InMemoryRunner(agent);
    Session session =
        runner.sessionService().createSession(agent.name(), USER_ID, null, null).blockingGet();

    // --- Turn 1: User requests ticket ---
    System.out.println("\n--- Turn 1: User Request ---");
    Content initialUserMessage =
        Content.fromParts(Part.fromText("Create a high urgency ticket for me."));

    AtomicReference<String> funcCallIdRef = new AtomicReference<>();
    runner
        .runAsync(USER_ID, session.id(), initialUserMessage)
        .blockingForEach(
            event -> {
              printEventSummary(event, "T1");
              if (funcCallIdRef.get() == null) { // Capture the first relevant function call ID
                event.content().flatMap(Content::parts).orElse(ImmutableList.of()).stream()
                    .map(Part::functionCall)
                    .flatMap(Optional::stream)
                    .filter(fc -> "create_ticket_long_running".equals(fc.name().orElse("")))
                    .findFirst()
                    .flatMap(FunctionCall::id)
                    .ifPresent(funcCallIdRef::set);
              }
            });

    if (funcCallIdRef.get() == null) {
      System.out.println("ERROR: Tool 'create_ticket_long_running' not called in Turn 1.");
      return;
    }
    System.out.println("ACTION: Captured FunctionCall ID: " + funcCallIdRef.get());

    // --- Turn 2: App provides initial ticket_id (simulating async tool completion) ---
    System.out.println("\n--- Turn 2: App provides ticket_id ---");
    String ticketId = "TICKET-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    FunctionResponse ticketCreatedFuncResponse =
        FunctionResponse.builder()
            .name("create_ticket_long_running")
            .id(funcCallIdRef.get())
            .response(ImmutableMap.of("ticket_id", ticketId))
            .build();
    Content appResponseWithTicketId =
        Content.builder()
            .parts(
                ImmutableList.of(
                    Part.builder().functionResponse(ticketCreatedFuncResponse).build()))
            .role("user")
            .build();

    runner
        .runAsync(USER_ID, session.id(), appResponseWithTicketId)
        .blockingForEach(event -> printEventSummary(event, "T2"));
    System.out.println("ACTION: Sent ticket_id " + ticketId + " to agent.");

    // --- Turn 3: App provides ticket status update ---
    System.out.println("\n--- Turn 3: App provides ticket status ---");
    FunctionResponse ticketStatusFuncResponse =
        FunctionResponse.builder()
            .name("create_ticket_long_running")
            .id(funcCallIdRef.get())
            .response(ImmutableMap.of("status", "approved", "ticket_id", ticketId))
            .build();
    Content appResponseWithStatus =
        Content.builder()
            .parts(
                ImmutableList.of(Part.builder().functionResponse(ticketStatusFuncResponse).build()))
            .role("user")
            .build();

    runner
        .runAsync(USER_ID, session.id(), appResponseWithStatus)
        .blockingForEach(event -> printEventSummary(event, "T3_FINAL"));
    System.out.println("Long running function completed successfully.");
  }

  private static void printEventSummary(Event event, String turnLabel) {
    event
        .content()
        .ifPresent(
            content -> {
              String text =
                  content.parts().orElse(ImmutableList.of()).stream()
                      .map(part -> part.text().orElse(""))
                      .filter(s -> !s.isEmpty())
                      .collect(Collectors.joining(" "));
              if (!text.isEmpty()) {
                System.out.printf("[%s][%s_TEXT]: %s%n", turnLabel, event.author(), text);
              }
              content.parts().orElse(ImmutableList.of()).stream()
                  .map(Part::functionCall)
                  .flatMap(Optional::stream)
                  .findFirst() // Assuming one function call per relevant event for simplicity
                  .ifPresent(
                      fc ->
                          System.out.printf(
                              "[%s][%s_CALL]: %s(%s) ID: %s%n",
                              turnLabel,
                              event.author(),
                              fc.name().orElse("N/A"),
                              fc.args().orElse(ImmutableMap.of()),
                              fc.id().orElse("N/A")));
            });
  }
}
```

Python complete example: File Processing Simulation

```python
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

import asyncio
from typing import Any
from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.tools import LongRunningFunctionTool
from google.adk.sessions import InMemorySessionService
from google.genai import types


# 1. Define the long running function
def ask_for_approval(
    purpose: str, amount: float
) -> dict[str, Any]:
    """Ask for approval for the reimbursement."""
    # create a ticket for the approval
    # Send a notification to the approver with the link of the ticket
    return {'status': 'pending', 'approver': 'Sean Zhou', 'purpose' : purpose, 'amount': amount, 'ticket-id': 'approval-ticket-1'}

def reimburse(purpose: str, amount: float) -> str:
    """Reimburse the amount of money to the employee."""
    # send the reimbrusement request to payment vendor
    return {'status': 'ok'}

# 2. Wrap the function with LongRunningFunctionTool
long_running_tool = LongRunningFunctionTool(func=ask_for_approval)


# 3. Use the tool in an Agent
file_processor_agent = Agent(
    # Use a model compatible with function calling
    model="gemini-2.0-flash",
    name='reimbursement_agent',
    instruction="""
      You are an agent whose job is to handle the reimbursement process for
      the employees. If the amount is less than $100, you will automatically
      approve the reimbursement.

      If the amount is greater than $100, you will
      ask for approval from the manager. If the manager approves, you will
      call reimburse() to reimburse the amount to the employee. If the manager
      rejects, you will inform the employee of the rejection.
    """,
    tools=[reimburse, long_running_tool]
)


APP_NAME = "human_in_the_loop"
USER_ID = "1234"
SESSION_ID = "session1234"

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=file_processor_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# Agent Interaction
async def call_agent_async(query):

    def get_long_running_function_call(event: Event) -> types.FunctionCall:
        # Get the long running function call from the event
        if not event.long_running_tool_ids or not event.content or not event.content.parts:
            return
        for part in event.content.parts:
            if (
                part
                and part.function_call
                and event.long_running_tool_ids
                and part.function_call.id in event.long_running_tool_ids
            ):
                return part.function_call

    def get_function_response(event: Event, function_call_id: str) -> types.FunctionResponse:
        # Get the function response for the fuction call with specified id.
        if not event.content or not event.content.parts:
            return
        for part in event.content.parts:
            if (
                part
                and part.function_response
                and part.function_response.id == function_call_id
            ):
                return part.function_response

    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()

    print("\nRunning agent...")
    events_async = runner.run_async(
        session_id=session.id, user_id=USER_ID, new_message=content
    )


    long_running_function_call, long_running_function_response, ticket_id = None, None, None
    async for event in events_async:
        # Use helper to check for the specific auth request event
        if not long_running_function_call:
            long_running_function_call = get_long_running_function_call(event)
        else:
            _potential_response = get_function_response(event, long_running_function_call.id)
            if _potential_response: # Only update if we get a non-None response
                long_running_function_response = _potential_response
                ticket_id = long_running_function_response.response['ticket-id']
        if event.content and event.content.parts:
            if text := ''.join(part.text or '' for part in event.content.parts):
                print(f'[{event.author}]: {text}')


    if long_running_function_response:
        # query the status of the correpsonding ticket via tciket_id
        # send back an intermediate / final response
        updated_response = long_running_function_response.model_copy(deep=True)
        updated_response.response = {'status': 'approved'}
        async for event in runner.run_async(
          session_id=session.id, user_id=USER_ID, new_message=types.Content(parts=[types.Part(function_response = updated_response)], role='user')
        ):
            if event.content and event.content.parts:
                if text := ''.join(part.text or '' for part in event.content.parts):
                    print(f'[{event.author}]: {text}')


# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.

# reimbursement that doesn't require approval
# asyncio.run(call_agent_async("Please reimburse 50$ for meals"))
await call_agent_async("Please reimburse 50$ for meals") # For Notebooks, uncomment this line and comment the above line
# reimbursement that requires approval
# asyncio.run(call_agent_async("Please reimburse 200$ for meals"))
await call_agent_async("Please reimburse 200$ for meals") # For Notebooks, uncomment this line and comment the above line
```

#### Key aspects of this example

- **`LongRunningFunctionTool`**: Wraps the supplied method/function; the framework handles sending yielded updates and the final return value as sequential FunctionResponses.
- **Agent instruction**: Directs the LLM to use the tool and understand the incoming FunctionResponse stream (progress vs. completion) for user updates.
- **Final return**: The function returns the final result dictionary, which is sent in the concluding FunctionResponse to indicate completion.

## Agent-as-a-Tool

This powerful feature allows you to leverage the capabilities of other agents within your system by calling them as tools. The Agent-as-a-Tool enables you to invoke another agent to perform a specific task, effectively **delegating responsibility**. This is conceptually similar to creating a Python function that calls another agent and uses the agent's response as the function's return value.

### Key difference from sub-agents

It's important to distinguish an Agent-as-a-Tool from a Sub-Agent.

- **Agent-as-a-Tool:** When Agent A calls Agent B as a tool (using Agent-as-a-Tool), Agent B's answer is **passed back** to Agent A, which then summarizes the answer and generates a response to the user. Agent A retains control and continues to handle future user input.
- **Sub-agent:** When Agent A calls Agent B as a sub-agent, the responsibility of answering the user is completely **transferred to Agent B**. Agent A is effectively out of the loop. All subsequent user input will be answered by Agent B.

### Usage

To use an agent as a tool, wrap the agent with the AgentTool class.

```python
tools=[AgentTool(agent=agent_b)]
```

```typescript
tools: [new AgentTool({agent: agentB})]
```

```go
agenttool.New(agent, &agenttool.Config{...})
```

```java
AgentTool.create(agent)
```

### Customization

The `AgentTool` class provides the following attributes for customizing its behavior:

- **skip_summarization: bool:** If set to True, the framework will **bypass the LLM-based summarization** of the tool agent's response. This can be useful when the tool's response is already well-formatted and requires no further processing.

Example

```python
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
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

APP_NAME="summary_agent"
USER_ID="user1234"
SESSION_ID="1234"

summary_agent = Agent(
    model="gemini-2.0-flash",
    name="summary_agent",
    instruction="""You are an expert summarizer. Please read the following text and provide a concise summary.""",
    description="Agent to summarize text",
)

root_agent = Agent(
    model='gemini-2.0-flash',
    name='root_agent',
    instruction="""You are a helpful assistant. When the user provides a text, use the 'summarize' tool to generate a summary. Always forward the user's message exactly as received to the 'summarize' tool, without modifying or summarizing it yourself. Present the response from the tool to the user.""",
    tools=[AgentTool(agent=summary_agent, skip_summarization=True)]
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


long_text = """Quantum computing represents a fundamentally different approach to computation, 
leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers 
that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively 
being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled, 
meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and 
interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such 
as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far 
faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages."""


# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async(long_text)
```

```typescript
/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import {
  AgentTool,
  InMemoryRunner,
  LlmAgent,
} from '@google/adk';
import {Part, createUserContent} from '@google/genai';

/**
 * This example demonstrates how to use an agent as a tool.
 */
async function main() {
  // Define the summarization agent that will be used as a tool
  const summaryAgent = new LlmAgent({
    name: 'summary_agent',
    model: 'gemini-2.5-flash',
    description: 'Agent to summarize text',
    instruction:
      'You are an expert summarizer. Please read the following text and provide a concise summary.',
  });

  // Define the main agent that uses the summarization agent as a tool.
  // skipSummarization is set to true, so the main_agent will directly output
  // the result from the summary_agent without further processing.
  const mainAgent = new LlmAgent({
    name: 'main_agent',
    model: 'gemini-2.5-flash',
    instruction:
      "You are a helpful assistant. When the user provides a text, use the 'summary_agent' tool to generate a summary. Always forward the user's message exactly as received to the 'summary_agent' tool, without modifying or summarizing it yourself. Present the response from the tool to the user.",
    tools: [new AgentTool({agent: summaryAgent, skipSummarization: true})],
  });

  const appName = 'agent-as-a-tool-app';
  const runner = new InMemoryRunner({agent: mainAgent, appName});

  const longText = `Quantum computing represents a fundamentally different approach to computation, 
leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers 
that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively 
being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled, 
meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and 
interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such 
as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far 
faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages.`;

  // Create the session before running the agent
  await runner.sessionService.createSession({
    appName,
    userId: 'user1',
    sessionId: 'session1',
  });

  // Run the agent with the long text to summarize
  const events = runner.runAsync({
    userId: 'user1',
    sessionId: 'session1',
    newMessage: createUserContent(longText),
  });

  // Print the final response from the agent
  console.log('Agent Response:');
  for await (const event of events) {
    if (event.content?.parts?.length) {
      const responsePart = event.content.parts.find((p: Part) => p.functionResponse);
      if (responsePart && responsePart.functionResponse) {
        console.log(responsePart.functionResponse.response);
      }
    }
  }
}

main();
```

```go
import (
    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/agenttool"
    "google.golang.org/genai"
)

// createSummarizerAgent creates an agent whose sole purpose is to summarize text.
func createSummarizerAgent(ctx context.Context) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
    if err != nil {
        return nil, err
    }
    return llmagent.New(llmagent.Config{
        Name:        "SummarizerAgent",
        Model:       model,
        Instruction: "You are an expert at summarizing text. Take the user's input and provide a concise summary.",
        Description: "An agent that summarizes text.",
    })
}

// createMainAgent creates the primary agent that will use the summarizer agent as a tool.
func createMainAgent(ctx context.Context, tools ...tool.Tool) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
    if err != nil {
        return nil, err
    }
    return llmagent.New(llmagent.Config{
        Name:  "MainAgent",
        Model: model,
        Instruction: "You are a helpful assistant. If you are asked to summarize a long text, use the 'summarize' tool. " +
            "After getting the summary, present it to the user by saying 'Here is a summary of the text:'.",
        Description: "The main agent that can delegate tasks.",
        Tools:       tools,
    })
}

func RunAgentAsToolSimulation() {
    ctx := context.Background()

    // 1. Create the Tool Agent (Summarizer)
    summarizerAgent, err := createSummarizerAgent(ctx)
    if err != nil {
        log.Fatalf("Failed to create summarizer agent: %v", err)
    }

    // 2. Wrap the Tool Agent in an AgentTool
    summarizeTool := agenttool.New(summarizerAgent, &agenttool.Config{
        SkipSummarization: true,
    })

    // 3. Create the Main Agent and provide it with the AgentTool
    mainAgent, err := createMainAgent(ctx, summarizeTool)
    if err != nil {
        log.Fatalf("Failed to create main agent: %v", err)
    }

    // 4. Run the main agent
    prompt := `
        Please summarize this text for me:
        Quantum computing represents a fundamentally different approach to computation,
        leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers
        that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively
        being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled,
        meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and
        interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such
        as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far
        faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages.
    `
    fmt.Printf("\nPrompt: %s\nResponse: ", prompt)
    callAgent(context.Background(), mainAgent, prompt)
    fmt.Println("\n---")
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.AgentTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;

public class AgentToolCustomization {

  private static final String APP_NAME = "summary_agent";
  private static final String USER_ID = "user1234";

  public static void initAgentAndRun(String prompt) {

    LlmAgent summaryAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("summaryAgent")
            .instruction(
                "You are an expert summarizer. Please read the following text and provide a concise summary.")
            .description("Agent to summarize text")
            .build();

    // Define root_agent
    LlmAgent rootAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("rootAgent")
            .instruction(
                "You are a helpful assistant. When the user provides a text, always use the 'summaryAgent' tool to generate a summary. Always forward the user's message exactly as received to the 'summaryAgent' tool, without modifying or summarizing it yourself. Present the response from the tool to the user.")
            .description("Assistant agent")
            .tools(AgentTool.create(summaryAgent, true)) // Set skipSummarization to true
            .build();

    // Create an InMemoryRunner
    InMemoryRunner runner = new InMemoryRunner(rootAgent, APP_NAME);
    // InMemoryRunner automatically creates a session service. Create a session using the service
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();
    Content userMessage = Content.fromParts(Part.fromText(prompt));

    // Run the agent
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    // Stream event response
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }

  public static void main(String[] args) {
    String longText =
        """
            Quantum computing represents a fundamentally different approach to computation,
            leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers
            that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively
            being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled,
            meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and
            interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such
            as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far
            faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages.""";

    initAgentAndRun(longText);
  }
}
```

### How it works

1. When the `main_agent` receives the long text, its instruction tells it to use the 'summarize' tool for long texts.
1. The framework recognizes 'summarize' as an `AgentTool` that wraps the `summary_agent`.
1. Behind the scenes, the `main_agent` will call the `summary_agent` with the long text as input.
1. The `summary_agent` will process the text according to its instruction and generate a summary.
1. **The response from the `summary_agent` is then passed back to the `main_agent`.**
1. The `main_agent` can then take the summary and formulate its final response to the user (e.g., "Here's a summary of the text: ...")
