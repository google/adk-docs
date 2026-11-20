# Get user choice

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v1.6.0</span><span class="lst-kotlin">Kotlin v0.5.0</span>
</div>

The `get_user_choice` tool in Agent Development Kit (ADK) lets an agent pause
its run and ask the end user to pick one option from a list. The model decides when to call the tool and which
options to offer. Your client application shows the options to the user and
sends the selection back to the agent, which then continues with the user's
answer. Use this tool when the agent has concrete alternatives and the user
should decide between them, for example:

-   Choosing a flight, hotel, or delivery slot from a set of search results.
-   Picking which of several matching records, such as customer accounts, the
    agent should act on.
-   Selecting a plan, size, or configuration before the agent places an order.

This tool is a [long-running function
tool](/tools-custom/function-tools/#long-run-tool). It returns no result of its
own, so the agent run stops on the tool call and waits until your client
provides the user's choice.

## Get started

Add the `get_user_choice` tool to an agent and tell the agent in its
instructions when to offer a choice. The following example creates a
travel-planning agent that asks the user to pick from options it proposes:

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools import get_user_choice

    root_agent = Agent(
        name="trip_planner",
        model="gemini-flash-latest",
        instruction="""
            You are a travel-planning assistant. When the user should pick
            between concrete alternatives, call get_user_choice with the list
            of options. Wait for the user's choice before you continue.
        """,
        tools=[get_user_choice],
    )
    ```

=== "TypeScript"

    ```typescript
    import {LlmAgent, getUserChoiceTool} from '@google/adk';

    export const rootAgent = new LlmAgent({
      name: 'trip_planner',
      model: 'gemini-flash-latest',
      instruction: `
        You are a travel-planning assistant. When the user should pick
        between concrete alternatives, call get_user_choice with the list
        of options. Wait for the user's choice before you continue.
      `,
      tools: [getUserChoiceTool],
    });
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.agents.Instruction
    import com.google.adk.kt.agents.LlmAgent
    import com.google.adk.kt.models.Gemini
    import com.google.adk.kt.tools.GetUserChoiceTool

    val rootAgent =
        LlmAgent(
            name = "trip_planner",
            model = Gemini(name = "gemini-flash-latest"),
            instruction =
                Instruction(
                    """
                    You are a travel-planning assistant. When the user should pick
                    between concrete alternatives, call get_user_choice with the list
                    of options. Wait for the user's choice before you continue.
                    """.trimIndent()
                ),
            tools = listOf(GetUserChoiceTool()),
        )
    ```

When the model calls the tool, the run ends with an event that contains a
`get_user_choice` function call, such as the following:

```json
{
  "name": "get_user_choice",
  "id": "adk-6f1c...",
  "args": {"options": ["Window seat", "Aisle seat", "No preference"]}
}
```

The event also lists the function call ID in its long-running tool IDs, which
marks the call as waiting for a response. To continue the run, return the
user's choice as described in the next section.

## Return the user's choice

To complete a `get_user_choice` call, your client application does the
following:

1.  Reads the run's events and finds the `get_user_choice` function call whose
    ID appears in the event's long-running tool IDs.
2.  Shows the `options` from the function call arguments to the user and
    collects the selection.
3.  Starts a new run in the same session with a user message that contains a
    `FunctionResponse`. The response must use the same function call ID and the
    name `get_user_choice`, and carry the selection in its `response` payload.

The agent passes the function response to the model, which continues with the
user's choice. The following example runs the agent from the previous section,
answers the first `get_user_choice` call with the first option, and prints the
agent's reply:

=== "Python"

    ```python
    import asyncio

    from google.adk.runners import InMemoryRunner
    from google.genai import types

    APP_NAME = "trip_planner_app"
    USER_ID = "user_1"


    def find_user_choice_call(event):
        """Returns the pending get_user_choice call in an event, if any."""
        for call in event.get_function_calls():
            if (
                call.name == "get_user_choice"
                and call.id in (event.long_running_tool_ids or set())
            ):
                return call
        return None


    def print_text(event):
        if event.content and event.content.parts:
            if text := "".join(part.text or "" for part in event.content.parts):
                print(f"[{event.author}]: {text}")


    async def main():
        runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
        session = await runner.session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID
        )

        # Turn 1: the agent offers options and pauses.
        choice_call = None
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text="Book me a seat on the 9 AM flight.")],
            ),
        ):
            choice_call = choice_call or find_user_choice_call(event)
            print_text(event)

        if not choice_call:
            return

        # Show choice_call.args["options"] to the user in your UI. This example
        # picks the first option.
        selection = choice_call.args["options"][0]

        # Turn 2: send the selection back with the same function call ID.
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[
                    types.Part(
                        function_response=types.FunctionResponse(
                            id=choice_call.id,
                            name=choice_call.name,
                            response={"choice": selection},
                        )
                    )
                ],
            ),
        ):
            print_text(event)


    asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript
    import {
      Event,
      InMemoryRunner,
      getFunctionCalls,
      stringifyContent,
    } from '@google/adk';
    import {FunctionCall, createUserContent} from '@google/genai';

    const APP_NAME = 'trip_planner_app';
    const USER_ID = 'user_1';

    // Returns the pending get_user_choice call in an event, if any.
    function findUserChoiceCall(event: Event): FunctionCall | undefined {
      return getFunctionCalls(event).find(
        (call) =>
          call.name === 'get_user_choice' &&
          call.id !== undefined &&
          (event.longRunningToolIds ?? []).includes(call.id),
      );
    }

    function printText(event: Event) {
      const text = stringifyContent(event);
      if (text) {
        console.log(`[${event.author}]: ${text}`);
      }
    }

    async function main() {
      const runner = new InMemoryRunner({agent: rootAgent, appName: APP_NAME});
      const session = await runner.sessionService.createSession({
        appName: APP_NAME,
        userId: USER_ID,
      });

      // Turn 1: the agent offers options and pauses.
      let choiceCall: FunctionCall | undefined;
      for await (const event of runner.runAsync({
        userId: USER_ID,
        sessionId: session.id,
        newMessage: createUserContent('Book me a seat on the 9 AM flight.'),
      })) {
        choiceCall ??= findUserChoiceCall(event);
        printText(event);
      }

      if (!choiceCall) {
        return;
      }

      // Show choiceCall.args.options to the user in your UI. This example
      // picks the first option.
      const options = choiceCall.args?.['options'] as string[];
      const selection = options[0];

      // Turn 2: send the selection back with the same function call ID.
      for await (const event of runner.runAsync({
        userId: USER_ID,
        sessionId: session.id,
        newMessage: {
          role: 'user',
          parts: [
            {
              functionResponse: {
                id: choiceCall.id,
                name: choiceCall.name,
                response: {choice: selection},
              },
            },
          ],
        },
      })) {
        printText(event);
      }
    }

    main();
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.events.Event
    import com.google.adk.kt.runners.InMemoryRunner
    import com.google.adk.kt.types.Content
    import com.google.adk.kt.types.FunctionCall
    import com.google.adk.kt.types.FunctionResponse
    import com.google.adk.kt.types.Part

    const val USER_ID = "user_1"
    const val SESSION_ID = "session_1"

    // Returns the pending get_user_choice call in an event, if any.
    fun findUserChoiceCall(event: Event): FunctionCall? =
        event.functionCalls().firstOrNull {
            it.name == "get_user_choice" && it.id in event.longRunningToolIds
        }

    fun printText(event: Event) {
        val text = event.content?.parts?.mapNotNull { it.text }?.joinToString("").orEmpty()
        if (text.isNotEmpty()) println("[${event.author}]: $text")
    }

    suspend fun main() {
        val runner = InMemoryRunner(agent = rootAgent, appName = "trip_planner_app")

        // Turn 1: the agent offers options and pauses.
        var choiceCall: FunctionCall? = null
        runner
            .runAsync(
                userId = USER_ID,
                sessionId = SESSION_ID,
                newMessage =
                    Content(
                        role = "user",
                        parts = listOf(Part(text = "Book me a seat on the 9 AM flight.")),
                    ),
            ).collect { event ->
                if (choiceCall == null) choiceCall = findUserChoiceCall(event)
                printText(event)
            }

        val call = choiceCall ?: return

        // Show the options to the user in your UI. This example picks the first one.
        val options = call.args["options"] as List<*>
        val selection = options.first().toString()

        // Turn 2: send the selection back with the same function call ID.
        val response =
            FunctionResponse(
                name = call.name,
                id = call.id,
                response = mapOf("choice" to selection),
            )
        runner
            .runAsync(
                userId = USER_ID,
                sessionId = SESSION_ID,
                newMessage = Content(role = "user", parts = listOf(Part(functionResponse = response))),
            ).collect(::printText)
    }
    ```

Keep the following in mind when you implement the response:

-   **Describe when to ask in the agent instruction.** The model decides when to
    call `get_user_choice` and which options to offer. State in the instruction
    which decisions belong to the user and that the agent must wait for the
    choice, so the model calls the tool instead of picking an option itself.
-   **Validate the selection in your client.** ADK does not check that the
    response matches one of the offered options. If your UI allows free-form
    input, check the value before you send it, or tell the model in the
    instruction how to handle an answer that is not in the list.
-   **Use a clear response payload.** The model reads the `response` payload as
    the result of the tool call. A simple payload such as `{"choice":
    "Aisle seat"}` is enough for the model to continue.

If your app uses the [Resume](/runtime/resume/) feature, the function
response must also target the invocation that made the `get_user_choice` call.
For details, see the note on long-running function responses in [Long running
function tools](/tools-custom/function-tools/#long-run-tool).

## Configuration options

The `get_user_choice` tool has no configuration options. You add the
predefined tool instance to an agent, and the model provides the tool's only
argument:

| Argument | Type | Description |
| :--- | :--- | :--- |
| `options` | List of strings | The options to present to the user. The model sets this value when it calls the tool. |

The tool is available in each language as follows:

| Language | Tool | Function call name |
| :--- | :--- | :--- |
| Python | `google.adk.tools.get_user_choice` | `get_user_choice` |
| TypeScript | `getUserChoiceTool` from `@google/adk` | `get_user_choice` |
| Kotlin | `com.google.adk.kt.tools.GetUserChoiceTool()` | `get_user_choice` |

## Next steps

-   [Long running function tools](/tools-custom/function-tools/#long-run-tool):
    Build your own tools that pause the agent run and wait for an external
    response.
-   [Get action confirmation for ADK Tools](/tools-custom/confirmation/):
    Require the user to confirm a tool call before it runs.
-   [Human input for agent workflows](/graphs/human-input/): Request input
    from the user at fixed steps in a graph workflow.
