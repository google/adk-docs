---
catalog_title: Trustabl
catalog_description: Find and fix reliability and safety gaps in ADK agent code
catalog_icon: /integrations/assets/trustabl.png
catalog_tags: ["mcp", "code"]
---

# Trustabl static analysis for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Trustabl](https://trustabl.ai) is an Apache-2.0 static analyzer for AI-agent
codebases. It reads an ADK project, builds an inventory of the agents, tools,
sub-agents and hosted tools it declares, then checks each one against a
versioned rule pack. It reports what is wrong, where, and how to fix it.

Analysis is deterministic and runs entirely on your machine: no model call, no
account, no network beyond fetching the rule pack, and your source is never
uploaded. Rules are versioned separately from the engine and resolved at scan
time, so new detections arrive without upgrading the binary.

For ADK specifically, Trustabl understands `LlmAgent` (and the `Agent` alias),
`SequentialAgent`, `ParallelAgent`, `LoopAgent`, `FunctionTool` wrapping, the
built-in hosted tools, and `sub_agents` relationships between them.

## Use cases

- **Catch unsafe tools before a model can reach them**: Find ADK tools that
  shell out to the OS, call `eval`/`exec`/`compile`, or fetch a URL built from a
  tool argument. Because the model chooses the arguments, a prompt-injected
  conversation reaches whatever those tools can reach.
- **Fix the tool contracts a model depends on**: Find `FunctionTool`-wrapped
  functions with no docstring, a description too short to guide selection, or an
  ambiguous name. ADK uses the docstring as the tool description, so a missing
  one leaves the model guessing when to call it.
- **Find the failure modes that only appear in production**: Network calls with
  no timeout, which hang the whole agent loop, and tools that print to stdout,
  which corrupts the protocol stream when the agent runs over stdio.
- **Gate a pull request on agent quality**: Run the same scan in CI and fail the
  build above a severity threshold, so a regression in an agent or tool is
  caught in review rather than after deployment.

## Prerequisites

- An ADK project in Python (`google-adk`) or TypeScript (`@google/adk`)
- One of: Docker, Homebrew, Scoop, or a downloaded binary. No Python or Node
  toolchain is required to run the scanner itself.
- No account or API key.

## Installation

Run it without installing anything:

```bash
docker run --rm -v "$PWD:/repo" ghcr.io/trustabl/agent-reliability-analyzer:latest scan /repo
```

Or install the CLI:

```bash
brew install trustabl/tap/trustabl                                  # macOS / Linux
scoop bucket add trustabl https://github.com/trustabl/scoop-bucket   # Windows
scoop install trustabl
```

## Use with agent

Point Trustabl at the directory holding your ADK agent. It reads the code; it
does not run it.

```bash
trustabl scan .
```

A scan prints the inventory it found, then each finding with its severity, the
exact file and line, an explanation, and a suggested fix. Read the inventory
first: if the agent and tool counts look wrong, the scan is pointed at the wrong
directory and the findings are not yet worth reading.

To gate CI on the result, use the exit code:

```bash
trustabl scan . --strict        # non-zero exit on any finding of low or above
```

Machine-readable output for a dashboard or a code-scanning upload:

```bash
trustabl scan . --format json -o report.json
trustabl scan . --sarif-out results.sarif
```

Trustabl also ships an MCP server, so an assistant that speaks MCP can run the
scan as a tool call while you work:

```json
{
  "mcpServers": {
    "trustabl": { "command": "trustabl", "args": ["mcp"] }
  }
}
```

## What it checks in ADK code

A sample of the ADK rules, not the full set:

Rule | What it catches
---- | ---------------
`ADK-001` | A `FunctionTool`-wrapped function with no docstring, so the model has no description to select on
`ADK-003` | A network call in a tool with no timeout, which hangs the agent loop rather than failing
`ADK-007` | An ambiguous tool name the model cannot reliably choose between
`ADK-009` | A tool that prints to stdout, corrupting the protocol stream when the agent runs over stdio
`ADK-010` | A tool that spawns a subprocess, exposing process execution to a model-chosen argument
`ADK-011` | A tool that calls `eval`, `exec` or `compile`
`ADK-012` | A tool that fetches a URL built from a tool argument rather than a fixed literal
`ADK-201` | ADK code with no agent-guidance document for a coding assistant to follow
`ADK-202` | An ADK project that wires no observability, so a failing agent leaves no trace to debug

Python coverage is complete across agents, tools and repository scope.
TypeScript coverage is narrower: tool descriptions, `eval`/`new Function`, SSRF,
and agent descriptions.

## Available tools

Exposed by the bundled MCP server.

Tool | Description
---- | -----------
`scan` | Scan a local directory or a GitHub repository URL and return the structured result
`version` | Report the build version, commit and build date

## Additional resources

- [Documentation](https://trustabl.ai/docs)
- [GitHub repository](https://github.com/trustabl/agent-reliability-analyzer)
- [Detection rule packs](https://github.com/trustabl/agent-reliability-rules)
- [Coverage by SDK and language](https://github.com/trustabl/agent-reliability-analyzer/blob/main/COVERAGE.md)
- [Report an issue](https://github.com/trustabl/agent-reliability-analyzer/issues)
