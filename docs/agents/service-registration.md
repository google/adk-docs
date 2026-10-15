# Service registration

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.17.0</span>
</div>

Extend the capabilities of ADK by registering custom services for sessions,
artifacts, and memory. Integrate your own backend systems or logic with the
ADK runtime.

Register custom services using two methods:

*   **`services.yaml`**: A simple YAML file for basic service registration.
*   **`services.py`**: A Python script for more complex registration logic.

## Register services with `services.yaml`

Register services that instantiate with a simple constructor (for example,
`MyService(uri="...")`) using a `services.yaml` or `services.yml` file in the
agent directory (for `adk run`) or the agents root directory (for `adk web`
and `adk api_server`).

**Example `services.yaml`:**

```yaml
services:
  - scheme: mysession
    type: session
    class: my_custom_package.modules.MyCustomSessionService
  - scheme: mymemory
    type: memory
    class: my_custom_package.modules.MyCustomMemoryService
```

The `services.yaml` file supports the following properties:

*   `scheme`: The URI scheme that triggers the custom service (for example,
    `mysession://`).
*   `type`: The type of service, which can be `session`, `artifact`, or
    `memory`.
*   `class`: The fully qualified class name of the service implementation.

## Register services with `services.py`

Use a `services.py` file in the agent directory for complex initialization or
when you require more control over the service creation process.

**Example `services.py`:**

```python
from google.adk.cli.service_registry import get_service_registry
from my_custom_package.modules import MyCustomSessionService
from my_custom_package.storage import MyCustomArtifactService
from my_custom_package.memory import MyCustomMemoryService

def my_session_factory(uri: str, **kwargs):
    # Add your custom logic here.
    return MyCustomSessionService(uri=uri, **kwargs)

def my_artifact_factory(uri: str, **kwargs):
    """Factory function to instantiate a custom artifact service."""
    return MyCustomArtifactService(uri=uri, **kwargs)

def my_memory_factory(uri: str, **kwargs):
    """Factory function to instantiate a custom memory service."""
    return MyCustomMemoryService(uri=uri, **kwargs)

# Retrieve the registry.
registry = get_service_registry()

# Register session, artifact, and memory services.
registry.register_session_service("mysession", my_session_factory)
registry.register_artifact_service("myartifact", my_artifact_factory)
registry.register_memory_service("mymemory", my_memory_factory)
```

The example script performs the following tasks:

1.  Import `get_service_registry` to retrieve the service registry instance.
2.  Define factory functions (such as `my_session_factory`) that take a URI and
    keyword arguments, and return an instance of the custom service.
3.  Use `register_session_service`, `register_artifact_service`, and
    `register_memory_service` to register the factory functions with the
    desired schemes (such as `mysession`).

## Load services

When you run your agent with the ADK command line tools (`adk run`, `adk web`,
or `adk api_server`), ADK automatically discovers and loads services from
`services.yaml` (or
`services.yml`) and `services.py` files. `adk run` looks in the agent
directory; `adk web` and `adk api_server` look in the agents root directory you
pass to the command. If both files
are present, ADK loads `services.yaml` first, followed by `services.py`. If a
service with the same scheme is defined in both files, the definition in
`services.py` takes precedence.

