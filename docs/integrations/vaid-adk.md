---
catalog_title: VAID
catalog_description: Verifies an agent's delegation chain before it runs or calls a tool
catalog_icon: /integrations/assets/vaid-adk.png
---

# VAID verification plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[VAID](https://github.com/solara-associates/vaid) is a signed, attenuable
identity credential for agents. The `vaid-adk` package is a `BasePlugin` that
verifies a presented VAID's signature, expiry, delegation-chain attenuation
and revocation status before an agent runs, before it is delegated to as a
sub-agent, and before it calls a tool. ADK has no built-in mechanism for this
(google/adk-python#4992, google/adk-python#6551); `vaid-adk` adds it for an
agent that already carries a VAID, using only `vaid_mint`'s existing
signature, chain and revocation primitives. It denies fail-closed whenever
any of that cannot be positively confirmed.

The plugin verifies and authorizes only. It does not mint credentials:
issuing a root VAID, or an attenuated child VAID for a sub-agent, is ordinary
`vaid_mint` usage (`MintService.mint_root` / `mint_child`) done by the caller
before the plugin is wired in.

## Use cases

- **Gate delegation to a sub-agent**: Deny a sub-agent's `run_async` before
  it executes, including when it is reached through ADK's native delegation
  (`transfer_to_agent` / `sub_agents`), if its VAID does not verify.
- **Gate individual tool calls**: Map each tool name to the capability and
  resource it requires, and deny the call before the tool runs if the
  calling agent's VAID does not cover it.
- **Enforce attenuation across delegation**: Confirm a sub-agent's VAID is a
  properly attenuated child of a trusted root, so a worker scoped to
  `data.orders`/`read` cannot reach a tool that needs `data.payments`/`write`.

## Prerequisites

- Python >= 3.10
- [ADK](https://adk.dev) >= 2.0 (verified against `google-adk` 2.11.0)
- An agent that already carries a VAID, or a way to mint one with
  [`vaid-mint`](https://github.com/solara-associates/vaid/tree/main/python/vaid-mint)
- A `RevocationCheck` backed by your own revoked-credential store for
  production use; see [Revocation](#revocation) below

## Installation

The `vaid-adk` package is not published on PyPI. Install it from source, from
the `vaid` repository's `python/vaid-adk` subdirectory:

```bash
pip install "git+https://github.com/solara-associates/vaid#subdirectory=python/vaid-adk"
```

This also installs `vaid-mint` and `google-adk` as dependencies.

## Use with agent

This example mints a root VAID for a coordinator agent, mints an attenuated
child VAID for a worker sub-agent (scope `data.orders` only, capability
`read` only, narrower than the coordinator's `data.orders` + `data.payments`,
`read` + `write`), registers both presentations with `VaidAuthPlugin`, and
runs them through a real ADK `Runner`. It is offline: the two agents are
plain `BaseAgent` subclasses that act without an LLM, so the example proves
the plugin's enforcement through the genuine ADK extension points rather than
a mock of them.

```python
import asyncio
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as gtypes

from vaid_mint import InMemoryAudit, MintService, ReferenceIssuer, VaidSeed
from vaid_mint.chain import SingleKernelKey
from vaid_mint.mint_types import MintPop, build_mint_pop_payload
from vaid_mint.revocation import InMemoryRevocationList
from vaid_pop import canonical_request_signing_bytes

from vaid_adk import ToolAuthorization, VaidAuthPlugin, VaidPresentation

APP_NAME = "vaid-adk-example"
USER_ID = "demo-user"


class ToolCallingAgent(BaseAgent):
    """A worker agent that attempts two tool calls through the real plugin
    manager: lookup_order (within its attenuated scope) and issue_refund
    (outside it)."""

    async def _run_async_impl(self, ctx: InvocationContext):
        for tool_name, resource in (
            ("lookup_order", "data.orders"),
            ("issue_refund", "data.payments"),
        ):
            denial = await ctx.plugin_manager.run_before_tool_callback(
                tool=_FakeTool(tool_name),
                tool_args={"resource": resource},
                tool_context=_FakeToolContext(self.name),
            )
            outcome = "ALLOWED" if denial is None else f"DENIED ({denial['code']})"
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                content=gtypes.Content(
                    role="model", parts=[gtypes.Part(text=f"{tool_name}: {outcome}")]
                ),
            )


class _FakeTool:
    """A minimal stand-in carrying only what before_tool_callback reads:
    .name. Avoids a real FunctionTool + LLM round trip for this example."""

    def __init__(self, name: str) -> None:
        self.name = name


class _FakeToolContext:
    """A minimal stand-in carrying only what before_tool_callback reads:
    .agent_name, the identity of the agent making the call."""

    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name


class CoordinatorAgent(BaseAgent):
    """Drives ADK's native in-process delegation (sub_agent.run_async)."""

    async def _run_async_impl(self, ctx: InvocationContext):
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=gtypes.Content(role="model", parts=[gtypes.Part(text="delegating to worker")]),
        )
        for sub in self.sub_agents:
            async for event in sub.run_async(ctx):
                yield event


async def main() -> None:
    # 1. Mint a root VAID for the coordinator, then an attenuated child for
    #    the worker. Ordinary vaid_mint usage, no ADK involved yet.
    kernel_key = Ed25519PrivateKey.generate()
    issuer = ReferenceIssuer.from_seed(
        kernel_key.private_bytes_raw(), vaid_ttl_hours=1, trust_domain="vaid.example"
    )
    revocation = InMemoryRevocationList.assume_nothing_revoked()
    mint = MintService(issuer, InMemoryAudit())

    root = mint.mint_root(
        VaidSeed(
            agent_class="coordinator",
            version="1.0.0",
            tenant_id="acme",
            scope_boundary=["data.orders", "data.payments"],
            capability_set=["read", "write"],
        )
    )

    worker_key = Ed25519PrivateKey.generate()
    worker_public = worker_key.public_key().public_bytes_raw()
    worker_seed = VaidSeed(
        agent_class="worker",
        version="1.0.0",
        tenant_id="acme",
        parent_vaid=root["vaid_id"],
        scope_boundary=["data.orders"],  # attenuated: no data.payments
        capability_set=["read"],  # attenuated: no write
        public_key_der=worker_public,
    )
    pop_nonce = "example-nonce-1"
    pop_issued_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pop_payload = build_mint_pop_payload(
        worker_seed, public_key_der=worker_public, nonce=pop_nonce, issued_at=pop_issued_at
    )
    pop = MintPop(
        nonce=pop_nonce,
        issued_at=pop_issued_at,
        signature=worker_key.sign(canonical_request_signing_bytes(pop_payload)),
    )
    worker_child = mint.mint_child(worker_seed, root, pop).vaid

    # 2. Wire the plugin: one trusted kernel key, a revocation check, and the
    #    explicit tool -> capability map. The revocation store here vouches
    #    for everything, which is fine for this offline demo and wrong for
    #    production; see "Revocation" below.
    plugin = VaidAuthPlugin(
        keys=SingleKernelKey(issuer.kernel_public_key()),
        revocation=revocation,
        tool_authorizations={
            "lookup_order": ToolAuthorization(capability="read", resource="data.orders"),
            "issue_refund": ToolAuthorization(capability="write", resource="data.payments"),
        },
    )
    plugin.register("coordinator", VaidPresentation(leaf=root))
    plugin.register("worker", VaidPresentation(leaf=worker_child, chain=(root,)))

    # 3. Build the agents and run through a real ADK Runner.
    worker = ToolCallingAgent(name="worker")
    coordinator = CoordinatorAgent(name="coordinator", sub_agents=[worker])

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id="s1"
    )
    runner = Runner(
        app_name=APP_NAME,
        agent=coordinator,
        session_service=session_service,
        plugins=[plugin],
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id="s1",
        new_message=gtypes.Content(role="user", parts=[gtypes.Part(text="go")]),
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if text:
                print(f"[{event.author}] {text}")


if __name__ == "__main__":
    asyncio.run(main())
```

Output:

```text
[coordinator] delegating to worker
[worker] lookup_order: ALLOWED
[worker] issue_refund: DENIED (out_of_scope)
```

The tool call `lookup_order` is within the worker's attenuated
`data.orders`/`read` bounds. The call `issue_refund` needs
`data.payments`/`write`, which the worker's VAID never held, so the plugin
denies it before the tool runs. A tool with
no entry in `tool_authorizations` is denied the same way, never allowed by
omission, and an agent with no registered presentation is denied too: it is
indistinguishable from one that was never given an identity.

## Revocation

The `VaidAuthPlugin` constructor takes `revocation` as a required argument
with no default:

```python
from vaid_adk import VaidAuthPlugin

plugin = VaidAuthPlugin(
    keys=keys,
    revocation=my_revocation_check,  # a RevocationCheck backed by your store
    tool_authorizations=tool_authorizations,
)
```

The example above passes `InMemoryRevocationList.assume_nothing_revoked()`
only because it has no production revocation store to call. That store is
non-durable and fails open after a restart: a VAID revoked before the
restart verifies clean again. That is acceptable for a demo and wrong for
anything that must survive one.

For production, inject a durable `RevocationCheck` backed by your own
revoked-credential store. `vaid_mint.revocation.RevocationCheck` is a
`Protocol` with one method, `check_lineage(lineage: list[str]) ->
RevocationStatus`, where `RevocationStatus` is three-valued:
`NOT_REVOKED`, `REVOKED`, or `UNAVAILABLE`. Return `UNAVAILABLE` whenever
your store cannot be reached; the plugin already denies on that outcome; it
never treats "could not determine" as "not revoked".

## Additional resources

- [VAID Repository](https://github.com/solara-associates/vaid)
- [vaid-adk source](https://github.com/solara-associates/vaid/tree/main/python/vaid-adk)
- [vaid-mint source](https://github.com/solara-associates/vaid/tree/main/python/vaid-mint)
