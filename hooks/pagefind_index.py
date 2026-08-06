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
``site/pagefind/``. The browser downloads only the shards a query touches,
instead of the single multi-megabyte JSON index that MkDocs' built-in
lunr-based ``search`` plugin produces.

Which pages get indexed is controlled by the ``data-pagefind-body`` attribute
set on the ``<article>`` element in ``overrides/main.html``. Once that
attribute exists anywhere on the site, Pagefind indexes *only* pages that
carry it, which keeps the generated API reference output (Dokka, Javadoc and
TypeDoc write thousands of HTML files into ``docs/api-reference/``) out of the
index. Those files were never in the lunr index either, so this preserves the
existing search scope.

Set ``PAGEFIND_SKIP=1`` to skip indexing, e.g. for link-checking builds that
never serve the search UI.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time

from mkdocs.exceptions import PluginError

log = logging.getLogger("mkdocs.hooks.pagefind")

# Characters that Pagefind should treat as part of a word rather than as
# punctuation to strip. The ADK docs are full of identifiers that are
# meaningless once split ("adk.run", "google.adk.agents", "@Tool", "--reload"),
# and the default configuration would index those as separate bare words.
INCLUDE_CHARACTERS = ".-@#+"

# Interface chrome that sits inside the indexed article but is not prose.
#
# Pagefind concatenates the text of adjacent inline elements without inserting
# a separator, so sibling elements written without whitespace between them are
# indexed as a single fused token. Three constructs in this site hit that:
#
#   .headerlink          the "¶" permalink anchor appended to every heading by
#                        the `toc` extension - pure navigation, and it fused
#                        into headings on 230 of 232 pages
#   .tabbed-labels       the tab strip emitted by `pymdownx.tabbed`, written as
#                        `<label>Python</label><label>Java</label>`, which is
#                        indexed as "PythonJava". The tab *contents* are still
#                        indexed, so per-language content remains searchable.
#   .language-support-tag  the hand-authored "Supported in ADK" version badge,
#                        a run of adjacent <span>s that produced tokens such as
#                        "ADKPythonTypeScriptGoJava".
#
# Excluding these took pages carrying fused language tokens from 109/232 to
# 5/232, and every remaining hit is a genuine identifier ("RxJava",
# "pdfArtifactJava") rather than a defect.
EXCLUDE_SELECTORS = ".headerlink, .tabbed-labels, .language-support-tag"


def on_post_build(config, **kwargs) -> None:
    """Runs the Pagefind CLI over the freshly built site."""
    if os.environ.get("PAGEFIND_SKIP") == "1":
        log.info("PAGEFIND_SKIP=1 set, skipping search index build.")
        return

    site_dir = config["site_dir"]
    command = [
        sys.executable,
        "-m",
        "pagefind",
        "--site",
        site_dir,
        "--include-characters",
        INCLUDE_CHARACTERS,
        "--exclude-selectors",
        EXCLUDE_SELECTORS,
        # Errors only. The sole warning this suppresses is that eight generated
        # files (seven Dokka `navigation.html` fragments and the Google site
        # verification file) have no <html> element. None of them are indexable
        # or intended to be, so the warning is noise on every build. Genuine
        # failures still set a non-zero exit code and are raised below.
        "--silent",
    ]

    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:  # pragma: no cover - defensive
        raise PluginError(
            f"Could not run the Pagefind indexer ({error}). Install the pinned "
            "version with: pip install -r requirements.txt"
        ) from error

    if "No module named pagefind" in result.stderr:
        raise PluginError(
            "Pagefind is not installed, so the site would be built without a "
            "search index. Install it with: pip install -r requirements.txt"
        )

    if result.returncode != 0:
        raise PluginError(
            "Pagefind failed to build the search index "
            f"(exit code {result.returncode}).\n{result.stdout}\n{result.stderr}"
        )

    elapsed = time.monotonic() - started
    log.info("Built Pagefind search index in %.2f seconds", elapsed)
