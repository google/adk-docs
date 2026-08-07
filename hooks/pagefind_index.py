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

"""Builds the Pagefind search index as a MkDocs post-build step.

Pagefind is a static search engine: it crawls the *rendered* HTML in
``site_dir`` and emits a sharded index plus a WASM query engine into
``site/pagefind/``. The browser fetches only the shards a query touches,
instead of the single multi-megabyte JSON index the built-in lunr-based
``search`` plugin produces. That plugin is still enabled at this commit, so
the site currently ships both indexes; ``search`` is removed later in this
series, once the Pagefind-backed UI is in place.

Which pages get indexed is controlled by the ``data-pagefind-body`` attribute
on the ``<article>`` element, set in ``overrides/main.html``. Once that
attribute exists anywhere on the site, Pagefind indexes *only* pages carrying
it, which keeps the generated API reference output out of the index.

Set ``PAGEFIND_SKIP`` to any value other than ``0``, ``false``, ``no`` or
``off`` to skip indexing. This is for ``mkdocs serve`` authoring loops; search
is non-functional while it is set, so skipping logs a warning and therefore
fails a ``--strict`` build.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import event_priority
from mkdocs.plugins import get_plugin_logger

log = get_plugin_logger(__name__)

BODY_ATTRIBUTE = b"data-pagefind-body"

# Pagefind concatenates adjacent inline elements without a separator, so
# sibling elements authored without whitespace fuse into a single token.
# Three constructs on this site hit that:
#   .headerlink           the "&para;" permalink anchor, fusing into headings
#   .tabbed-labels        <label>Python</label><label>Java</label> from
#                         pymdownx.tabbed, indexed as "PythonJava"
#   .language-support-tag the "Supported in ADK" badge, which produced
#                         "ADKPythonTypeScriptGoJava"
# Measured on the 2026-08-07 content set, over a 226-page control build with
# no exclude selectors: removing them drops fused tokens from 219 across 193
# of the 226 indexed pages to zero. Tab *contents* stay indexed, so
# per-language content remains searchable.
#
# Each selector is paired with the substring that proves it is still rendered
# somewhere on the site. A selector that matches nothing is valid CSS and
# fails silently -- the build stays green while the fused tokens come back --
# so the marker counts are asserted on every build. Pairing them here means a
# selector cannot be added without a liveness check.
#
# Those counts are taken over indexed pages ONLY (see _count_markers), and that
# scoping is load-bearing, not an optimisation. site/api-reference/python/ is
# Sphinx/Furo output from a pipeline decoupled from mkdocs-material, and Furo
# also emits class="headerlink" -- google-adk.html alone has 1372 occurrences.
# Counting site-wide would pin that marker above zero forever, so the tripwire
# could never fire for the exact case it exists for: mkdocs-material renaming
# the class. Verified: with site-wide counting, a simulated rename across all
# theme-rendered pages still left headerlink at 3 and the check stayed silent.
#
# One caveat on .tabbed-labels: 234 pages match the substring but only 119
# contain a real element, because material's inlined JS bundle mentions
# ".tabbed-labels" on every page. It still detects a material rename (the
# bundle changes too), but it is really measuring "the bundle is present" and
# would not notice pymdownx.tabbed being dropped from mkdocs.yml.
SELECTOR_MARKERS: dict[str, bytes] = {
    ".headerlink": b"headerlink",
    ".tabbed-labels": b"tabbed-labels",
    ".language-support-tag": b"language-support-tag",
}

# Two selectors sharing a marker would collapse into one count, and both would
# then be checked by whichever is live -- the one way to add a selector that
# skips its own liveness check. A hard raise rather than an `assert`, because
# `assert` is stripped under `python -O` and a guard that vanishes under an
# interpreter flag is worse than no guard at all.
if len(set(SELECTOR_MARKERS.values())) != len(SELECTOR_MARKERS):
    raise ValueError(
        "each selector needs its own marker; a shared one is not an "
        "independent check"
    )

# ".headerlink, .tabbed-labels, .language-support-tag"
EXCLUDE_SELECTORS = ", ".join(SELECTOR_MARKERS)

# Keep dotted and prefixed identifiers intact. Without this,
# "google.adk.agents" degrades into three unrelated words.
INCLUDE_CHARACTERS = ".-@#+"

# Indexing this site takes ~4s. The ceiling only exists so that a wedged
# Pagefind fails the build instead of burning the CI job's 6-hour limit.
TIMEOUT_SECONDS = 600

# Values of PAGEFIND_SKIP that mean "do not skip". Presence alone is not
# enough: PAGEFIND_SKIP=0 in a CI matrix must not silently ship dead search.
_SKIP_DISABLED = {"", "0", "false", "no", "off"}


def _count_markers(site_dir: Path) -> dict[bytes, int]:
    """Count how many built HTML files contain each marker, in one pass.

    Returns a mapping from each marker to the number of files containing it.
    Everything is counted in a single traversal because the traversal, not the
    substring search, is what costs anything.

    ``BODY_ATTRIBUTE`` is counted across every built page; the selector markers
    are counted only on the pages carrying it. A page Pagefind does not index
    cannot contribute a fused token to the index, so its markup says nothing
    about whether a selector is still doing its job -- and the generated API
    reference is large enough to hold a marker above zero on its own.
    """
    selector_markers = tuple(SELECTOR_MARKERS.values())
    counts = dict.fromkeys((BODY_ATTRIBUTE, *selector_markers), 0)
    for path in site_dir.rglob("*.html"):
        try:
            html = path.read_bytes()
        except OSError as exc:  # pragma: no cover - unreadable file
            log.warning("Could not read %s: %s", path, exc)
            continue
        if BODY_ATTRIBUTE not in html:
            continue
        counts[BODY_ATTRIBUTE] += 1
        for marker in selector_markers:
            if marker in html:
                counts[marker] += 1
    return counts


def _reported_page_count(site_dir: Path) -> int:
    """Return the page count Pagefind recorded in its entry file."""
    entry = site_dir / "pagefind" / "pagefind-entry.json"
    if not entry.is_file():
        raise PluginError(f"Pagefind wrote no entry file at {entry}.")
    data = json.loads(entry.read_text(encoding="utf-8"))
    return sum(lang["page_count"] for lang in data["languages"].values())


def _check_selectors_still_match(marker_counts: dict[bytes, int]) -> None:
    """Fail if any exclude selector no longer matches any indexed page."""
    for selector, marker in SELECTOR_MARKERS.items():
        if marker_counts[marker] == 0:
            raise PluginError(
                f"The exclude selector {selector!r} matches no indexed page, so "
                "it is no longer suppressing anything and adjacent inline "
                "elements will fuse into single tokens in the search index. "
                "Either the theme renamed the class, in which case update "
                "EXCLUDE_SELECTORS in this hook to the new name, or the "
                "construct has genuinely been removed from the site, in which "
                "case drop it from EXCLUDE_SELECTORS. Do not leave it as a "
                "selector that matches nothing: that is silently ineffective."
            )


@event_priority(-100)
def on_post_build(config: MkDocsConfig, **kwargs: Any) -> None:
    """Run Pagefind over the built site and verify the index scope.

    Runs at the lowest priority so that it sees the final contents of
    ``site_dir``. Anything emitting indexable HTML from its own
    ``on_post_build`` must run before this, or its pages are both unindexed
    and uncounted, which would leave the assertions below green.
    """
    if os.environ.get("PAGEFIND_SKIP", "").strip().lower() not in _SKIP_DISABLED:
        log.warning(
            "PAGEFIND_SKIP is set - skipping the Pagefind index build. "
            "Site search will not work in this build."
        )
        return

    site_dir = Path(config.site_dir)
    marker_counts = _count_markers(site_dir)

    expected = marker_counts[BODY_ATTRIBUTE]
    if expected == 0:
        raise PluginError(
            f"No file in {site_dir} carries {BODY_ATTRIBUTE.decode()}. The "
            "container block in overrides/main.html has probably stopped "
            "matching the theme, and search would be built empty."
        )
    _check_selectors_still_match(marker_counts)

    command = [
        sys.executable,
        "-m",
        "pagefind",
        "--site",
        str(site_dir),
        "--exclude-selectors",
        EXCLUDE_SELECTORS,
        "--include-characters",
        INCLUDE_CHARACTERS,
        "--quiet",
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=TIMEOUT_SECONDS
        )
    except subprocess.TimeoutExpired as exc:
        raise PluginError(
            f"Pagefind did not finish within {TIMEOUT_SECONDS}s and was "
            "killed. The index in site/pagefind/ is incomplete."
        ) from exc
    if result.returncode != 0:
        raise PluginError(
            "Pagefind indexing failed with exit code "
            f"{result.returncode}:\n{result.stdout}\n{result.stderr}"
        )

    # Pagefind writes non-fatal diagnostics to stderr while still exiting 0,
    # even under --quiet. Keep this at info, NOT warning: the site's standing
    # notices ("N pages found without an <html> element") come from generated
    # API-reference files we do not control, and CI builds with --strict,
    # which turns any warning into a hard failure.
    if result.stderr.strip():
        log.info("Pagefind reported:\n%s", result.stderr.strip())

    reported = _reported_page_count(site_dir)
    if reported != expected:
        raise PluginError(
            f"Pagefind indexed {reported} pages but {expected} files carry "
            f"{BODY_ATTRIBUTE.decode()}. The index scope is not what the "
            "templates describe."
        )

    log.info("Pagefind indexed %d pages.", reported)
