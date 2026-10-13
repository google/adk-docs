# Service registration

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
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
agent directory.

**Example `services.yaml`:**

```yaml
services:
  - scheme: mysession
    type: session
    class: example_package.example_module.MyCustomSessionService
  - scheme: mymemory
    type: memory
    class: example_package.other_module.MyCustomMemoryService
```

The properties in the YAML file are:

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
from example_package.example_module import MyCustomSessionService

def my_session_factory(uri: str, **kwargs):
    # Add your custom logic here.
    return MyCustomSessionService(uri=uri, **kwargs)

get_service_registry().register_session_service("mysession", my_session_factory)
```

The example script performs the following tasks:

1.  Import `get_service_registry` to retrieve the service registry instance.
2.  Define a factory function (`my_session_factory`) that takes a URI and
    keyword arguments, and returns an instance of the custom service.
3.  Use `register_session_service` to register the factory function with the
    desired scheme (`mysession`).

Use `register_artifact_service` and `register_memory_service` for artifact and
memory services, respectively.

## Load services

ADK automatically discovers and loads services from `services.yaml` (or
`services.yml`) and `services.py` files in the agent directory. If both files
are present, ADK loads `services.yaml` first, followed by `services.py`. If a
service with the same scheme is defined in both files, the definition in
`services.py` takes precedence.
