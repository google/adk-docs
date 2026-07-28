# adk-bot-review skill

Usage guide for the `adk-bot-review` skill.

**What it does:** Reviews adk-bot-authored pull requests for technical accuracy
against ADK source code, checks PR state and formatting, and applies ADK docs
style conventions.

**Audience:** Maintainers.

## How to invoke

Ask the agent naturally, for example:

- "Review bot PR #<n>"
- "Check bot changes for issue #<n>"
- "Verify bot issue #<n>"

## What you get back

- Findings ordered blockers first, then required edits, then nits.
- A recommended outcome for the bot PR(s).

## Follow-up actions

- Close the bot PR(s).
- Approve as-is.
- Edit in place, then approve.
- Open a new consolidating PR and close the superseded bot PR(s).
