# api-reference-audit skill

Usage guide for the `api-reference-audit` skill.

**What it does:** Audits whether the generated API reference docs in
`docs/api-reference/` and the hardcoded version strings across the docs are up
to date with the latest release of each language SDK. It reports what needs
bumping and which release process to follow, and changes nothing unless you ask.

**Audience:** Maintainers.

## How to invoke

Ask the agent naturally, for example:

- "Audit the API reference docs"
- "Are the API docs up to date?"
- "Check SDK doc versions"
- "Bump API doc versions"

## What you get back

- A status table with one row per surface (in-repo version, latest upstream,
  status, recommended action).
- Prioritized findings: 🔴 out of date or broken, 🟠 stale hardcoded versions
  (`file:line`, old -> new), 🟡 sample-drift hints.
- The recommended release process per stale surface.

## Follow-up actions

- Ask for the executable plan (commands, `file:line` edits, PR titles); it emits
  this only when you ask.
- Run the self-serve scripts (Python, Kotlin, TypeScript), wait on the owning
  team's PR (Java), or update manually (Agent Config).
- Have the agent execute the plan.
