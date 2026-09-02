# App workflow management class

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.14.0</span><span class="lst-java">Java v0.1.0</span>
</div>

The ***App*** class is a top-level container for an entire Agent Development Kit
(ADK) agent workflow. It is designed to manage the lifecycle, configuration, and
state for a collection of agents grouped by a ***root agent***. The **App** class
separates the concerns of an agent workflow's overall operational infrastructure
from individual agents' task-oriented reasoning.

Defining an ***App*** object in your ADK workflow is optional and changes how you
organize your agent code and run your agents. From a practical perspective, you
use the ***App*** class to configure the following features for your agent workflow:

*   [**Context caching**](/context/caching/)
*   [**Context compression**](/context/compaction/)
*   [**Agent resume**](/runtime/resume/)
*   [**Plugins**](/plugins/)

This guide explains how to use the App class for configuring and managing your
ADK agent workflows.

## Purpose of App Class

The ***App*** class addresses several architectural issues that arise when
building complex agentic systems:

*   **Centralized configuration:** Provides a single, centralized location for
    managing shared resources like API keys and database clients, avoiding the
    need to pass configuration down through every agent.
*   **Lifecycle management:** The ***App*** class includes ***on startup*** and
    ***on shutdown*** hooks, which allow for reliable management of persistent
    resources such as database connection pools or in-memory caches that need to
    exist across multiple invocations.
*   **State scope:** It defines an explicit boundary for application-level
     state with an `app:*` prefix making the scope and lifetime of this state
    clear to developers.
*   **Unit of deployment:** The ***App*** concept establishes a formal *deployable
    unit*, simplifying versioning, testing, and serving of agentic applications.

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
    --8<-- "examples/inline/python/apps/index/001-define-app-with-root-agent.py"
    ```

=== "Java"

    ```java title="AgentConfiguration.java"
    --8<-- "examples/inline/java/apps/index/002-define-app-with-root-agent.java"
    ```

!!! tip "Recommended: Use `app` variable name"

    In your agent project code, set your ***App*** object to the variable name
    `app` so it is compatible with the ADK command line interface runner tools.

### Run your App agent

You can use the ***Runner*** class to run your agent workflow using the
`app` parameter, as shown in the following code sample:

=== "Python"

    ```python title="main.py"
    --8<-- "examples/inline/python/apps/index/003-run-your-app-agent.py"
    ```

=== "Java"

    ```java title="AppMain.java"
    --8<-- "examples/inline/java/apps/index/004-run-your-app-agent.java"
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
