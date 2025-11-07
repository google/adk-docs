# App object for ADK

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.14.0</span>
</div>

The `App` class is a top-level container for an entire Agent Development Kit
(ADK) agent workflow. It is designed to manage the lifecycle, configuration, and
state for a collection of agents. The App class separates the concerns of an
agent workflow's overall operational infrastructure from individual agents'
task-oriented reasoning. 

Defining an App object in your ADK workflow is optional and changes how you
organize your agent code and run your agents. From a practical perspective, you
use the App class to configure the following features for your agent workflow:

*   [**Context caching**](/adk-docs/context/caching/)
*   [**Context compression**](/adk-docs/context/compaction/)
*   [**Agent resume**](/adk-docs/runtime/resume/)
*   [**Plugins**](/adk-docs/plugins/)

This guide explains how to use the App class for configuring and managing your
ADK agent workflows.

## Use the App class

The App class is used as the primary container of your agent workflow and
contains the root agent of the project.

### Define your Agent

First, define an agent using a class derived from BaseAgent. The
following code sample defines a simple greeter agent:

```python
from google.adk.agents import Agent

class GreeterAgent(Agent):
    name = "Greeter Agent"
    description = "An agent that provides a friendly greeting."

    def __call__(self, unused_input: str) -> str:
        return "Hello, world!"

```

### Define your App

Create a class that inherits from `App`. Configure this object with the
`root_agent` parameter and optional features, as shown in the following
sample code:

```python
from google.adk.apps import App

class MyGreeterApp(App):
    name = "Simple Greeter App"
    root_agent = GreeterAgent()
    # Optionally include App-level features:
    # plugins, context_cache_config, resumability_config

my_app = MyGreeterApp()
```

### Run your App

You can use the Runner class to run your agent workflow using the
`app` parameter, as shown in the following code sample:

```python
Runner.run(app=my_app, ...)
```

## Purpose of App Class

The `App` class addresses several architectural challenges that arise when
building complex, production-grade agentic systems:

*   **Centralized configuration:** Provides a single, centralized location for
    managing shared resources like API keys and database clients, avoiding the
    need to pass configuration down through every agent.
*   **Lifecycle management:** The `App` class includes `on_startup` and
    `on_shutdown` hooks, which allow for reliable management of persistent
    resources such as database connection pools or in-memory caches that need to
    exist across multiple invocations.
*   **State scope:** It defines an explicit boundary for application-level
     state with an `app:*` prefix making the scope and lifetime of this state
    clear to developers.
*   **Unit of deployment:** The `App` concept establishes a formal *deployable
    unit*, simplifying versioning, testing, and serving of agentic applications.

## Next steps

For a more complete sample code implementation, see the  
[Hello World App](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_app) 
code example.
