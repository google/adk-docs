# integration-review skill

Usage guide for the `integration-review` skill.

**What it does:** Reviews an integration page or pull request under
`docs/integrations/` for correctness, structure, style, working code, valid
links, and catalog conventions.

**Audience:** Contributors and maintainers.

This is the integration-specific review in the ADK docs review family. It uses
the same risk tiers and the same 100-point scoring model as the general ADK docs
reviews, so an integration page can be compared against any other docs change.
Run it instead of the information architecture review when the primary file is
under `docs/integrations/`.

## How to invoke

Ask the agent naturally, for example:

- "Review integration PR #1959"
- "Run integration-review on `docs/integrations/bigquery.md`"
- "Review this integration"

## What you get back

- A **review score** out of 100: 100 minus 20 per ❌ Critical Risk item, 10 per
  🔴 High Risk, 2 per 🟡 Medium Risk, and 1 per 🟢 Low Risk.
- An overall assessment, summary reasoning, recommended action, and the change
  size in files and lines.
- All four risk sections printed in order (❌ Critical, 🔴 High, 🟡 Medium,
  🟢 Low), each finding tagged with `file:line` and a github.com link, and
  `None` under any section with no findings.
- A developer value and maturity assessment.
- A recommended decision: approve, request changes, or close PR.
- A top-level review response.
- Draft line-anchored comments, one per finding, prefixed
  `INTEGRATION REVIEW (Critical | High | Medium | Low):`.

Everything is a draft. Nothing is posted to GitHub and no files are changed
unless you explicitly ask.

## Follow-up actions

- Act on the decision: approve, request changes, or close the PR.
- Edit the drafted review response and comments before sending them to the
  author.
- Ask the agent to apply fixes (for example, "apply the fixes"); it edits files
  only when explicitly asked.
