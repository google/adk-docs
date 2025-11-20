# Custom Services

The ADK allows you to extend its functionality by registering your own custom services for session management, artifact storage, and memory. This is a powerful feature that lets you integrate the ADK with your own infrastructure or preferred backend systems.

You can register custom services in two ways:

1.  **YAML Configuration (`services.yaml`)**: Recommended for simple cases where your custom service can be instantiated with a URI and keyword arguments.
2.  **Python Registration (`services.py`)**: For more complex initialization logic.

If both `services.yaml` (or `.yml`) and `services.py` are present in the same directory, services from **both** files will be loaded. YAML files are processed first, then `services.py`. If the same service scheme is defined in both, the definition in `services.py` will overwrite the one from YAML.

## YAML Configuration (`services.yaml`)

If your custom service can be instantiated with `MyService(uri="...", **kwargs)`, you can register it without writing Python code by creating a `services.yaml` or `services.yml` file in your agent directory (e.g., `my_agent/services.yaml`).

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

*   `scheme`: The URI scheme that will trigger your custom service (e.g., `mysession://...`).
*   `type`: The type of service (`session`, `artifact`, or `memory`).
*   `class`: The full Python path to your custom service class.

## Python Registration (`services.py`)

For more complex initialization logic, create a `services.py` file in your agent directory (e.g., `my_agent/services.py`). In this file, you can get the service registry instance and register your custom factory functions.

**Example `services.py`:**

```python
from google.adk.cli.service_registry import get_service_registry
from my_package.my_module import MyCustomSessionService

def my_session_factory(uri: str, **kwargs):
    # custom logic to initialize your service
    return MyCustomSessionService(...)

get_service_registry().register_session_service("mysession", my_session_factory)
```

In this example, `my_session_factory` is a function that takes a URI and keyword arguments and returns an instance of your custom session service. You then register this factory with the service registry using the desired scheme.
