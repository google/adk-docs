# Limitations for ADK tools

Some ADK tools have limitations that can impact how you implement them within an agent workflow. This page lists these tool limitations and workarounds, if available.

## One tool per agent limitation

ONLY for Search in ADK Python v1.15.0 and lower

This limitation only applies to the use of Google Search and Agent Search tools in ADK Python v1.15.0 and lower. ADK Python release v1.16.0 and higher provides a built-in workaround to remove this limitation.

In general, you can use more than one tool in an agent, but use of specific tools within an agent excludes the use of any other tools in that agent. The following ADK Tools can only be used by themselves, without any other tools, in a single agent object:

- [Code Execution](/integrations/code-execution/) with Gemini API (Note: in TypeScript, this requires Gemini 2.0+ and does not have this limitation)
- [Google Search](/integrations/google-search/) with Gemini API (Note: limitation only applies to Gemini 1.x models in TypeScript)
- [Agent Search](/integrations/agent-search/) (Note: currently unavailable in TypeScript)

For example, the following approach that uses one of these tools along with other tools, within a single agent, is ***not supported***:

```py
root_agent = Agent(
    name="RootAgent",
    model="gemini-flash-latest",
    description="Code Agent",
    tools=[custom_function],
    code_executor=BuiltInCodeExecutor() # <-- NOT supported when used with tools
)
```

```typescript
import {Agent, BuiltInCodeExecutor} from '@google/adk';

const rootAgent = new Agent({
  name: 'RootAgent',
  model: 'gemini-flash-latest',
  description: 'Code Agent',
  tools: [myCustomTool], // Assume myCustomTool is defined
  codeExecutor: new BuiltInCodeExecutor(), // <-- NOT supported when used with tools
});
```

```java
 LlmAgent searchAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("SearchAgent")
            .instruction("You're a specialist in Google Search")
            .tools(new GoogleSearchTool(), new YourCustomTool()) // <-- NOT supported
            .build();
```

### Workaround #1: AgentTool.create() method

Supported in ADKPythonTypeScript (v0.6.1+)Java

The following code sample demonstrates how to use multiple built-in tools or how to use built-in tools with other tools by using multiple agents:

```py
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.code_executors import BuiltInCodeExecutor

search_agent = Agent(
    model='gemini-flash-latest',
    name='SearchAgent',
    instruction="""
    You're a specialist in Google Search
    """,
    tools=[google_search],
)
coding_agent = Agent(
    model='gemini-flash-latest',
    name='CodeAgent',
    instruction="""
    You're a specialist in Code Execution
    """,
    code_executor=BuiltInCodeExecutor(),
)
root_agent = Agent(
    name="RootAgent",
    model="gemini-flash-latest",
    description="Root Agent",
    tools=[AgentTool(agent=search_agent), AgentTool(agent=coding_agent)],
)
```

```typescript
import {Agent, AgentTool, BuiltInCodeExecutor, GOOGLE_SEARCH} from '@google/adk';

const searchAgent = new Agent({
  model: 'gemini-flash-latest',
  name: 'SearchAgent',
  instruction: "You're a specialist in Google Search",
  tools: [GOOGLE_SEARCH],
});

const codingAgent = new Agent({
  model: 'gemini-flash-latest', // Built-in code execution requires Gemini 2.0+ in ADK JS
  name: 'CodeAgent',
  instruction: "You're a specialist in Code Execution",
  codeExecutor: new BuiltInCodeExecutor(),
});

const rootAgent = new Agent({
  name: 'RootAgent',
  model: 'gemini-flash-latest',
  description: 'Root Agent',
  tools: [new AgentTool({agent: searchAgent}), new AgentTool({agent: codingAgent})],
});
```

```java
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.AgentTool;
import com.google.adk.tools.BuiltInCodeExecutionTool;
import com.google.adk.tools.GoogleSearchTool;
import com.google.common.collect.ImmutableList;

public class NestedAgentApp {

  private static final String MODEL_ID = "gemini-flash-latest";

  public static void main(String[] args) {

    // Define the SearchAgent
    LlmAgent searchAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("SearchAgent")
            .instruction("You're a specialist in Google Search")
            .tools(new GoogleSearchTool()) // Instantiate GoogleSearchTool
            .build();


    // Define the CodingAgent
    LlmAgent codingAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("CodeAgent")
            .instruction("You're a specialist in Code Execution")
            .tools(new BuiltInCodeExecutionTool()) // Instantiate BuiltInCodeExecutionTool
            .build();

    // Define the RootAgent, which uses AgentTool.create() to wrap SearchAgent and CodingAgent
    BaseAgent rootAgent =
        LlmAgent.builder()
            .name("RootAgent")
            .model(MODEL_ID)
            .description("Root Agent")
            .tools(
                AgentTool.create(searchAgent), // Use create method
                AgentTool.create(codingAgent)   // Use create method
             )
            .build();

    // Note: This sample only demonstrates the agent definitions.
    // To run these agents, you'd need to integrate them with a Runner and SessionService,
    // similar to the previous examples.
    System.out.println("Agents defined successfully:");
    System.out.println("  Root Agent: " + rootAgent.name());
    System.out.println("  Search Agent (nested): " + searchAgent.name());
    System.out.println("  Code Agent (nested): " + codingAgent.name());
  }
}
```

### Workaround #2: bypass_multi_tools_limit

Supported in ADKPythonJava

ADK Python has a built-in workaround which bypasses this limitation for `GoogleSearchTool` and `VertexAiSearchTool` (use `bypass_multi_tools_limit=True` to enable it), as shown in the [built_in_multi_tools](https://github.com/google/adk-python/tree/main/contributing/samples/built_in_multi_tools). sample agent.

Warning

Built-in tools cannot be used within a sub-agent, with the exception of `GoogleSearchTool` and `VertexAiSearchTool` in ADK Python because of the workaround mentioned above.

For example, the following approach that uses built-in tools within sub-agents is **not supported**:

```py
url_context_agent = Agent(
    model='gemini-flash-latest',
    name='UrlContextAgent',
    instruction="""
    You're a specialist in URL Context
    """,
    tools=[url_context],
)
coding_agent = Agent(
    model='gemini-flash-latest',
    name='CodeAgent',
    instruction="""
    You're a specialist in Code Execution
    """,
    code_executor=BuiltInCodeExecutor(),
)
root_agent = Agent(
    name="RootAgent",
    model="gemini-flash-latest",
    description="Root Agent",
    sub_agents=[
        url_context_agent,
        coding_agent
    ],
)
```

```typescript
import {Agent, BuiltInCodeExecutor} from '@google/adk';

const urlContextAgent = new Agent({
  model: 'gemini-flash-latest',
  name: 'UrlContextAgent',
  instruction: "You're a specialist in URL Context",
  tools: [myCustomTool], // Assume myCustomTool is defined
});

const codingAgent = new Agent({
  model: 'gemini-flash-latest',
  name: 'CodeAgent',
  instruction: "You're a specialist in Code Execution",
  codeExecutor: new BuiltInCodeExecutor(),
});

const rootAgent = new Agent({
  name: 'RootAgent',
  model: 'gemini-flash-latest',
  description: 'Root Agent',
  subAgents: [urlContextAgent, codingAgent], // NOT supported when sub-agents use built-in tools
});
```

```java
LlmAgent searchAgent =
    LlmAgent.builder()
        .model("gemini-flash-latest")
        .name("SearchAgent")
        .instruction("You're a specialist in Google Search")
        .tools(new GoogleSearchTool())
        .build();

LlmAgent codingAgent =
    LlmAgent.builder()
        .model("gemini-flash-latest")
        .name("CodeAgent")
        .instruction("You're a specialist in Code Execution")
        .tools(new BuiltInCodeExecutionTool())
        .build();


LlmAgent rootAgent =
    LlmAgent.builder()
        .name("RootAgent")
        .model("gemini-flash-latest")
        .description("Root Agent")
        .subAgents(searchAgent, codingAgent) // Not supported, as the sub agents use built in tools.
        .build();
```
