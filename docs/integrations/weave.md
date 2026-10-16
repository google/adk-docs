---
catalog_title: W&B Weave
catalog_description: Log, visualize, and analyze model calls and agent performance
catalog_icon: /integrations/assets/weave.png
catalog_tags: ["observability"]
---

# W&B Weave observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[W&B Weave](https://docs.wandb.ai/weave) traces ADK agent invocations,
sub-agent handoffs, model calls, and tool calls. Weave groups the resulting
traces by agent and conversation in the **Agents** view so you can inspect an
agent's behavior, latency, token usage, and cost.

## Prerequisites

- A [W&B account](https://wandb.ai) and
  [API key](https://wandb.ai/authorize)
- A [Google API key](https://aistudio.google.com/apikey) for Gemini

Set the credentials in your environment:

```bash
export WANDB_API_KEY=<your-wandb-api-key>
export GOOGLE_API_KEY=<your-google-api-key>
export GEMINI_API_KEY=<your-google-api-key>
```

Python ADK reads `GOOGLE_API_KEY`. The TypeScript example below reads
`GEMINI_API_KEY`.

## Install dependencies

=== "Python"

    ```bash
    pip install weave google-adk
    ```

=== "TypeScript"

    ```bash
    npm install weave @google/adk zod
    ```

## Trace an ADK agent

Initialize Weave with your W&B team and project, then create and run your ADK
agent normally.

=== "Python"

    The Python SDK detects ADK when `weave.init()` runs and patches it for
    tracing. Import ADK before initializing Weave, as shown here.

    ```python
    import asyncio

    import weave
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner
    from google.genai import types


    weave.init("<your-team>/<your-project>")


    def add(a: float, b: float) -> dict[str, float]:
        """Add two numbers."""
        return {"total": a + b}


    root_agent = Agent(
        name="calculator_agent",
        model="gemini-2.5-flash",
        instruction="Use the add tool to answer arithmetic questions.",
        tools=[add],
    )


    async def main() -> None:
        runner = InMemoryRunner(
            agent=root_agent,
            app_name="weave-adk-example",
        )
        session = await runner.session_service.create_session(
            app_name="weave-adk-example",
            user_id="example-user",
        )

        async for event in runner.run_async(
            user_id="example-user",
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text="What is 17 plus 25?")],
            ),
        ):
            if event.is_final_response() and event.content:
                print(event.content.parts[0].text)


    asyncio.run(main())
    ```

=== "TypeScript"

    Register `WeaveAdkPlugin` on the runner. Explicit registration works in
    ESM, CommonJS, and bundled applications without a module-loader hook.

    ```typescript
    import {
      FunctionTool,
      Gemini,
      InMemoryRunner,
      LlmAgent,
    } from "@google/adk";
    import { flushOTel, init, WeaveAdkPlugin } from "weave";
    import { z } from "zod";

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error("Set GEMINI_API_KEY before running this example.");
    }

    const addTool = new FunctionTool({
      name: "add",
      description: "Add two numbers.",
      parameters: z.object({
        a: z.number(),
        b: z.number(),
      }),
      execute: async ({ a, b }) => ({ total: a + b }),
    });

    async function main() {
      await init("<your-team>/<your-project>");

      const agent = new LlmAgent({
        name: "calculator_agent",
        description: "Answers arithmetic questions.",
        instruction: "Use the add tool to answer arithmetic questions.",
        model: new Gemini({ model: "gemini-2.5-flash", apiKey }),
        tools: [addTool],
      });

      const appName = "weave-adk-example";
      const userId = "example-user";
      const runner = new InMemoryRunner({
        agent,
        appName,
        plugins: [new WeaveAdkPlugin()],
      });
      const session = await runner.sessionService.createSession({
        appName,
        userId,
      });

      for await (const event of runner.runAsync({
        userId,
        sessionId: session.id,
        newMessage: {
          role: "user",
          parts: [{ text: "What is 17 plus 25?" }],
        },
      })) {
        const text = event.content?.parts
          ?.map((part) => part.text)
          .filter(Boolean)
          .join("");
        if (text) console.log(text);
      }

      await flushOTel();
    }

    main().catch(console.error);
    ```

After the run completes, open your W&B project and select **Weave** >
**Agents**. The trace shows the agent invocation with its model and tool calls,
including their inputs, outputs, timing, token usage, and cost when available.

![Traces in Weave](https://wandb.github.io/weave-public-assets/google-adk/traces-overview.png)

## Data and privacy

Weave sends trace data to the W&B service configured by your SDK. Depending on
the agent, this data can include prompts, model responses, tool inputs and
outputs, and application metadata. Review your security, privacy, and retention
requirements before tracing sensitive workloads.

## Additional resources

- [Google ADK integration guide](https://docs.wandb.ai/weave/guides/integrations/agents/google-adk)
- [W&B Weave documentation](https://docs.wandb.ai/weave)
- [Navigate the trace view](https://docs.wandb.ai/weave/guides/tracking/trace-tree)
