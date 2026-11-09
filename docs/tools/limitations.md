# Limitations for ADK tools

Some ADK tools have limitations that can impact how you implement them within an
agent workflow. This page lists these tool limitations and workarounds, if available.

## One tool per agent limitation {#one-tool-one-agent}

!!! note "Search in ADK Python"

    For ADK Python, this search limitation applies to Google Search and Agent
    Search tools in ADK Python v1.15.0 and lower. ADK Python release v1.16.0 and
    higher provides a built-in workaround to remove this limitation.

!!! note "Go tool combinations"

    ADK Go does not impose a universal one-built-in-tool limit. Whether you can
    combine native tools with each other or with function tools depends on the
    model, backend API, and request configuration. Check the selected API's
    [tool-combination requirements](https://ai.google.dev/gemini-api/docs/generate-content/tool-combination).
    If the required combination is unsupported, wrap a specialist agent with
    `agenttool.New`, as shown in the Go tab under
    [Workaround #1](#workaround-1-agenttoolcreate-method).

In general, you can use more than one tool in an agent. Some SDK and model/API
combinations require the following native tools to be used without other tools
in the same agent request:

* [Code Execution](/integrations/code-execution/) with Gemini API (Note: in
  TypeScript, this requires Gemini 2.0+ and does not have this limitation)
* [Google Search](/integrations/google-search/) with Gemini API (Note:
  limitation only applies to Gemini 1.x models in TypeScript)
* [Agent Search](/integrations/agent-search/) (Note: currently unavailable in
  TypeScript)

The following examples illustrate combinations subject to these restrictions;
check the requirements for your SDK, model, and backend:

=== "Python"

    ```py
    root_agent = Agent(
        name="RootAgent",
        model="gemini-flash-latest",
        description="Code Agent",
        tools=[custom_function],
        code_executor=BuiltInCodeExecutor() # <-- NOT supported when used with tools
    )
    ```

=== "TypeScript"

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

=== "Java"

    ```java
     LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("You're a specialist in Google Search")
                .tools(new GoogleSearchTool(), new YourCustomTool()) // <-- NOT supported
                .build();
    ```

=== "Kotlin"

    ```kotlin
    val searchAgent = LlmAgent(
        name = "SearchAgent",
        model = Gemini(name = "gemini-flash-latest"),
        instruction = Instruction("You're a specialist in Google Search"),
        tools = listOf(GoogleSearchTool(), YourCustomTool()) // <-- NOT supported
    )
    ```

### Workaround #1: AgentTool.create() method

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript (v0.6.1+)</span><span class="lst-go">Go</span><span class="lst-java">Java</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

The following code sample demonstrates how to use multiple built-in tools or how
to use built-in tools with other tools by using multiple agents:

=== "Python"

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

=== "TypeScript"

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

=== "Go"

    Keep Google Search in a specialist agent and expose it to the parent as a
    function tool using `agenttool.New(searchAgent, nil)`. The parent can then
    combine that function tool with another function tool. The native search
    tool is sent only in the specialist's model requests.

    ```go
    --8<-- "examples/go/snippets/tools/agent-tool-workaround/main.go:agents"
    ```

    The specialist's model must support Google Search, and the parent's model
    must support function calling. This arrangement does not enable an
    unsupported native tool on a model. Go has no equivalent of Python's
    `bypass_multi_tools_limit` option.

    The complete example is `snippets/tools/agent-tool-workaround/main.go` in
    the [Go examples](https://github.com/google/adk-docs/tree/main/examples/go).
    [Configure a Gemini API key](/get-started/go/#set-your-api-key), then run
    from `examples/go`:

    ```shell
    go run ./snippets/tools/agent-tool-workaround
    ```

    Try: `What time is it in UTC, and what is the latest news about Go?`

=== "Java"

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

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/tools/LimitationsWorkaround.kt:workaround_1"
    ```

### Workaround #2: bypass_multi_tools_limit

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-java">Java</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

ADK Python has a built-in workaround which bypasses this limitation for
`GoogleSearchTool` and `VertexAiSearchTool` (use `bypass_multi_tools_limit=True` to enable it),
as shown in the
[built_in_multi_tools](https://github.com/google/adk-python/tree/main/contributing/samples/tools/built_in_multi_tools).
sample agent.

!!! warning

    Transfer-based sub-agents can add function tools for agent transfer. If
    your SDK, model, or API does not support combining those functions with a
    built-in tool, use an AgentTool wrapper instead. In Go, the compatibility
    requirements depend on the model, backend API, and request configuration,
    as described above. ADK Python provides the Search workaround mentioned
    above for `GoogleSearchTool` and `VertexAiSearchTool`.

The following examples illustrate transfer-based sub-agent configurations that
are subject to these SDK and model/API restrictions:

=== "Python"

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

=== "TypeScript"

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

=== "Java"

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

=== "Kotlin"

    ```kotlin
    val searchAgent = LlmAgent(
        model = Gemini(name = "gemini-flash-latest"),
        name = "SearchAgent",
        instruction = Instruction("You're a specialist in Google Search"),
        tools = listOf(GoogleSearchTool())
    )

    val codingAgent = LlmAgent(
        model = Gemini(name = "gemini-flash-latest"),
        name = "CodeAgent",
        instruction = Instruction("You're a specialist in Code Execution")
        // Kotlin currently doesn't have a BuiltInCodeExecutionTool in core
    )


    val rootAgent = LlmAgent(
        name = "RootAgent",
        model = Gemini(name = "gemini-flash-latest"),
        description = "Root Agent",
        subAgents = listOf(searchAgent, codingAgent) // Not supported when sub-agents use built-in tools
    )
    ```
