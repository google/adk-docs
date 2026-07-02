# A2A SDK Compatibility (a2a-sdk 0.3.x and 1.x.x)

ADK's A2A integration is compatible with both major versions of the A2A Python
SDK (`a2a-sdk` **0.3.x** and **1.x.x**) without requiring changes to ADK
application code. This document specifies the compatibility problem, the design adopted to solve it, and the complete set of version-divergence points together with their resolution in the internal compatibility module `google/adk/a2a/_compat.py`.

!!! warning "a2a-sdk 0.3.x is deprecated"

    a2a-sdk 0.3.x is on a deprecation path: it no longer receives updates, and
    ADK's support for it is a transitional measure that will be **removed in a
    future ADK release**. New integrations should target a2a-sdk **1.x.x**. See
    [Deprecation of a2a-sdk 0.3.x](#deprecation-of-a2a-sdk-03x).

## Problem statement

a2a-sdk 1.0 is a backwards-incompatible release. The changes that affect ADK's
A2A integration are summarized below.

| Concern | a2a-sdk 0.3.x behavior | a2a-sdk 1.x.x behavior |
| --- | --- | --- |
| **Data model** | Wire types (`Message`, `Task`, `Part`, `Artifact`, `TaskStatus`, update events) are Pydantic models. | The same wire types are protobuf messages, changing construction, field access, discriminated-union handling, and serialization. |
| **`Part` representation** | A wrapper exposing a discriminated union via `.root` (`TextPart` / `FilePart` / `DataPart`). | A flat protobuf message with a `oneof content` selecting `text`, `raw`, `url`, or `data`. |
| **Enumerations** | Pydantic enums, e.g. `Role.agent`, `TaskState.submitted`. | protobuf enum integers, e.g. `Role.ROLE_AGENT`, `TaskState.TASK_STATE_SUBMITTED`. |
| **Metadata** | A native `dict`. | A `google.protobuf.Struct`. |
| **Serialization** | `model_dump()` / `model_dump_json()`. | `MessageToDict()` / `MessageToJson()`. |
| **Deep copy** | `model_copy(deep=True)`. | `Message.CopyFrom()`. |
| **Server hosting API** | Route registration via the `A2AStarletteApplication` wiring. | Restructured registration using `create_agent_card_routes` / `create_jsonrpc_routes` with a `DefaultRequestHandler`. |
| **Request handler validation** | Permissive: an executor may publish a status update before a `Task`. | Stricter event ordering: the first event published for a new task must be a `Task`. |

Two additional constraints shape the solution:

1. **Single version per process.** Both majors are published under the same
   top-level `a2a` package, so exactly one version can be imported in a given
   Python process.
2. **The a2a-sdk version is selected by the integrator, not by ADK.** ADK does
   not pin `a2a-sdk`; it is provided as an optional dependency by the caller. ADK cannot mandate 1.x.x — doing so would break existing integrations pinned to 0.3.x — nor remain on 0.3.x, which would preclude 1.x.x adoption.

Consequently, ADK must support both versions concurrently, with version
selection deferred to the environment.

## Design: a shim layer with runtime version selection

ADK introduces a single internal module, `google/adk/a2a/_compat.py`, that
encapsulates every point of divergence between the two SDK majors. All other ADK
modules import the module itself (`from .. import _compat`) and reference its
helpers and constants in qualified form (`_compat.make_text_part(...)`,
`_compat.ROLE_AGENT`) rather than referencing `a2a.*` symbols that differ across
versions. The module's stated contract is to be the single point of divergence
between a2a-sdk 0.3.x and 1.x.x.

Version detection is performed once, at import time, by probing for a
1.x.x-exclusive symbol:

```python
# google/adk/a2a/_compat.py
try:
    from a2a.types import StreamResponse  # 1.x.x-only symbol
    IS_A2A_V1 = True
except ImportError:
    IS_A2A_V1 = False
```

Detection occurs exactly once per module import, so the branch selection has no
per-call overhead.

The resulting control flow:

```text
┌─────────────────────┐    ┌─────────────────────┐
│  ADK application    │───▶│  ADK public         │
│  code               │    │  A2A API            │
└─────────────────────┘    └─────────────────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │  _compat.py         │
                           │  (version branch)   │
                           └─────────────────────┘
                              │                │
                     IS_A2A_V1 = False   IS_A2A_V1 = True
                              ▼                ▼
                  ┌─────────────────┐  ┌─────────────────┐
                  │  a2a-sdk 0.3.x  │  │  a2a-sdk 1.x.x    │
                  │  (Pydantic)     │  │  (protobuf)     │
                  └─────────────────┘  └─────────────────┘
```

`_compat` is an internal module. Application code does not import it; it
interacts with ADK's public A2A APIs, and ADK routes version-sensitive
operations through `_compat` internally.

## Compatibility layer specification

### Enums and constants

Enum spellings and representations differ; `_compat` exports stable aliases.

**Direct:**

```python
# 0.3.x
role = Role.agent
state = TaskState.submitted
# 1.x.x
role = Role.ROLE_AGENT
state = TaskState.TASK_STATE_SUBMITTED
```

**Via `_compat`:**

```python
role, state = _compat.ROLE_AGENT, _compat.TS_SUBMITTED
```

**`_compat` implementation:**

```python
if IS_A2A_V1:
    ROLE_USER, ROLE_AGENT = Role.Value("ROLE_USER"), Role.Value("ROLE_AGENT")
    TS_SUBMITTED = TaskState.Value("TASK_STATE_SUBMITTED")
    TP_JSONRPC = TransportProtocol.JSONRPC
    # ...
else:
    ROLE_USER, ROLE_AGENT = Role.user, Role.agent
    TS_SUBMITTED = TaskState.submitted
    TP_JSONRPC = TransportProtocol.jsonrpc
    # ...
```

Exported constants: `IS_A2A_V1`; roles `ROLE_USER`, `ROLE_AGENT`; task states
`TS_SUBMITTED`, `TS_WORKING`, `TS_COMPLETED`, `TS_FAILED`, `TS_INPUT_REQUIRED`,
`TS_AUTH_REQUIRED`, `TS_CANCELED`; transport protocols `TP_JSONRPC`,
`TP_HTTP_JSON`, `TP_GRPC`.

### Part construction and inspection

The `Part` representation is the most significant data-model divergence.

**Direct:**

```python
# 0.3.x — discriminated union via .root
part = Part(root=TextPart(text="hi"))
is_text = isinstance(part.root, TextPart)
text = part.root.text
# 1.x.x — flat message, oneof content
part = Part(text="hi")
is_text = part.WhichOneof("content") == "text"
text = part.text
```

**Via `_compat`:**

```python
part = _compat.make_text_part("hi")
text = _compat.part_text(part) if _compat.is_text_part(part) else None
```

**`_compat` implementation:**

```python
def make_text_part(text: str) -> Part:
    return Part(text=text) if IS_A2A_V1 else Part(root=TextPart(text=text))

def is_text_part(p: Part) -> bool:
    return p.WhichOneof("content") == "text" if IS_A2A_V1 else isinstance(p.root, TextPart)

def part_text(p: Part) -> str:
    return p.text if IS_A2A_V1 else p.root.text
```

Related symbols: `is_file_part`, `is_data_part`, `part_metadata`,
`set_part_metadata`, `part_kind_label`.

### File and data parts

File and data parts differ in construction (byte encoding, field placement) and
in payload representation (`Struct` vs `dict`).

**Direct:**

```python
# 0.3.x — construct via .root/FilePart, read via .root.file
part = Part(root=FilePart(file=FileWithUri(uri=uri, mime_type=mt, name=name)))
uri, mt = part.root.file.uri, part.root.file.mime_type
# 1.x.x — construct/read flat fields
part = Part(url=uri, media_type=mt, filename=name)
uri, mt = part.url, part.media_type
```

**Via `_compat`:**

```python
part = _compat.make_file_part_with_uri(uri=uri, mime_type=mt, name=name)
uri, mt = _compat.file_part_uri(part), _compat.file_part_mime_type(part)
```

| Symbol | Responsibility |
| --- | --- |
| `make_file_part_with_uri` | construct a URI-backed file part |
| `make_file_part_with_bytes` | construct a bytes-backed file part |
| `make_data_part` | construct a structured-data part |
| `make_data_part_from_blob` | reconstruct a data part from a serialized blob |
| `file_part_uri`, `file_part_bytes` | accessors for URI / raw bytes |
| `file_part_mime_type`, `file_part_name` | accessors for media type / filename |
| `data_part_dict` | read a data part payload as `dict` |
| `data_part_blob_bytes` | serialize a data part payload to `bytes` |

### Serialization and metadata

Serialization moves from Pydantic (`model_dump*`) to protobuf JSON utilities;
metadata is a `dict` in 0.3.x and a `Struct` in 1.x.x.

**Direct:**

```python
# 0.3.x (Pydantic models, dict metadata)
d = obj.model_dump(exclude_none=True, by_alias=True)   # serialize to a dict
value = metadata.get("key")                            # read one metadata key
plain = metadata or {}                                 # normalize metadata to a dict
# 1.x.x (protobuf messages, Struct metadata)
d = MessageToDict(obj)                                  # serialize to a dict
value = metadata["key"] if "key" in metadata else None  # Struct: `in` + indexing, no .get
plain = MessageToDict(metadata)                        # normalize metadata to a dict
```

**Via `_compat`:**

```python
d = _compat.a2a_to_dict(obj)
value = _compat.metadata_get(metadata, "key")
plain = _compat.meta_to_dict(metadata)          # normalized dict
```

Related symbols: `set_struct_metadata`, `set_event_metadata`.

### Agent cards

The `AgentCard` model changed, most notably the removal of a top-level `url`
field in favor of `supported_interfaces`.

**Direct:**

```python
# 0.3.x (Pydantic)
url = card.url                                    # read the RPC URL
card = AgentCard(**json_dict)                     # build a card from a JSON dict
# 1.x.x (protobuf)
url = card.supported_interfaces[0].url            # read the RPC URL
card = parse_agent_card(json_dict)                # a2a.client.card_resolver.parse_agent_card
```

**Via `_compat`:**

```python
url = _compat.agent_card_url(card)
card = _compat.parse_agent_card(json_dict)
```

**`_compat` implementation:**

```python
def agent_card_url(card, *, protocol_binding=TP_JSONRPC) -> str | None:
    if IS_A2A_V1:
        interfaces = list(card.supported_interfaces)
        if not interfaces:
            return None
        for iface in interfaces:
            if getattr(iface, "protocol_binding", None) == protocol_binding:
                return iface.url
        return interfaces[0].url
    else:
        return getattr(card, "url", None)  # protocol_binding unused on 0.3.x
```

`build_agent_card` constructs a version-correct `AgentCard` from primitive
fields, avoiding constructor divergence at call sites.

### Client: message dispatch and stream normalization

`send_message` yields different shapes per version: 0.3.x yields
`tuple[Task, UpdateEvent | None]` or a bare `Message`; 1.x.x returns an
`AsyncIterator[StreamResponse]`, where each `StreamResponse` carries a `oneof`
payload (`task` / `message` / `status_update` / `artifact_update`). `_compat`
normalizes both into a uniform sequence of `(task, update)` items.

**Direct:**

```python
# 0.3.x — request is a Message; items are (Task, update|None) tuples or a bare Message
async for item in client.send_message(msg, context=ctx):
    if isinstance(item, tuple):
        task, update = item
    else:
        message = item
# 1.x.x — request is a SendMessageRequest; items are StreamResponse (oneof `payload`)
async for resp in client.send_message(SendMessageRequest(message=msg), context=ctx):
    for kind in ("task", "message", "status_update", "artifact_update"):
        if resp.HasField(kind):
            payload = getattr(resp, kind)
            break
```

**Via `_compat`** (as used by `RemoteA2aAgent`):

```python
normalize = _compat.make_stream_normalizer()   # stateful; one instance per stream
async for raw in _compat.send_message(client, request=req, context=ctx):
    task, update = normalize(raw)
    # ...
```

`make_stream_normalizer` returns a stateful callable that aggregates task state
across incremental updates (artifacts, status, and status-message history)
reproducing the aggregation performed by the 0.3.x client task manager so that
consumers always observe a fully materialized `Task`. Related symbols:
`stream_item_kind`, `make_client_config`, `rebind_client_factory_httpx`.

### Server hosting

Route registration for a Starlette/FastAPI application differs between versions.

**Direct:**

```python
# 0.3.x — legacy application wiring
a2a_app = A2AStarletteApplication(agent_card=card, http_handler=handler)
a2a_app.add_routes_to_app(app)
# 1.x.x — request handler + route factories
handler = DefaultRequestHandler(agent_executor=executor, task_store=store, agent_card=card)
app.routes.extend([
    *create_agent_card_routes(card),                          # card_url defaults to /.well-known/agent-card.json
    *create_jsonrpc_routes(handler, "/", enable_v0_3_compat=True),  # rpc_url is required
])
```

**Via `_compat`** (used by `to_a2a` and the ADK CLI):

```python
_compat.attach_a2a_routes_to_app(
    app,
    agent_card=card,
    agent_executor=executor,
    task_store=store,
    prefix="/a2a/my_agent",
)
```

The 1.x.x branch constructs a `DefaultRequestHandler` and registers routes via
`create_agent_card_routes` / `create_jsonrpc_routes`; the 0.3.x branch uses the
legacy `A2AStarletteApplication` wiring. Both are exposed behind a single call.

### Security schemes

**Direct:**

```python
# 0.3.x — wrapped via .root, uses the `in` keyword
scheme = SecurityScheme(root=APIKeySecurityScheme(name="X-API-Key", **{"in": "header"}))
# 1.x.x — proto oneof, uses a `location` field
scheme = SecurityScheme(
    api_key_security_scheme=APIKeySecurityScheme(name="X-API-Key", location="header"))
```

**Via `_compat`:**

```python
scheme = _compat.make_api_key_scheme(name="X-API-Key", location="header")
```

1.x.x models the API-key scheme as a protobuf `oneof` with a `location` field;
0.3.x wraps it via `.root` and uses the `in` keyword. The helper reconciles both.

### Extensions and executor event contract

- `add_activated_extension(context, uri)` — in 0.3.x this invoked an SDK method;
  in 1.x.x the method was removed (extensions are propagated via message metadata),
  so the helper is a no-op on 1.x.x.
- The 1.x.x request handler requires that the first event published for a new task
  be a `Task`. ADK's legacy integration published a status update first; on 1.x.x
  `_compat` publishes a leading submitted `Task` so the validation is satisfied.

## Complete symbol reference

| Group | Symbols |
| --- | --- |
| Detection | `IS_A2A_V1` |
| Roles / states / transports | `ROLE_USER`, `ROLE_AGENT`, `TS_SUBMITTED`, `TS_WORKING`, `TS_COMPLETED`, `TS_FAILED`, `TS_INPUT_REQUIRED`, `TS_AUTH_REQUIRED`, `TS_CANCELED`, `TP_JSONRPC`, `TP_HTTP_JSON`, `TP_GRPC` |
| Parts | `make_text_part`, `is_text_part`, `is_file_part`, `is_data_part`, `part_text`, `part_metadata`, `set_part_metadata`, `part_kind_label` |
| File / data parts | `make_file_part_with_uri`, `make_file_part_with_bytes`, `make_data_part`, `make_data_part_from_blob`, `file_part_uri`, `file_part_bytes`, `file_part_mime_type`, `file_part_name`, `data_part_dict`, `data_part_blob_bytes` |
| Serialization / metadata | `a2a_to_dict`, `meta_to_dict`, `metadata_get`, `set_struct_metadata`, `set_event_metadata` |
| Agent card | `parse_agent_card`, `build_agent_card`, `agent_card_url` |
| Messages / tasks / status | `make_message`, `make_task`, `make_artifact`, `make_task_status`, `make_task_status_update_event`, `normalize_message`, `role_to_str` |
| Client / streaming | `make_client_config`, `rebind_client_factory_httpx`, `send_message`, `stream_item_kind`, `make_stream_normalizer` |
| Hosting | `attach_a2a_routes_to_app` |
| Security | `make_api_key_scheme` |
| Extensions | `add_activated_extension` |

## Deprecation of a2a-sdk 0.3.x

a2a-sdk 0.3.x is deprecated:

- It receives no further updates from the A2A project.
- ADK's dual-version support is a transitional mechanism and **will be removed**
  in a future ADK release once 1.x.x adoption is sufficient.
- Integrations should plan migration to a2a-sdk **1.x.x**; new projects should
  target 1.x.x from the outset.

The removal timeline will be communicated in the ADK release notes.

## Impact on integrators

- **Consumers of ADK's public A2A APIs** (`to_a2a`, `RemoteA2aAgent`, the CLI
  hosting helpers) require no source changes to move between SDK majors; the
  version is selected at install/build time:

    ```bash
    pip install 'a2a-sdk>=0.3.4,<0.4'   # 0.3.x (deprecated)
    pip install 'a2a-sdk>=1.0,<2'       # 1.x.x (recommended)
    ```

- **Code that references a2a-sdk types directly** (custom executors,
  request/response interceptors, hand-constructed `AgentCard` instances) must be
  migrated when moving to 1.x.x, because those are the SDK's own types and are
  outside ADK's shim boundary. Refer to the
  [A2A SDK v1.0 migration guide](https://github.com/a2aproject/a2a-python/tree/main/docs/migrations/v1_0).

## Next steps

- [A2A SDK v1.0 migration guide](https://github.com/a2aproject/a2a-python/tree/main/docs/migrations/v1_0)
