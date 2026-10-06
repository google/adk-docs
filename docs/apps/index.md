# App workflow management class

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.14.0</span><span class="lst-java">Java v0.1.0</span>
</div>

The ***App*** class is a top-level container for an entire Agent Development Kit
(ADK) agent workflow. It holds the ***root agent*** of the workflow together with
the configuration that applies to every agent in it. The **App** class
separates the concerns of an agent workflow's overall operational infrastructure
from individual agents' task-oriented reasoning.

Defining an ***App*** object in your ADK workflow is optional and changes how you
organize your agent code and run your agents. From a practical perspective, you
use the ***App*** class to configure the application-wide features listed in
[App fields](#app-fields).

This guide explains how to use the App class for configuring and managing your
ADK agent workflows.

## App fields

An ***App*** object has the following fields. Java uses the same fields in
camelCase, such as `rootAgent`.

| Field | Description |
|---|---|
| `name` | Required. The application name, which the `Runner` stores sessions under by default. Start it with a letter and use only letters, digits, and underscores. You cannot use `user` as the name, because ADK reserves it for end-user input. |
| `root_agent` | Required. The agent that handles each request. In ADK Python v2.0.0 and later, it can also be a [graph-based workflow](/graphs/). |
| `plugins` | [Plugins](/plugins/) that apply to every agent in the app. |
| `context_cache_config` | [Context caching](/context/caching/) settings for every LLM agent in the app. |
| `events_compaction_config` | [Context compression](/context/compaction/) settings for the app's sessions. |
| `resumability_config` | [Agent resume](/runtime/resume/) settings for every agent in the app. |

You pass services, such as the session service, to the `Runner`, and you store
application-wide state with the `app:` [state prefix](/sessions/state/), which
works with or without an ***App*** object.

## Define an App object

The ***App*** class is used as the primary container of your agent workflow and
contains the root agent of the project. The ***root agent*** is the container
for the primary controller agent and any additional sub-agents.

### Define app with root agent

Create a ***root agent*** for your workflow by creating an instance of the
***Agent*** class. Then define an ***App*** object and configure it with
the ***root agent*** object and optional features, as shown in the following
sample code:

=== "Python"

    ```python title="agent.py"
    from google.adk.agents.llm_agent import Agent
    from google.adk.apps import App

    root_agent = Agent(
        model='gemini-flash-latest',
        name='greeter_agent',
        description='An agent that provides a friendly greeting.',
        instruction='Reply with Hello, World!',
    )

    app = App(
        name="my_agent",
        root_agent=root_agent,
        # Optionally include App-level features:
        # plugins, context_cache_config, events_compaction_config,
        # resumability_config
    )
    ```

=== "Java"

    ```java title="AgentConfiguration.java"
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.apps.App;

    LlmAgent rootAgent = LlmAgent.builder()
        .model("gemini-flash-latest")
        .name("greeter_agent")
        .description("An agent that provides a friendly greeting.")
        .instruction("Reply with Hello, World!")
        .build();

    App app = App.builder()
        .name("agents")
        .rootAgent(rootAgent)
        // Optionally include App-level features:
        // .plugins(plugins)
        // .contextCacheConfig(contextCacheConfig)
        // .eventsCompactionConfig(eventsCompactionConfig)
        .build();
    ```

!!! tip "Recommended: Use the `app` variable name and match the folder name"

    In your agent project code, set your ***App*** object to the variable name
    `app` so it is compatible with the ADK command line interface runner tools.
    In Python, `adk run` and `adk web` load a module-level `app` variable first,
    and use `root_agent` only when there is no `app`.

    In Python, set the app `name` to the name of the folder that contains your
    agent code, such as `my_agent` for `my_agent/agent.py`. The `adk web`
    command stores sessions under the folder name. The `adk run` command stores
    them under the app `name`, and logs an app name mismatch warning if the app
    `name` differs from the folder name.

### Run your App agent

You can use the ***Runner*** class to run your agent workflow using the
`app` parameter, as shown in the following code sample:

=== "Python"

    ```python title="main.py"
    import asyncio
    from dotenv import load_dotenv
    from google.adk.runners import InMemoryRunner
    from agent import app # import code from agent.py

    load_dotenv() # load API keys and settings
    # Set a Runner using the imported application object
    runner = InMemoryRunner(app=app)

    async def main():
        try:  # run_debug() requires ADK Python 1.18 or higher:
            response = await runner.run_debug("Hello there!")

        except Exception as e:
            print(f"An error occurred during agent execution: {e}")

    if __name__ == "__main__":
        asyncio.run(main())

    ```

=== "Java"

    ```java title="AppMain.java"
    import com.google.genai.types.Content;
    import com.google.adk.runner.Runner;

    public class AppMain {

      public static void main(String[] args) throws Exception {
        // Set a Runner using the application object

        App app = ...;

        Runner runner = Runner.builder()
            .app(app) // Use the 'app' object defined previously
            .build();

        runner.runAsync("user", "session-1", Content.fromParts(Part.fromText("Hello there!")))
            .filter(event -> event.finalResponse() && event.content().isPresent())
            .blockingSubscribe(event -> System.out.println("Response: " + event.stringifyContent()));
      }
    }
    ```

!!! note "Version requirement for `Runner.run_debug()` "

    The `Runner.run_debug()` command requires ADK Python v1.18.0 or higher.
    You can also use `Runner.run()`, which requires more setup code. For
    more details, see the [Agent Runtime](/runtime/) guide.

=== "Python"

    Run your App agent with the `main.py` code using the following command:

    ```console
    python3 main.py
    ```

=== "Java"

    Run your App agent with the `AppMain.java` code using your build tool (e.g. Gradle `application` plugin):

    ```console
    ./gradlew run
    ```

## Next steps

For a more complete sample code implementation, see the
[Hello World App](https://github.com/google/adk-python/tree/main/contributing/samples/core/app)
code example.
