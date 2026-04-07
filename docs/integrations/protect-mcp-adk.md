---
catalog_title: protect-mcp-adk
catalog_description: Ed25519 receipt signing for agent tool call governance and audit
catalog_tags: ["resilience"]
---

# Receipt signing for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[protect-mcp-adk](https://pypi.org/project/protect-mcp-adk/) adds Ed25519 cryptographic receipt signing to Google ADK agents. Every tool call produces a signed, chain-linked receipt that is independently verifiable offline.

## Why receipt signing?

When ADK agents run in production, compliance and security teams need verifiable proof of agent behavior. Centralized logs can be tampered with. Cryptographic receipts provide:

*   **Tamper evidence:** Ed25519 signatures ensure receipts cannot be modified after signing.
*   **Privacy:** Tool inputs and outputs are SHA-256 hashed, not stored raw. The receipt proves what happened without exposing what was said.
*   **Chain integrity:** Each receipt links to the previous via `previousReceiptHash`. If any receipt is modified or removed, the chain breaks.
*   **Offline verification:** Receipts verify without contacting any server, using a deterministic CLI verifier.
*   **Interoperability:** The receipt format follows an [IETF Internet-Draft](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/). Four independent implementations produce interoperable receipts.

## Getting Started

### 1. Install

```bash
pip install protect-mcp-adk
```

### 2. Add the plugin to your agent

```python
from google.adk import Agent
from google.adk.tools import FunctionTool
from protect_mcp_adk import ReceiptPlugin, ReceiptSigner

# Generate signing keys (or load from file)
signer = ReceiptSigner.generate()

# Create the plugin
receipt_plugin = ReceiptPlugin(
    signer,
    auto_export_path="receipts.jsonl",
)

# Add to your agent
agent = Agent(
    model="gemini-2.0-flash",
    name="my_agent",
    tools=[FunctionTool(my_tool)],
    plugins=[receipt_plugin],
)
```

### 3. Verify receipts after execution

```bash
npx @veritasacta/verify@0.2.5 receipts.jsonl --key <public-key-hex>
# Exit 0 = all valid
# Exit 1 = tampered (signature mismatch)
# Exit 2 = malformed input
```

## How it works

The plugin hooks into ADK's `BasePlugin` interface:

| Callback | When | What it signs |
|----------|------|---------------|
| `after_tool_callback` | After every tool execution | Tool name, input hash, output hash, decision |
| `on_tool_error_callback` | On tool execution error | Tool name, input hash, error reason |
| `before_tool_callback` | Before tool execution | Override for policy evaluation |

Each receipt follows the IETF draft envelope format:

```json
{
  "payload": {
    "type": "protectmcp:decision",
    "spec": "draft-farley-acta-signed-receipts-01",
    "tool_name": "web_search",
    "tool_input_hash": "sha256:ff7e27...",
    "decision": "allow",
    "output_hash": "sha256:a3f8c9...",
    "session_id": "sess_a1b2c3",
    "sequence": 1,
    "previousReceiptHash": null,
    "agent_name": "my_agent"
  },
  "signature": {
    "alg": "EdDSA",
    "kid": "sb:adk:de073ae6",
    "sig": "3da316..."
  }
}
```

## Key management

```python
# Generate a new keypair
signer = ReceiptSigner.generate()

# Save for reuse across sessions
signer.save_key("keys/agent.json")

# Load existing keys
signer = ReceiptSigner.from_key_file("keys/agent.json")
```

## Export and audit

```python
# After agent execution
print(f"Receipts signed: {receipt_plugin.receipt_count}")
receipt_plugin.export_receipts("audit-bundle.jsonl")
print(receipt_plugin.get_verification_command())
```

## Algorithm note

The plugin uses Ed25519 (RFC 8032) with JCS canonicalization (RFC 8785). The receipt envelope's `signature.alg` field supports algorithm negotiation for environments requiring post-quantum signatures (ML-DSA-65 / FIPS 204).

## Resources

*   [protect-mcp-adk on PyPI](https://pypi.org/project/protect-mcp-adk/)
*   [IETF Draft: Signed Receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)
*   [Verifier](https://npmjs.com/package/@veritasacta/verify) (Apache-2.0, offline)
*   [Source](https://github.com/scopeblind/scopeblind-gateway)
*   [Veritas Acta Protocol](https://veritasacta.com)
