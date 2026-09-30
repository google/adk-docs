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

"""Builds the Pagefind search index, replacing Material's built-in search.

``MKDOCS_PAGEFIND_SKIP=1`` skips indexing, except under ``gh-deploy``;
``MKDOCS_PAGEFIND_PLAYGROUND=1`` also writes the ranking playground.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from mkdocs.exceptions import PluginError

log = logging.getLogger("mkdocs.hooks.pagefind")

# Material 9.x renders the page body into this element. Marking it from a hook
# avoids owning a copy of Material's markup in a template override.
ARTICLE = '<article class="md-content__inner md-typeset">'
ARTICLE_INDEXED = '<article class="md-content__inner md-typeset" data-pagefind-body>'

# Pagefind fuses text across adjacent inline elements with no separator:
# `.headerlink` onto every heading, `.tabbed-labels` into "PythonJava".
EXCLUDE_SELECTORS = ".headerlink, .tabbed-labels, .language-support-tag"

# Derived from EXCLUDE_SELECTORS so the guard cannot drift from them. Hyphens
# defeat `\b`, hence the lookarounds. Only bare `.class` selectors can be
# matched as text, so anything else is skipped rather than left unmatchable.
_SIMPLE_CLASS = re.compile(r"\.([A-Za-z_][\w-]*)$")
EXCLUDE_CLASS_PATTERNS = {
    match[1]: re.compile(rf'class="[^"]*(?<![\w-]){re.escape(match[1])}(?![\w-])')
    for match in (
        _SIMPLE_CLASS.fullmatch(selector.strip())
        for selector in EXCLUDE_SELECTORS.split(",")
    )
    if match
}

# Punctuation that carries meaning here: adk.dev, run_async, a2a, C++, @tool.
INCLUDE_CHARACTERS = ".-@#+"

# Symbols overrides/main.html chains through to set ranking. A rename throws in
# the browser, ranking silently reverts, and nothing else notices.
RANKING_API_SYMBOLS = ("PagefindComponents", "getInstanceManager")

_missing_anchor: list[str] = []

# Which EXCLUDE_CLASS_PATTERNS keys were seen in any page rendered this build.
_seen_exclude_classes: set[str] = set()

# Set once per invocation by on_startup, not per build: `mkdocs serve` calls
# on_startup once and then rebuilds on every file change.
_command: str | None = None
_dirty: bool = False


def _skip() -> bool:
    return os.environ.get("MKDOCS_PAGEFIND_SKIP") == "1"


def _is_excluded(page) -> bool:
    search = page.meta.get("search")
    return isinstance(search, dict) and search.get("exclude") is True


def _count_marked(site_dir: Path) -> int:
    """Counts marked pages in the built site, not ``on_post_page`` calls.

    ``--dirty`` re-renders only changed pages, so counting calls would
    undercount what Pagefind still indexes.
    """
    return sum(
        ARTICLE_INDEXED in path.read_text(encoding="utf-8", errors="ignore")
        for path in site_dir.rglob("*.html")
    )


def on_startup(*, command: str, dirty: bool) -> None:
    """Records how MkDocs was invoked; no later hook is passed either value."""
    global _command, _dirty
    _command = command
    _dirty = dirty


def on_pre_build(config) -> None:
    """Resets per-build state so it cannot leak across ``mkdocs serve`` rebuilds."""
    _missing_anchor.clear()
    _seen_exclude_classes.clear()


def on_post_page(output: str, page, config) -> str:
    """Adds ``data-pagefind-body`` to the content article of indexable pages."""
    if _skip() or _is_excluded(page):
        return output
    # Only indexed pages count: a class on an excluded page proves nothing.
    for name, pattern in EXCLUDE_CLASS_PATTERNS.items():
        if name not in _seen_exclude_classes and pattern.search(output):
            _seen_exclude_classes.add(name)
    if ARTICLE not in output:
        _missing_anchor.append(page.file.src_uri)
        return output
    return output.replace(ARTICLE, ARTICLE_INDEXED, 1)


def on_post_build(config) -> None:
    if _skip():
        # gh-deploy runs without --strict, so the warning below would not
        # stop it shipping a site with no index.
        if _command == "gh-deploy":
            raise PluginError(
                "MKDOCS_PAGEFIND_SKIP=1 is set, but `mkdocs gh-deploy` "
                "publishes the site and cannot skip the search index. Unset "
                "the variable; it is meant for `mkdocs serve`."
            )
        log.warning("MKDOCS_PAGEFIND_SKIP=1 set; search index not built.")
        return

    if _missing_anchor:
        sample = ", ".join(sorted(_missing_anchor)[:5])
        raise PluginError(
            f"Pagefind could not mark {len(_missing_anchor)} page(s): the "
            f"anchor {ARTICLE!r} was not found. Either Material changed its "
            f"content markup, so update ARTICLE in hooks/pagefind.py, or "
            f"these pages use a custom template with no md-content__inner "
            f"article, so opt them out with the 'search: exclude: true' front "
            f"matter documented in CONTRIBUTING.md. First offenders: {sample}"
        )

    # Argues from absence, which only a full render supports: a dirty build
    # re-renders too few pages for an unseen class to mean anything.
    if not _dirty:
        for name in EXCLUDE_CLASS_PATTERNS:
            if name not in _seen_exclude_classes:
                raise PluginError(
                    f"No indexed page carried the class {name!r}, so the "
                    f"matching selector in EXCLUDE_SELECTORS "
                    f"(hooks/pagefind.py) targets markup that no longer "
                    f"exists, most likely renamed. Until it is updated the "
                    f"fused tokens it suppressed are back in the index, with "
                    f"no other symptom. Drop the selector if the markup is "
                    f"gone for good."
                )

    site_dir = Path(config["site_dir"])

    # Checked before indexing: with nothing marked, Pagefind falls back to
    # indexing every file whole-body, its slowest path, for the same failure.
    marked = _count_marked(site_dir)
    if marked == 0:
        raise PluginError(
            f"No page in {site_dir} carries the Pagefind marker, so search "
            f"would return nothing. Every page was excluded or unmarked: "
            f"check _is_excluded in hooks/pagefind.py and any "
            f"'search: exclude: true' front matter."
        )

    # Pagefind appends to its output directory and `--dirty` does not clean
    # site_dir, so fragments for deleted pages would survive in results.
    shutil.rmtree(site_dir / "pagefind", ignore_errors=True)

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
    if os.environ.get("MKDOCS_PAGEFIND_PLAYGROUND") == "1":
        command.append("--write-playground")

    log.info("Building Pagefind search index in %s", site_dir)
    try:
        # Captured, not inherited: Pagefind warns on every build about API
        # reference files with no <html>. Debug keeps new warnings reachable.
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        log.debug("Pagefind stdout:\n%s", result.stdout)
        log.debug("Pagefind stderr:\n%s", result.stderr)
    except subprocess.CalledProcessError as error:
        # `python -m pagefind` with the package absent exits non-zero rather
        # than raising FileNotFoundError, so the install hint belongs here.
        stderr = error.stderr or ""
        if "No module named pagefind" in stderr:
            raise PluginError(
                "Could not run the Pagefind indexer. Install it with "
                "'pip install -r requirements.txt'."
            ) from error
        raise PluginError(
            f"Pagefind indexing failed with exit code {error.returncode}. "
            f"No prebuilt binary may exist for this platform; see "
            f"https://pypi.org/project/pagefind-bin/\n"
            f"{error.stdout}\n{stderr}"
        ) from error

    # One fragment per indexed page, so the counts describe the same set and
    # any difference is a defect. No threshold to go stale.
    indexed = len(list((site_dir / "pagefind" / "fragment").glob("*.pf_fragment")))
    if indexed != marked:
        raise PluginError(
            f"Pagefind indexed {indexed} page(s) but the build marked "
            f"{marked}; Pagefind writes one fragment per indexed page, so the "
            f"two must match. Far more indexed than marked means the marker "
            f"was on no page at all and Pagefind indexed the whole site "
            f"whole-body, so check that on_post_page still finds the ARTICLE "
            f"anchor. Fewer means marked pages were dropped during indexing; "
            f"drop --quiet to see which. Either way, "
            f"`grep -rl {ARTICLE_INDEXED!r} {site_dir}` lists the marked pages."
        )

    # overrides/main.html links both from every page's <head>. Nothing above
    # notices a rename: fragment counts stay perfect while search 404s.
    for asset in ("pagefind-component-ui.js", "pagefind-component-ui.css"):
        if not (site_dir / "pagefind" / asset).is_file():
            raise PluginError(
                f"Pagefind did not emit pagefind/{asset}, which "
                f"overrides/main.html loads on every page, so no search box "
                f"would render at all. Check whether the Pagefind bundle "
                f"renamed the file and update overrides/main.html to match."
            )

    # Read once for both symbols: the bundle is hundreds of kilobytes of
    # minified JavaScript and this runs on every build.
    component_ui = (site_dir / "pagefind" / "pagefind-component-ui.js").read_text(
        encoding="utf-8", errors="ignore"
    )
    for symbol in RANKING_API_SYMBOLS:
        if symbol not in component_ui:
            raise PluginError(
                f"pagefind/pagefind-component-ui.js no longer contains "
                f"{symbol!r}, which overrides/main.html chains through to set "
                f"the search ranking. Left alone it throws a TypeError in the "
                f"browser and ranking silently reverts to Pagefind's "
                f"defaults. Update the script in overrides/main.html to the "
                f"new API, and RANKING_API_SYMBOLS with it."
            )

    log.info("Pagefind indexed %d pages, matching %d marked.", indexed, marked)
