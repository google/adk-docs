---
name: api-ref-audit
description: Audits whether ADK API reference docs and version-pinned strings are up to date across all language SDKs. Compares in-repo versions against upstream releases and package registries, then reports what needs bumping and which process to follow, and emits an executable plan only when asked. Triggers on "audit API reference", "check API ref docs", "are API docs up to date", "bump API doc versions", "check SDK doc versions".
---

# ADK API reference doc auditor (api-ref-audit)

This skill audits the API reference documentation in the
[adk-docs](https://github.com/google/adk-docs) repository across every language
SDK and reports what is out of date. It is a **reporting and guidance** skill:
it detects drift, recommends the correct per-surface release process, and emits
an executable plan only when the user explicitly asks. It does **not** edit
files, run generators, or open PRs by default.

The audit covers three kinds of drift:

1. **Generated API reference docs** under `docs/api-reference/` that lag behind
   the latest SDK release.
2. **Hardcoded version strings** in prose and examples (dependency coordinates,
   `pom.xml` versions) that must be bumped with each Java/Kotlin release.
3. **Code-sample drift** (light flagging only): samples that reference pinned
   versions or obviously deprecated APIs. Deep sample verification is out of
   scope of this skill.

> [!IMPORTANT]
> The maps below are **hints, not ground truth**. File layouts, script paths,
> and team processes change. At each step, verify the path or marker exists and
> re-derive it if a lookup fails, rather than trusting the table blindly.

## Version map (in-repo version vs. upstream truth)

For each surface, read the in-repo version from the file listed, then compare it
against the latest upstream release and package registry.

| Surface | In-repo version marker | Upstream repo | Package registry |
| --- | --- | --- | --- |
| Python API | `docs/api-reference/python/_static/documentation_options.js` (`VERSION:`) | `google/adk-python` | PyPI `google-adk` |
| Python CLI | `docs/api-reference/cli/_static/documentation_options.js` (`VERSION:`) and `docs/api-reference/cli/index.html` ("ADK X.Y.Z") | `google/adk-python` | PyPI `google-adk` |
| Python REST API | `docs/api-reference/rest/openapi.json` (`info.version`) | `google/adk-python` | PyPI `google-adk` |
| Python Agent Config | no version marker; diff the type set in `agentconfig/index.html` against upstream `AgentConfig.json` | `google/adk-python` (same release as Python API/CLI/REST) | n/a |
| TypeScript | `docs/api-reference/typescript/variables/version.html` (the `version` const) | `google/adk-js` (monorepo; see note) | npm `@google/adk` (authoritative) |
| Go | external, hosted on `pkg.go.dev`; verify links in `docs/api-reference/index.md` | `google/adk-go` | `pkg.go.dev` |
| Java | `docs/api-reference/java/index.html` (`<title>` "Maven Parent POM X.Y.Z API") | `google/adk-java` (authoritative) | Maven Central `com.google.adk:google-adk` (lags; cross-check only) |
| Kotlin | `docs/api-reference/kotlin/index.html` (version string near the header) | `google/adk-kotlin` (authoritative) | Maven Central `com.google.adk:google-adk-kotlin-core` (lags; cross-check only) |

Notes:

- Python API, CLI, and REST all track the **same** `adk-python` release, so they
  usually move together. Flag it when they diverge.
- Python Agent Config has no version field. Parse the **keys of the `$defs`
  object** (plus top-level `oneOf` variants) from the upstream
  `AgentConfig.json` at the target tag, e.g. `jq '."$defs" | keys'`. Do not
  substring-grep for `*Config`: that mixes property names (camelCase, e.g.
  `imageConfig`) with type names (PascalCase, e.g. `ImageConfig`) and produces
  false drift. Check each `$defs` key as a whole word against
  `agentconfig/index.html`; a key present upstream but missing in the page (or
  vice versa) is drift.
- TypeScript: use npm `@google/adk` `dist-tags.latest` as the authoritative
  version. adk-js is a monorepo with package-prefixed tags (e.g. `main-v1.4.0`,
  `integrations-v1.4.0`), so `gh ... releases/latest` can return an unrelated
  package. The in-repo const and npm share one scheme (`0.5.0` -> `1.4.0`), so a
  large gap means the docs are genuinely stale, not mis-versioned.
- Go docs are not built into this repo. Confirm the release version and that the
  `index.md` links point at the correct major versions (e.g. v2.x and v1.x). Go
  versions are also pinned in `examples/go/go.mod` / `go.sum` and appear as
  `/adk/v2` import paths in prose (e.g. `docs/events/index.md`, `docs/2.0/`), so
  check those too.

## Hardcoded version references

These version-pinned strings are intentional and useful: they show developers
the exact dependency versions to use. The audit's job is to keep them current,
not remove them. They drift with each Java/Kotlin release and are bumped in a
separate PR (see the process map). Discover current occurrences by grep; do not
trust the file list alone, as new pages might appear over time.

- **Grep targets**:
    - `com.google.adk:google-adk` and `com.google.adk:google-adk-kotlin` across
      `docs/**/*.md`
    - `<google-adk.version>` across `docs/**/*.md` and `examples/java/**/pom.xml`
    - bare `google-adk>=X.Y.Z` pins in integration pages (report only; these are
      minimum-version pins, not doc-version bumps)
- **Known files that carry these (verify, do not assume complete)**:
    - `docs/get-started/installation.md`
    - `docs/get-started/java.md`
    - `docs/get-started/kotlin.md`
    - `docs/get-started/streaming/quickstart-streaming-java.md`
    - `docs/deploy/cloud-run.md`
    - `docs/agents/models/litert-lm.md`
    - `docs/integrations/firestore-session-service.md`
    - `examples/java/**/pom.xml`

- **Never flag or bump language support tags.** Versions that are inside of
  `language-support-tag` spans (e.g. `<span class="lst-python">Python
  v1.32.0</span>`) mark the release a feature was *introduced* in, not the
  latest published version. Leave them untouched; bumping them misrepresents
  when the feature became available.

## Per-surface process map (owner, tooling, steps)

Treat each entry as a starting hint. Before recommending it, confirm the script
still exists and inspect the most recent matching bump PR to confirm the current
process.

- **Python API**: self-serve. Run `bash tools/python-api-docs/generate.sh
  <version>`, then open a PR (the script injects the Google Analytics tag via
  Sphinx).
- **Python CLI**: self-serve. Run `bash tools/python-cli-docs/generate.sh
  <version>`, then open a PR. The GA tag is injected via a Sphinx layout
  template in the script.
- **Python REST API**: self-serve. Run `bash
  tools/python-rest-api-docs/generate.sh <version>`, then open a PR. GA tag is
  baked into the generated `index.html`.
- **Python Agent Config**: regenerated from the adk-python schema with
  `json-schema-for-humans`; no `tools/` generate script exists yet, so treat the
  update as manual.
- **TypeScript**: the adk-js team opens a PR in this repo with the built TypeDoc
  assets. Not self-serve here.
- **Java**: two separate PRs per release. The adk-java team pushes the built
  Javadoc assets (title `chore: update ADK Java doc to version <X>`); the docs
  maintainer bumps the hardcoded dependency versions and `pom.xml` values (title
  `Update ADK Java dependency versions to <X>`). The two can lag each other; the
  assets PR is not self-serve, the dependency bump is.
- **Kotlin**: self-serve, one PR. Run `bash tools/kotlin-api-docs/generate.sh
  <version>`, then open a PR that bundles the generated assets and the hardcoded
  Kotlin refs (`installation.md`, `get-started/kotlin.md`, `litert-lm.md`). The
  GA tag is auto-injected into every HTML file.

### Verify the process

- Confirm each referenced script exists under `tools/` before recommending it.
- Inspect the last matching bump to confirm the real, current process and the
  files it touched, for example:
    - `gh pr list --repo google/adk-docs --state merged --search "Kotlin"`
    - `gh pr list --repo google/adk-docs --state merged --search "CLI reference"`
    - `gh pr list --repo google/adk-docs --state merged --search "Java"`

## Audit workflow

### Step 1: Read in-repo versions

For every surface in the version map, read the marker file and record the
current version. Use `grep`/`Read` for the JS and HTML markers and parse
`info.version` from `rest/openapi.json`. If a marker path does not resolve,
re-derive it (search the generated output) and note the discrepancy.

### Step 2: Fetch upstream releases and registry versions

For each SDK, get the latest release and the latest published package:

- GitHub latest release and tags:
    - `gh api repos/google/adk-python/releases/latest --jq .tag_name`
    - Repeat for `adk-go`, `adk-kotlin`, `adk-java`.
    - For `adk-js`, do not use `releases/latest` (monorepo tags are
      package-prefixed, e.g. `main-v1.4.0`); use npm `@google/adk` as the source
      of truth.
- Package registries:
    - PyPI: fetch `https://pypi.org/pypi/google-adk/json` and read `info.version`.
    - npm: fetch `https://registry.npmjs.org/@google/adk` and read
      `dist-tags.latest`.
    - Maven Central: query
      `https://search.maven.org/solrsearch/select?q=g:com.google.adk+AND+a:google-adk&rows=1&wt=json`
      and read `latestVersion` (use `a:google-adk-kotlin-core` for Kotlin).
- **For Java and Kotlin, treat the GitHub release/tag as authoritative.** The
  Maven Central search index frequently lags real releases (it has returned
  versions older than what is already shipped in this repo). Use the registry
  only as a cross-check, and when it disagrees with the GitHub tag, trust the
  tag and note the lag.
- Note when a GitHub tag and its registry version disagree (a release may be
  tagged but not yet published, or vice versa); report both.

### Step 3: Classify each surface

Mark each surface as one of:

- **Up to date**: in-repo version equals the latest upstream release.
- **Behind**: in-repo version is older than the latest release (report the gap,
  e.g. `2.3.0 -> 2.4.1`).
- **Unknown / manual**: upstream lookup failed, or a surface with no automatable
  check. Agent Config is not "unknown"; classify it via the type-set diff
  (Behind if types were added or removed upstream).

Call out the common case where Python API, CLI, and REST should share the same
`adk-python` version but do not.

For Agent Config, run the type-set diff described in the version map Notes to
decide Up to date vs. Behind.

### Step 4: Check hardcoded version references

Grep the targets in "Hardcoded version references" and compare each pinned
version to the latest Java and Kotlin releases. List every file and line that
needs a bump. Keep minimum-version pins (`google-adk>=X.Y.Z`) separate; only
flag them if they reference a version newer than what is released or are clearly
stale.

### Step 5: Light code-sample drift flag

Do a quick scan (not a deep audit): note samples with hardcoded model or package
versions, obviously deprecated imports, or patterns superseded by a new
release's changelog. Report these as hints and recommend a dedicated
sample-audit pass for deep verification. Do not attempt to rewrite samples here.

### Step 6: Verify Go links

Confirm `docs/api-reference/index.md` links point at the correct Go major
versions on `pkg.go.dev` and that the latest `adk-go` release is represented.
Also check the pinned versions in `examples/go/go.mod` / `go.sum` and the
`/adk/v2` import paths in prose (e.g. `docs/events/index.md`, `docs/2.0/`).

## Report format

Produce a Markdown report. Lead with a status table, then prioritized findings.

Status table (one row per surface):

| Surface | In-repo | Latest upstream | Status | Recommended action |
| --- | --- | --- | --- | --- |

Prioritized findings after the table. List only items that require action; do
not emit "no action" or "confirmed correct" lines anywhere, including inside an
otherwise-actionable finding. If a surface needs nothing, its table row already
says so.

- 🔴 **Out of date / broken**: a surface multiple releases behind, a
  broken/incorrect API-reference link, or version markers that disagree with
  each other (e.g. Python API/CLI/REST on different versions).
- 🟠 **Stale hardcoded versions**: `file:line` list of dependency coordinates and
  `pom.xml` values to bump, with old -> new.
- 🟡 **Sample-drift hints**: samples that likely need updating; recommend the
  deep sample-audit pass.

For each stale surface, name the **recommended process** from the process map
(self-serve script, wait on team, or manual) so the user knows how to proceed.

After the report, **stop**. Do not modify files, run generators, or open PRs
unless the user explicitly asks.

## Executable plan (only when asked)

When the user asks you to proceed, output concrete next actions per stale
surface:

- The exact command to run, when self-serve, for example:
    - `bash tools/python-cli-docs/generate.sh <new-version>`
    - `bash tools/python-rest-api-docs/generate.sh <new-version>`
    - `bash tools/kotlin-api-docs/generate.sh <new-version>`
- For team-owned surfaces (Java, TypeScript), state that the update is blocked
  on the owning team's asset PR and what to request or wait for.
- For hardcoded versions, the precise `file:line` edits (old -> new), including
  `examples/java/**/pom.xml`.
- Which surfaces move together (Python API + CLI + REST on one `adk-python`
  version) so they are bumped in one coordinated pass.
- A PR description per stale surface, following the repo convention:
    - a short bullet summary of what changed
    - `Rendered page:` <preview link, where applicable>
    - upstream release link and version
- A final note telling the user how to proceed: self-run the commands, wait on
  the owning team, or have the agent execute the plan.

### PR title conventions

Match the established titles so history stays searchable:

- Python API: `Update API reference docs for ADK Python <X.Y.Z>`
- Python CLI: `Update CLI reference docs for ADK Python <X.Y.Z>`
- Python REST API: `Update REST API reference docs for ADK Python <X.Y.Z>`
- Java dependency bump: `Update ADK Java dependency versions to <X.Y.Z>`
- Kotlin: `Update ADK Kotlin to <X.Y.Z>`

## Style rules to bake in

- Report versions precisely as `old -> new`; never guess a version you did not
  read from a marker or fetch from upstream.
- Do not invent links; use only markers you read and releases you fetched.
- No em dashes or verbose AI-generated content.
- The canonical source repositories are listed in
  `docs/community/contributing-guide.md`.
