# Service registration

Supported in ADKPython v1.34.0

Extend ADK runtime capabilities by registering custom services for sessions, artifacts, memory, and Agent2Agent (A2A) task stores. Registering custom services allows you to integrate your own backend systems and storage providers into your agents.

Register custom services using either of the following methods:

- **`services.yaml`**: A YAML configuration file for services that instantiate with simple constructors.
- **`services.py`**: A Python script for services that require custom initialization or complex logic.

## Register services with `services.yaml`

Use a `services.yaml` or `services.yml` file to register services that instantiate with a simple constructor (for example, `MyService(uri="...")`). Place this file in the agent directory (for `adk run`) or the agents root directory (for `adk web` and `adk api_server`).

Define your custom services in `services.yaml`:

```yaml
services:
  - scheme: mysession
    type: session
    class: my_custom_package.modules.MyCustomSessionService
  - scheme: myartifact
    type: artifact
    class: my_custom_package.storage.MyCustomArtifactService
  - scheme: mymemory
    type: memory
    class: my_custom_package.modules.MyCustomMemoryService
  - scheme: mytaskstore
    type: task_store
    class: my_custom_package.tasks.MyCustomTaskStore
```

The `services.yaml` file supports the following properties:

- `scheme`: The URI scheme that triggers the custom service (for example, `mysession://`).
- `type`: The type of service, which can be `session`, `artifact`, `memory`, or `task_store`.
- `class`: The fully qualified class name of the service implementation.

## Register services with `services.py`

Use a `services.py` file, placed in the same location as `services.yaml`, for complex initialization or when you require more control over the service creation process.

Register custom `session`, `artifact`, and `memory` services in `services.py`:

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

1. Import `get_service_registry` to retrieve the service registry instance.
1. Define factory functions (such as `my_session_factory`) that take a URI and keyword arguments, and return an instance of the custom service.
1. Use `register_session_service`, `register_artifact_service`, and `register_memory_service` to register the factory functions with the desired schemes (such as `mysession`).

## Load services

When you run your agent with ADK command-line tools (`adk run`, `adk web`, or `adk api_server`), ADK automatically discovers and loads custom services from `services.yaml` (or `services.yml`) and `services.py`.

### Discovery locations

ADK locates configuration files based on the command you run:

- **`adk run`**: Discovers service files in the agent directory.
- **`adk web` and `adk api_server`**: Discover service files in the agents root directory passed to the command.

### Loading order and precedence

When both `services.yaml` and `services.py` are present in the target directory:

1. **Loading order**: ADK loads `services.yaml` first, followed by `services.py`.
1. **Precedence**: If a service with the same scheme is defined in both files, the definition in `services.py` takes precedence.
