# integration-review skill

Usage guide for the `integration-review` skill.

**What it does:** Reviews an integration page or pull request under
`docs/integrations/` for correctness, structure, style, working code, valid
links, and catalog conventions.

**Audience:** Contributors and maintainers.

## How to invoke

Ask the agent naturally, for example:

- "Review integration PR #1959"
- "Run integration-review on `docs/integrations/bigquery.md`"
- "Review this integration"

## What you get back

- A prioritized report with all four tiers listed (🔴 Critical, 🟠 Quality,
  🟡 Style, 🔵 Nits), each finding tagged with `file:line`.
- A developer value and maturity assessment.
- A recommended decision: approve, request changes, or close PR.
- A top-level review response.
- Draft line-anchored comments, one per finding.

Everything is a draft. Nothing is posted to GitHub and no files are changed
unless you explicitly ask.

## Follow-up actions

- Act on the decision: approve, request changes, or close the PR.
- Edit the drafted review response and comments before sending them to the
  author.
- Ask the agent to apply fixes (for example, "apply the fixes"); it edits files
  only when explicitly asked.
