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

"""Build the Pagefind search index for the site.

Replaces MkDocs Material's built-in lunr search. Four responsibilities:

1. ``on_startup`` records the command MkDocs was invoked with and whether
   ``--dirty`` was passed. It is the only hook told either, and both decide
   whether guards below apply.
2. ``on_pre_build`` clears the module-level state the other hooks accumulate.
   The hook module stays loaded for the life of the process, so without this a
   long-running ``mkdocs serve`` would carry one rebuild's findings into the
   next.
3. ``on_post_page`` marks the indexable region of each rendered page by adding
   ``data-pagefind-body`` to Material's content ``<article>``. Once any page on
   a site carries that attribute, Pagefind skips every page without it, so this
   is also how pages opt out of search. It also records which
   ``EXCLUDE_SELECTORS`` classes actually appeared, since the rendered HTML is
   already in hand here and re-reading the built site would be wasted I/O.
4. ``on_post_build`` runs the Pagefind indexer over the built site and fails
   the build if the resulting page count falls outside
   ``MIN_INDEXED_PAGES..MAX_INDEXED_PAGES``, if either browser-facing asset is
   missing, or if an exclude selector matched nothing. Both count bounds are
   checked against the finished index rather than against per-page counters, so
   they hold under ``mkdocs build``, ``mkdocs serve`` and ``mkdocs build
   --dirty`` alike: a dirty build re-renders only a handful of pages, but
   Pagefind still indexes the whole ``site_dir``.

Environment variables (``MKDOCS_`` prefixed so they cannot be confused with
Pagefind's own ``PAGEFIND_*`` configuration, which the subprocess inherits):

* ``MKDOCS_PAGEFIND_SKIP=1``       - skip indexing, logging a warning as it
  does so. Two separate guards keep it out of anything a reader sees.
  ``mkdocs build --strict`` promotes the warning to a failure, which covers
  pull requests. ``mkdocs gh-deploy``, which publishes the site, is refused
  outright: the deploy workflow does not pass ``--strict``, so the warning
  alone would let a site ship with no index. ``mkdocs serve`` is neither
  strict nor a deploy, so the escape hatch still works where it is meant to be
  used.
* ``MKDOCS_PAGEFIND_PLAYGROUND=1`` - also write the ranking playground.
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

# Material 9.x renders the page body into this element (base.html, block
# `container`). Adding the attribute here rather than in a template override
# keeps all Pagefind logic in one file and avoids owning a copy of Material's
# markup, which would silently stop tracking upstream changes.
ARTICLE = '<article class="md-content__inner md-typeset">'
ARTICLE_INDEXED = '<article class="md-content__inner md-typeset" data-pagefind-body>'

# Source-path prefixes that are published but must never appear in search.
# `superpowers/` matches nothing in a fresh clone: `docs/superpowers/` holds
# local planning notes kept untracked via .git/info/exclude. The prefix is here
# so those notes stay out of search on the machines that do have them.
EXCLUDED_PREFIXES = ("superpowers/",)

# Pagefind concatenates text across adjacent inline elements without inserting
# a separator, so siblings written with no whitespace between them index as a
# single fused token. `.headerlink` fuses the permalink onto every heading,
# `.tabbed-labels` yields "PythonJava", and `.language-support-tag` yields
# "ADKPythonTypeScriptGoJava".
EXCLUDE_SELECTORS = ".headerlink, .tabbed-labels, .language-support-tag"

# Derived from EXCLUDE_SELECTORS rather than written out again, so the guard in
# on_post_build cannot drift from the selectors it is guarding. A class
# attribute holds a space-separated list and these names contain hyphens, which
# `\b` treats as a word boundary, so the lookarounds are what stop
# `.headerlink` from matching a future `md-headerlink`.
EXCLUDE_CLASS_PATTERNS = {
    name: re.compile(rf'class="[^"]*(?<![\w-]){re.escape(name)}(?![\w-])')
    for name in (
        selector.strip().lstrip(".") for selector in EXCLUDE_SELECTORS.split(",")
    )
}

# Punctuation that carries meaning here: adk.dev, run_async, a2a, C++, @tool.
INCLUDE_CHARACTERS = ".-@#+"

# A build producing fewer indexed pages than this is broken, not small.
# The site currently indexes 226 pages.
MIN_INDEXED_PAGES = 200

# The built site holds roughly 3,500 HTML files (3,470 at the time of writing;
# the figure moves with every API-reference refresh), but only 226 are
# Material-rendered documentation pages; the rest are generated API reference
# (javadoc, typedoc, sphinx). Pagefind only honours data-pagefind-body if at
# least one page carries it, and with none it falls back to indexing every file
# whole-body. A count near the larger number therefore means nothing got marked
# and the index is full of API reference and navigation chrome, which no other
# guard sees.
MAX_INDEXED_PAGES = 500

_missing_anchor: list[str] = []

# Which EXCLUDE_CLASS_PATTERNS keys were seen in any page rendered this build.
_seen_exclude_classes: set[str] = set()

# Set once per `mkdocs` invocation by on_startup, before any build, and
# deliberately not cleared in on_pre_build: `mkdocs serve` calls on_startup once
# and then rebuilds on every file change, so a per-build reset would erase the
# command halfway through the first rebuild. The defaults below are what applies
# when the hooks are driven directly rather than through the CLI.
_command: str | None = None
_dirty: bool = False


def _skip() -> bool:
    return os.environ.get("MKDOCS_PAGEFIND_SKIP") == "1"


def _is_excluded(page) -> bool:
    if page.file.src_uri.startswith(EXCLUDED_PREFIXES):
        return True
    search = page.meta.get("search")
    return isinstance(search, dict) and search.get("exclude") is True


def on_startup(*, command: str, dirty: bool) -> None:
    """Record how MkDocs was invoked; no later hook is passed either value."""
    global _command, _dirty
    _command = command
    _dirty = dirty


def on_pre_build(config) -> None:
    """Reset per-build state so it cannot leak across ``mkdocs serve`` rebuilds."""
    _missing_anchor.clear()
    _seen_exclude_classes.clear()


def on_post_page(output: str, page, config) -> str:
    """Add ``data-pagefind-body`` to the content article of indexable pages."""
    if _skip() or _is_excluded(page):
        return output
    # Only pages that reach the index are scanned for the excluded classes. A
    # class surviving on an excluded page would prove nothing about the index,
    # and the excluded docs/superpowers/ notes quote these very class names
    # inside code blocks, which would hold the guard green through a real
    # rename.
    for name, pattern in EXCLUDE_CLASS_PATTERNS.items():
        if name not in _seen_exclude_classes and pattern.search(output):
            _seen_exclude_classes.add(name)
    if ARTICLE not in output:
        _missing_anchor.append(page.file.src_uri)
        return output
    return output.replace(ARTICLE, ARTICLE_INDEXED, 1)


def on_post_build(config) -> None:
    if _skip():
        # The publish workflow runs `mkdocs gh-deploy --force` without
        # --strict, so the warning below would not stop it: setting the
        # variable in the deploy environment would put a site with no search
        # index on adk.dev behind a green build. Refuse instead.
        if _command == "gh-deploy":
            raise PluginError(
                "MKDOCS_PAGEFIND_SKIP=1 is set and this is a `mkdocs "
                "gh-deploy`, which publishes the site: the search index "
                "cannot be skipped when publishing. Unset "
                "MKDOCS_PAGEFIND_SKIP and deploy again. The variable is meant "
                "for `mkdocs serve` while editing prose."
            )
        log.warning("MKDOCS_PAGEFIND_SKIP=1 set; search index not built.")
        return

    if _missing_anchor:
        sample = ", ".join(sorted(_missing_anchor)[:5])
        raise PluginError(
            f"Pagefind could not mark {len(_missing_anchor)} page(s) for "
            f"indexing: the anchor {ARTICLE!r} was not found. Either the "
            f"Material theme changed its content markup, in which case update "
            f"ARTICLE in hooks/pagefind.py to the new tag, or these pages "
            f"render from a custom template that has no md-content__inner "
            f"article, in which case opt them out of search with the "
            f"'search: exclude: true' front matter documented in "
            f"CONTRIBUTING.md. First offenders: {sample}"
        )

    # A dirty build re-renders only the pages that changed, so nearly every
    # class legitimately goes unseen and this check would fail on a healthy
    # site. It is the one guard here that reads per-page state rather than the
    # finished index, which is why it alone needs the exemption.
    if not _dirty:
        for name in EXCLUDE_CLASS_PATTERNS:
            if name not in _seen_exclude_classes:
                raise PluginError(
                    f"No indexed page carried the class {name!r}, so the "
                    f"matching selector in EXCLUDE_SELECTORS "
                    f"(hooks/pagefind.py) now targets markup that no longer "
                    f"exists. The class was most likely renamed. Until "
                    f"EXCLUDE_SELECTORS is updated to the new name, the fused "
                    f"tokens that selector was added to suppress are back in "
                    f"the index and search quality has degraded with no other "
                    f"symptom. Drop the selector instead if the markup is gone "
                    f"for good."
                )

    site_dir = Path(config["site_dir"])

    # Pagefind appends to its output directory instead of replacing it, and
    # `mkdocs build --dirty` does not clean site_dir, so fragments for deleted
    # pages would survive and keep turning up in search results.
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
        # Output is captured rather than inherited: Pagefind warns on every
        # build about the handful of API-reference files that have no <html>
        # element, which is expected and would otherwise be permanent noise.
        # Re-emitting it at debug level keeps a genuinely new warning
        # recoverable via `mkdocs build --verbose`. On failure the full output
        # is attached to the error instead.
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

    indexed = len(list((site_dir / "pagefind" / "fragment").glob("*.pf_fragment")))
    if indexed < MIN_INDEXED_PAGES:
        raise PluginError(
            f"Pagefind indexed only {indexed} page(s), below the floor of "
            f"{MIN_INDEXED_PAGES}. Search would ship broken. Check that "
            f"data-pagefind-body is present in the built HTML."
        )
    if indexed > MAX_INDEXED_PAGES:
        raise PluginError(
            f"Pagefind indexed {indexed} page(s), above the ceiling of "
            f"{MAX_INDEXED_PAGES}. No page carried data-pagefind-body, so "
            f"Pagefind ignored the attribute and indexed the entire site "
            f"whole-body: generated API reference and navigation chrome are "
            f"now in the index, and pages meant to be excluded are searchable. "
            f"Check _is_excluded and EXCLUDED_PREFIXES in hooks/pagefind.py, "
            f"and any 'search.exclude' front matter. If instead the "
            f"documentation has genuinely grown past {MAX_INDEXED_PAGES} "
            f"pages, raise MAX_INDEXED_PAGES and MIN_INDEXED_PAGES together so "
            f"the floor keeps its distance from the real page count."
        )

    # overrides/main.html links both of these by name from the <head> of every
    # page. Nothing above notices if Pagefind renames one or a later step
    # clobbers it: the fragment count stays perfect and the build stays green
    # while every page 404s its search UI.
    for asset in ("pagefind-component-ui.js", "pagefind-component-ui.css"):
        if not (site_dir / "pagefind" / asset).is_file():
            raise PluginError(
                f"Pagefind did not emit pagefind/{asset}, but "
                f"overrides/main.html loads it on every page, so search would "
                f"render as nothing: every page would 404 the asset and show "
                f"no search box at all. Check whether the Pagefind bundle "
                f"renamed the file, and update overrides/main.html to match."
            )

    log.info("Pagefind indexed %d pages.", indexed)
