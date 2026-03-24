# Production Readiness Checklist

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

Before deploying an ADK agent to production, work through the checklist below.
Each section maps to a risk category; items marked **Required** are baseline
expectations for any internet-facing deployment, while items marked
**Recommended** improve resilience and operability at scale.

---

## 1. Authentication & Authorization

| # | Item | Priority |
|---|------|----------|
| 1.1 | All HTTP, SSE, and WebSocket endpoints are protected by an authentication mechanism (API key, OAuth 2.0, or an identity-aware proxy). | **Required** |
| 1.2 | Session tokens are generated with a cryptographically strong random source (≥ 128 bits of entropy). | **Required** |
| 1.3 | Sessions have a configurable expiration time and are invalidated server-side on logout or timeout. | **Required** |
| 1.4 | Every `send_message` / `client_to_agent_messaging` call validates that the caller owns the target session before processing the message. | **Required** |
| 1.5 | Agent identity (service account) follows least-privilege: read-only access where read-only is sufficient; write access scoped to specific resources. | **Required** |
| 1.6 | User-delegated OAuth flows (User Auth) request only the minimum required scopes. | **Recommended** |

---

## 2. Input Validation & Payload Safety

| # | Item | Priority |
|---|------|----------|
| 2.1 | All external-facing endpoints enforce a maximum request body size and reject oversized payloads with `413 Content Too Large`. | **Required** |
| 2.2 | Base64-encoded binary payloads and Blob references include a declared content-type that is validated server-side before decoding. | **Required** |
| 2.3 | Tool arguments received from the model are validated against an explicit schema before being forwarded to external APIs or shell commands. | **Required** |
| 2.4 | Prompt injection mitigations are in place (e.g., a Gemini-as-Judge or Model Armor plugin) for agents that process user-supplied or tool-returned text. | **Recommended** |
| 2.5 | Auth-related ADK events (`is_pending_auth_event`, `get_function_call_auth_config`) verify that the function name matches an expected allowlist before honoring the event. | **Required** |

---

## 3. Unsafe Code & Command Execution

!!! danger "Never run in production"
    The validation utilities `validate_snippets` (uses `exec`) and
    `validate_links` (uses `subprocess.run` + `requests`) are designed for
    **offline CI pipelines only**.  Do not import or invoke them inside a
    running agent server.

| # | Item | Priority |
|---|------|----------|
| 3.1 | `exec`-based snippet validation is gated behind a CI-only flag and cannot be triggered by any network request. | **Required** |
| 3.2 | `subprocess.run` calls derived from documentation or user content are replaced with a sandboxed execution environment (e.g., Vertex Code Interpreter Extension, gVisor). | **Required** |
| 3.3 | The agent's code execution tool uses one of the [recommended sandboxing options](index.md#sandboxed-code-execution): Vertex Gemini Enterprise code execution, the ADK Code Executor tool, or a custom hermetic sandbox. | **Required** |

---

## 4. External HTTP Calls (SSRF & Resource Exhaustion)

| # | Item | Priority |
|---|------|----------|
| 4.1 | All outbound HTTP calls (weather APIs, market-data APIs, link validation) have an explicit connect + read timeout (e.g., 5 s / 30 s). | **Required** |
| 4.2 | Response sizes are capped (e.g., `max_bytes=5_000_000`) before being read into memory. | **Required** |
| 4.3 | Ticker symbols, city names, and other model-supplied URL parameters are validated against an allowlist or a strict format before being embedded in outbound requests. | **Required** |
| 4.4 | `validate_links` URL scanning is restricted to a known-safe domain allowlist and is never pointed at internal network addresses. | **Required** |
| 4.5 | Repeated calls for the same key (e.g., same city or ticker) are short-circuit cached with a TTL appropriate to the data's freshness requirement. | **Recommended** |
| 4.6 | Per-agent and per-user rate limits are enforced on tool calls that proxy to paid external APIs. | **Recommended** |

---

## 5. Endpoint & Transport Security

| # | Item | Priority |
|---|------|----------|
| 5.1 | The `adk api_server` is **never** bound to `0.0.0.0` without an authenticating reverse proxy (e.g., Cloud Run IAP, NGINX + mTLS) in front of it. | **Required** |
| 5.2 | SSE and WebSocket endpoints enforce a maximum number of concurrent connections per process and return `503` when the limit is reached. | **Required** |
| 5.3 | Idle WebSocket / SSE connections are reaped after a configurable heartbeat timeout (e.g., 60 s with no activity). | **Recommended** |
| 5.4 | All traffic between the client and the ADK server uses TLS 1.2 or higher. | **Required** |

---

## 6. Session & State Management

| # | Item | Priority |
|---|------|----------|
| 6.1 | `LiveRequestQueue` and session state are backed by an external store (e.g., Redis, Firestore, or a dedicated session service) when running more than one replica. | **Required** (multi-replica) |
| 6.2 | `InMemoryArtifactService` is replaced with an external object store (e.g., Cloud Storage) for deployments that must survive process restarts. | **Required** (stateful workloads) |
| 6.3 | Per-session artifact count and individual artifact size are bounded to prevent unbounded RAM growth. | **Recommended** |
| 6.4 | Session IDs are rotated after authentication to prevent session fixation. | **Recommended** |

---

## 7. Configuration & Secret Management

| # | Item | Priority |
|---|------|----------|
| 7.1 | Instruction files and environment-definition files loaded by `util.load_instruction_from_file` / `integrations.define_env` are read-only to the agent process user. | **Required** |
| 7.2 | API keys, OAuth client secrets, and service-account credentials are sourced from Secret Manager or equivalent (not from environment variables embedded in container images). | **Required** |
| 7.3 | Instruction files loaded at startup are cached in memory; repeated disk reads per invocation are avoided in high-QPS deployments. | **Recommended** |

---

## 8. Logging, Observability & Data Leakage

| # | Item | Priority |
|---|------|----------|
| 8.1 | Logging uses a structured logger (e.g., Python `logging`, `pino`, `zap`) instead of ad-hoc `print` calls so that log levels and output sinks can be controlled at runtime. | **Required** |
| 8.2 | `AuthConfig` objects, OAuth tokens, and raw user PII are redacted before log records are emitted. | **Required** |
| 8.3 | Log volume in hot paths (event streaming loops) is throttled to `DEBUG` level or sampled to avoid becoming a CPU / I/O bottleneck. | **Recommended** |
| 8.4 | Distributed tracing (Cloud Trace, OpenTelemetry) is enabled so that slow tool calls and cascading agent invocations can be diagnosed. See [Observability](../observability/index.md). | **Recommended** |

---

## 9. Scalability & Resource Limits

| # | Item | Priority |
|---|------|----------|
| 9.1 | The LLM backend (Vertex AI, Gemini API) is accessed through a client that respects quota limits and applies exponential-backoff retries. | **Required** |
| 9.2 | Callback chains (before/after model, before/after tool, human-in-the-loop, routing) are reviewed for fan-out: nested `call_agent_async` calls must be bounded to prevent runaway model invocation counts. | **Required** |
| 9.3 | Blocking I/O in CLI helpers (e.g., `get_user_input` wrapping `input()`) is served from a **bounded** thread pool, not an unbounded `run_in_executor`. | **Recommended** |
| 9.4 | `process_document` and other large-document ingestion paths enforce a maximum document size and delegate storage to an external vector store or object store rather than accumulating in `InMemoryArtifactService`. | **Recommended** |
| 9.5 | Load tests have been run against the SSE / WebSocket endpoints at the expected peak connection count to validate that the event loop does not saturate. | **Recommended** |

---

## 10. Pre-Launch Review

Before going live, confirm the following:

- [ ] All **Required** items above are checked off.
- [ ] A threat-model review has been conducted for the specific tools and external APIs the agent uses.
- [ ] Security scanning (SAST, dependency audit) has been run against the agent codebase.
- [ ] The agent has been evaluated with adversarial prompts; see [Evaluate Agents](../evaluate/index.md).
- [ ] Runbooks exist for common failure modes (quota exhaustion, credential rotation, session store failover).
- [ ] On-call alerting is configured for error-rate and latency SLOs.

---

## Related Pages

- [Safety and Security for AI Agents](index.md)
- [Deploy to Cloud Run](../deploy/cloud-run.md)
- [Deploy to GKE](../deploy/gke.md)
- [Evaluate Agents](../evaluate/index.md)
- [Observability](../observability/index.md)