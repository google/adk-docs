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

Replaces MkDocs Material's built-in lunr search. Three responsibilities:

1. ``on_pre_build`` clears the module-level state the other two hooks
   accumulate. The hook module stays loaded for the life of the process, so
   without this a long-running ``mkdocs serve`` would carry one rebuild's
   counts and findings into the next.
2. ``on_post_page`` marks the indexable region of each rendered page by adding
   ``data-pagefind-body`` to Material's content ``<article>``. Once any page on
   a site carries that attribute, Pagefind skips every page without it, so this
   is also how pages opt out of search.
3. ``on_post_build`` runs the Pagefind indexer over the built site and fails
   the build if the result looks empty.

Environment variables (``MKDOCS_`` prefixed so they cannot be confused with
Pagefind's own ``PAGEFIND_*`` configuration, which the subprocess inherits):

* ``MKDOCS_PAGEFIND_SKIP=1``       - skip indexing, logging a warning as it
  does so. ``mkdocs build --strict`` promotes that warning to a failure, which
  is deliberate: a strict build must never ship a site with no search index.
  CI builds with ``--strict``; ``mkdocs serve`` does not, so the escape hatch
  still works where it is meant to be used.
* ``MKDOCS_PAGEFIND_PLAYGROUND=1`` - also write the ranking playground.
"""

from __future__ import annotations

import logging
import os
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

# Punctuation that carries meaning here: adk.dev, run_async, a2a, C++, @tool.
INCLUDE_CHARACTERS = ".-@#+"

# A build producing fewer indexed pages than this is broken, not small.
# The site currently indexes 226 pages.
MIN_INDEXED_PAGES = 200

_missing_anchor: list[str] = []
_marked = 0


def _skip() -> bool:
    return os.environ.get("MKDOCS_PAGEFIND_SKIP") == "1"


def _is_excluded(page) -> bool:
    if page.file.src_uri.startswith(EXCLUDED_PREFIXES):
        return True
    search = page.meta.get("search")
    return isinstance(search, dict) and search.get("exclude") is True


def on_pre_build(config) -> None:
    """Reset per-build state so it cannot leak across ``mkdocs serve`` rebuilds."""
    global _marked
    _missing_anchor.clear()
    _marked = 0


def on_post_page(output: str, page, config) -> str:
    """Add ``data-pagefind-body`` to the content article of indexable pages."""
    global _marked
    if _skip() or _is_excluded(page):
        return output
    if ARTICLE not in output:
        _missing_anchor.append(page.file.src_uri)
        return output
    _marked += 1
    return output.replace(ARTICLE, ARTICLE_INDEXED, 1)


def on_post_build(config) -> None:
    if _skip():
        log.warning("MKDOCS_PAGEFIND_SKIP=1 set; search index not built.")
        return

    if _missing_anchor:
        sample = ", ".join(sorted(_missing_anchor)[:5])
        raise PluginError(
            f"Pagefind could not mark {len(_missing_anchor)} page(s) for "
            f"indexing: the anchor {ARTICLE!r} was not found. This usually "
            f"means the Material theme changed its content markup. Update "
            f"ARTICLE in hooks/pagefind.py. First offenders: {sample}"
        )

    # Pagefind only honours data-pagefind-body if at least one page carries it;
    # with zero marked pages it silently falls back to indexing every HTML file
    # whole-body. That failure mode raises the fragment count, so the floor
    # check below cannot catch it, and neither can the missing-anchor guard
    # above (excluded pages never reach it). This is the only place it shows.
    if _marked < MIN_INDEXED_PAGES:
        raise PluginError(
            f"Pagefind marked only {_marked} page(s) with data-pagefind-body, "
            f"below the floor of {MIN_INDEXED_PAGES}. With too few marked "
            f"pages Pagefind stops honouring the attribute and indexes every "
            f"page whole-body, so the build would go green while shipping an "
            f"index full of navigation chrome and pages meant to be excluded. "
            f"Check EXCLUDED_PREFIXES and _is_excluded in hooks/pagefind.py, "
            f"and any 'search.exclude' front matter."
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
    log.info("Pagefind indexed %d pages.", indexed)
