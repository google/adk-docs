# Service Registration

The ADK service registry allows you to extend the capabilities of the ADK by registering custom services for sessions, artifacts, and memory. This enables you to integrate your own backend systems or logic with the ADK runtime.

You can register custom services using two methods:

*   **`services.yaml`**: A simple YAML file for basic service registration.
*   **`services.py`**: A Python script for more complex registration logic.

## Registering Services with `services.yaml`

If your custom service can be instantiated with a simple constructor like `MyService(uri="...")`, you can register it using a `services.yaml` or `services.yml` file in your agent's directory.

**Example `services.yaml`:**

```yaml
services:
  - scheme: mysession
    type: session
    class: my_package.my_module.MyCustomSessionService
  - scheme: mymemory
    type: memory
    class: my_package.other_module.MyCustomMemoryService
```

In this example:

*   `scheme`: The URI scheme that will trigger your custom service (e.g., `mysession://`).
*   `type`: The type of service, which can be `session`, `artifact`, or `memory`.
*   `class`: The fully qualified class name of your service implementation.

## Registering Services with `services.py`

For more complex initialization or when you need more control over the service creation process, you can use a `services.py` file in your agent's directory.

**Example `services.py`:**

```python
from google.adk.cli.service_registry import get_service_registry
from my_package.my_module import MyCustomSessionService

def my_session_factory(uri: str, **kwargs):
    # Add your custom logic here
    return MyCustomSessionService(...)

get_service_registry().register_session_service("mysession", my_session_factory)
```

In this example:

1.  We import `get_service_registry` to get the service registry instance.
2.  We define a factory function (`my_session_factory`) that takes a URI and keyword arguments, and returns an instance of our custom service.
3.  We use `register_session_service` to register our factory function with the desired scheme (`mysession`).

You can also use `register_artifact_service` and `register_memory_service` for artifact and memory services, respectively.

## Loading Services

When you run your agent, the ADK automatically discovers and loads services from `services.yaml` (or `services.yml`) and `services.py` files in your agent's directory. If both files are present, `services.yaml` is loaded first, followed by `services.py`. If a service with the same scheme is defined in both files, the definition in `services.py` will take precedence.