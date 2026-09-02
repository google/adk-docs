---
catalog_title: Agent Threat Rules (ATR)
catalog_description: Open detection rules that block prompt injection and tool-argument attacks in the ADK Runner
catalog_icon: /integrations/assets/atr-guardrail.png
---

# Agent Threat Rules (ATR) guardrail plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Agent Threat Rules
(ATR)](https://github.com/Agent-Threat-Rule/agent-threat-rules) is an open,
MIT-licensed detection ruleset for AI-agent threats such as prompt injection,
instruction override, tool-argument tampering, and context exfiltration. The
[ADK plugin](https://github.com/eeee2345/adk-atr-guardrail) wires the ruleset
into the ADK Runner lifecycle through the in-process `pyatr` engine: it inspects
the user message, the assembled model request, and every tool call, then halts
or blocks them when a rule matches. Detection is deterministic pattern matching
— no model call, no network, and no API key.

## Use cases

- **Block prompt injection before the model**: Inspect the inbound user message
  and halt the run on a match, so a malicious prompt never reaches the model.
- **Defense in depth on model requests**: Inspect the assembled prompt
  (including injected tool output or retrieved context) and skip the model call
  when it still carries a threat.
- **Fail-closed tool calls**: Inspect tool-call arguments before execution and
  return an error instead of running a tool whose arguments match a rule.

## Prerequisites

- Python >= 3.10
- [ADK](https://adk.dev) >= 2.0.0
- No account, API key, or network connection — detection runs in-process via the
  open-source [`pyatr`](https://pypi.org/project/pyatr/) engine.

## Installation

```bash
pip install adk-atr-guardrail
```

## Use with agent

Register the plugin once on the `App`. It then applies to every agent, model
call, and tool call managed by the runner.

```python
--8<-- "examples/inline/python/integrations/atr-guardrail/001-use-with-agent.py"
```

`min_severity` sets the lowest rule severity that blocks (`info`, `low`,
`medium`, `high`, `critical`); the default `high` keeps benign traffic flowing.
The blocked path above is halted by the plugin before any model call, so it is
observable without model credentials. The benign path uses the model, so
configure your ADK model credentials as in the
[ADK quickstart](https://google.github.io/adk-docs/get-started/quickstart/).

## Resources

- [adk-atr-guardrail package](https://github.com/eeee2345/adk-atr-guardrail)
- [Agent Threat Rules ruleset](https://github.com/Agent-Threat-Rule/agent-threat-rules)
- [ATR documentation](https://agentthreatrule.org)
