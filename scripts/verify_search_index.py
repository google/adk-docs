# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Verifies the quality and scope of the built Pagefind index.

Run against a built site:

    python scripts/verify_search_index.py site

Three invariants are checked.

1. Scope, under-broad: the page count Pagefind recorded matches the number of
   built HTML files carrying ``data-pagefind-body``. This catches Pagefind
   silently dropping pages it was told to index -- an unparseable page, a
   crawler that stopped following part of the tree after an upgrade.

2. Scope, over-broad: no page that must never be searchable appears in the
   index. ``data-pagefind-body`` is applied in ``overrides/main.html`` inside
   an ``{% if page %}`` guard precisely so that ``404.html`` is excluded, and
   check 1 cannot see that guard fail (see ``check_scope``).

3. Tokenization: no fused language token survives. Pagefind concatenates
   adjacent inline elements without a separator, so the language badge and
   the tab label strip previously produced tokens such as ``ADKPython`` and
   ``PythonTypeScriptGoJava`` -- 219 of them across 193 of the 226 indexed
   pages, measured on the 2026-08-07 content set. Genuine identifiers that
   contain a language name, such as ``RxJava``, must not be flagged, so the
   pattern matches only runs of two or more language names spliced together.

``hooks/pagefind_index.py`` asserts invariant 1 at build time and additionally
guards the exclude selectors against a silent theme rename. This script is
deliberately standalone and re-derives everything from the built output, so it
can be pointed at a site directory that some other machine built -- a CI
artefact, a release tarball, a colleague's `site/` -- where the hook's
build-time assertions are no longer observable.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from pathlib import Path

# Two or more of these spliced directly together is always a fusion artefact,
# never a real identifier. "RxJava" and "pdfArtifactJava" contain a single
# language name and are correctly ignored.
#
# CONTRACT: any language that can appear in a language-support badge or a
# pymdownx.tabbed label strip must be listed in this alternation. A language
# added to the site but not added here is invisible to this check, and nothing
# else will notice -- there is no liveness tripwire for the alternation itself
# the way SELECTOR_MARKERS in hooks/pagefind_index.py has one for the
# selectors.
#
# The leading \b is deliberate: fusion into a preceding word character, as in
# "SetupPythonJava", is knowingly out of scope. Requiring the run to start at
# a word boundary is what keeps "RxJava" and "pdfArtifactJava" unflagged, and
# the two cannot both be had from one pattern. Measured on the 2026-08-07
# content set: across all 226 control fragments, zero fused runs began
# mid-word, so the exemption costs nothing today.
FUSED_TOKEN = re.compile(r"\b(?:ADK|Python|TypeScript|Go|Java|Kotlin){2,}[A-Za-z.0-9]*")

# Local-only pages. `docs/superpowers/` is listed in .gitignore, so these
# exist in a developer build and never in CI. The design document itself
# quotes fused tokens as literal prose describing the defect.
#
# The exemption is unconditional and path-based, not content-based: anything
# that ever lands under this prefix is silently exempt from the tokenization
# check. That is only safe while the prefix stays git-ignored scratch space.
# If real documentation is ever published there, narrow this to the specific
# design documents or drop it.
LOCAL_ONLY_PREFIX = "/superpowers/"

# URL prefixes that must never appear in the index, whatever the templates do.
#
# /404.html is the case the {% if page %} guard in overrides/main.html exists
# for. The rest is generated API-reference output -- Sphinx/Furo for Python,
# Dokka for Kotlin, and so on -- from pipelines decoupled from mkdocs-material;
# it is enormous, differently themed, and would swamp real results.
#
# These are language-specific on purpose. The bare prefix "/api-reference/"
# would match "/api-reference/", the hand-written landing page, which IS
# legitimately indexed. Verified against the 2026-08-07 build: "/api-reference/"
# is the only indexed URL under that tree.
#
# All seven generated subtrees are listed, not just the four large ones.
# agentconfig/, cli/ and rest/ are one to three files each and are equally
# not indexed today; barring them costs nothing and means a future template
# change cannot quietly pull them in.
NEVER_INDEXED = (
    "/404.html",
    "/api-reference/agentconfig/",
    "/api-reference/cli/",
    "/api-reference/java/",
    "/api-reference/kotlin/",
    "/api-reference/python/",
    "/api-reference/rest/",
    "/api-reference/typescript/",
)

# Pagefind prefixes each gzip-compressed fragment payload with this marker.
# The compression is applied over the marker too, so the file has to be
# decompressed before the marker can be found.
FRAGMENT_MARKER = b"pagefind_dcd"

# Fragment keys this script reads. Absence means the fragment schema changed
# under a Pagefind upgrade, which must be a loud failure: every check below
# reads these keys, and a checker that silently reads nothing reports green on
# a broken index.
REQUIRED_FRAGMENT_KEYS = ("url", "content")


def _load_fragments(site: Path) -> list[dict]:
    """Return the decoded JSON of every Pagefind fragment.

    Raises ``ValueError`` if a fragment is not in the expected format, rather
    than skipping it. ``requirements.txt`` pins ``pagefind-bin==1.5.2`` -- the
    binary, which is what produces the fragment format, and which the
    ``pagefind[bin]`` extra alone would only constrain to <2 -- so the format
    is fixed until someone bumps it, and the bump is exactly when this needs
    to fail loudly instead of quietly scanning nothing.
    """
    fragments = []
    for path in sorted((site / "pagefind" / "fragment").glob("*.pf_fragment")):
        raw = gzip.decompress(path.read_bytes())
        marker = raw.find(FRAGMENT_MARKER)
        if marker == -1:
            raise ValueError(
                f"{path.name} is not a Pagefind fragment: no "
                f"{FRAGMENT_MARKER.decode()} marker in the decompressed bytes"
            )
        fragment = json.loads(raw[raw.index(b"{", marker) :].decode("utf-8"))
        missing = [key for key in REQUIRED_FRAGMENT_KEYS if key not in fragment]
        if missing:
            raise ValueError(
                f"{path.name} has no {missing} key; the fragment schema has "
                f"changed and it now carries {sorted(fragment)}. Update "
                "REQUIRED_FRAGMENT_KEYS and the checks that read them"
            )
        fragments.append(fragment)
    return fragments


def _reported_page_count(site: Path) -> int:
    """Return the page count Pagefind recorded in its entry file.

    Raises ``ValueError`` if the entry file is malformed or its schema has
    changed, so that a Pagefind upgrade surfaces as a finding rather than a
    bare traceback -- the same contract as ``_load_fragments``.
    """
    path = site / "pagefind" / "pagefind-entry.json"
    try:
        entry = json.loads(path.read_text(encoding="utf-8"))
        return sum(lang["page_count"] for lang in entry["languages"].values())
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as exc:
        raise ValueError(
            f"{path} is not the schema this script expects "
            f"({type(exc).__name__}: {exc}); Pagefind's entry file format has "
            "probably changed"
        ) from exc


def check_scope(site: Path, indexed: int) -> list[str]:
    """Fail if Pagefind indexed fewer pages than were marked for indexing.

    This mirrors the scope assertion in ``hooks/pagefind_index.py``; the two
    must be kept in sync. The duplication is deliberate -- importing the hook
    would drag ``mkdocs.*`` into a script that otherwise needs only the
    standard library, and the point of this script is to run against a built
    site without the toolchain that built it.

    Note what this can and cannot catch. Pagefind indexes *exactly* the pages
    carrying ``data-pagefind-body``, so ``indexed`` and ``attribute_count`` are
    two measurements of the same cause and normally move together. The
    equality therefore only fires in one direction: Pagefind dropping a page
    it was told to index. It does NOT catch the attribute leaking onto a page
    that should never be searchable -- both numbers rise together and the
    check stays green. ``check_never_indexed`` owns that direction.
    """
    attribute_count = sum(
        1 for p in site.rglob("*.html") if b"data-pagefind-body" in p.read_bytes()
    )
    if indexed != attribute_count:
        return [
            f"index scope: Pagefind indexed {indexed} pages but "
            f"{attribute_count} HTML files carry data-pagefind-body"
        ]
    # An empty index satisfies the equality above, and would then let every
    # check below pass over nothing at all. Refuse to call that a pass.
    if indexed == 0:
        return [
            "index scope: no page carries data-pagefind-body and Pagefind "
            "indexed nothing, so search is empty and every check below is "
            "vacuous"
        ]
    print(f"  scope OK: {indexed} pages indexed, matching the attribute count")
    return []


def check_never_indexed(fragments: list[dict]) -> list[str]:
    """Fail if any page that must never be searchable made it into the index."""
    failures = [
        f"must never be indexed but is: {fragment['url']} (matched "
        f"{prefix!r}); the {{% if page %}} guard in overrides/main.html or "
        "the data-pagefind-body placement has stopped excluding it"
        for fragment in fragments
        for prefix in NEVER_INDEXED
        if fragment["url"].startswith(prefix)
    ]
    # Say nothing when there is nothing to say. An "OK" over an empty index is
    # reassurance the run has not earned, and check_scope has already failed.
    if not failures and fragments:
        print(f"  exclusions OK: none of {len(NEVER_INDEXED)} barred prefixes indexed")
    return failures


def check_fused_tokens(fragments: list[dict], indexed: int) -> list[str]:
    """Fail if any indexed page carries a fused language token."""
    failures = []
    checked = 0
    skipped = 0
    total_hits = 0
    for fragment in fragments:
        if fragment["url"].startswith(LOCAL_ONLY_PREFIX):
            skipped += 1
            continue
        checked += 1
        hits = FUSED_TOKEN.findall(fragment["content"])
        if hits:
            total_hits += len(hits)
            failures.append(f"fused tokens on {fragment['url']}: {sorted(set(hits))}")

    if failures:
        failures.append(
            f"{total_hits} fused tokens across {len(failures)} of {checked} "
            "indexed pages. Pagefind concatenates adjacent inline elements "
            "without a separator, so some construct is rendering language "
            "labels flush against each other. Either an EXCLUDE_SELECTORS "
            "entry in hooks/pagefind_index.py has stopped matching after a "
            "theme upgrade, in which case update it to the new class name, or "
            "a new construct needs adding to it. Do not suppress this by "
            "narrowing FUSED_TOKEN: the tokens are really in the index and "
            "really break search for those terms."
        )

    # Reconcile against the entry file. Without this the check is vacuous
    # whenever it sees no fragments -- a renamed fragment directory or
    # extension makes the glob return nothing, and scanning zero pages for
    # zero tokens reports green on an index nobody looked at.
    if checked + skipped != indexed:
        failures.append(
            f"fragment coverage: read {checked + skipped} fragments but the "
            f"entry file reports {indexed} indexed pages. The fragment layout "
            "under pagefind/fragment/ has changed, so the tokenization check "
            "is not seeing the index it is meant to check"
        )
    elif not failures and checked:
        # Suppressed when nothing was scanned: an empty index reconciles
        # cleanly (0 == 0) and would otherwise print a clean bill of health
        # directly above check_scope's report that the index is empty.
        print(f"  tokenization OK: no fused tokens across {checked} indexed pages")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        # The module docstring is a page long; argparse would reflow it into a
        # wall of collapsed text. The summary line is the useful part.
        description=__doc__.strip().splitlines()[0]
    )
    parser.add_argument(
        "site", nargs="?", default="site", help="path to the built site directory"
    )
    args = parser.parse_args()
    site = Path(args.site)

    if not (site / "pagefind" / "pagefind-entry.json").is_file():
        print(f"error: no Pagefind index found under {site}", file=sys.stderr)
        return 1

    print(f"Verifying Pagefind index in {site}")
    try:
        indexed = _reported_page_count(site)
    except ValueError as exc:
        sys.stdout.flush()  # see the note on the failure block below
        print("\nFAILED:", file=sys.stderr)
        print(f"  - {exc}", file=sys.stderr)
        return 1
    failures = check_scope(site, indexed)

    # A malformed or renamed fragment schema is a finding, not a crash: CI
    # readers should get the FAILED block below, not a bare traceback.
    try:
        fragments = _load_fragments(site)
    except (OSError, ValueError) as exc:
        failures.append(f"could not read Pagefind fragments: {exc}")
    else:
        failures += check_never_indexed(fragments)
        failures += check_fused_tokens(fragments, indexed)

    if failures:
        # stdout is block-buffered when redirected but stderr is not, so
        # without this the failure list lands above the progress lines it is
        # supposed to follow.
        sys.stdout.flush()
        print("\nFAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print("All search index checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
