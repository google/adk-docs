#!/usr/bin/env python3
# Copyright 2025 Google LLC
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

"""Validate that all URLs in skills markdown files are reachable.

Extracts markdown links [text](url) and bare https:// URLs, deduplicates,
and verifies each returns a successful HTTP status.

Usage:
  python validate_links.py                    # validate all skills/**/*.md
  python validate_links.py skills/foo/bar.md  # validate specific files
"""

from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── URL extraction ────────────────────────────────────────────────────────────

# Matches [text](url) markdown links
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\((https?://[^)]+)\)")
# Matches bare https:// URLs not already inside a markdown link
_BARE_URL_RE = re.compile(r"(?<!\()(https?://[^\s\)>\]\"]+)")

# URLs or domains to skip (localhost, example domains, placeholders)
_SKIP_PATTERNS = (
    "localhost",
    "127.0.0.1",
    "example.com",
    "example.org",
    "your-project",
    "PROJECT_ID",
    "PROJECT_NUMBER",
    "SERVICE_NAME",
    "YOUR_",
    "{",
    "<",
)


def _should_skip(url: str) -> bool:
    """Return True if the URL is a placeholder or local address."""
    return any(pattern in url for pattern in _SKIP_PATTERNS)


def extract_urls(filepath: str) -> list[tuple[str, int]]:
    """Extract all HTTP(S) URLs from a markdown file.

    Returns (url, line_number) pairs.
    """
    urls: list[tuple[str, int]] = []
    in_code_block = False
    with open(filepath) as f:
        for line_num, line in enumerate(f, start=1):
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            for m in _MD_LINK_RE.finditer(line):
                url = m.group(2).rstrip(".,;:`")
                if not _should_skip(url):
                    urls.append((url, line_num))
            # Also catch bare URLs not captured by markdown links
            md_urls = {m.group(2).rstrip(".,;:`") for m in _MD_LINK_RE.finditer(line)}
            for m in _BARE_URL_RE.finditer(line):
                url = m.group(1).rstrip(".,;:`")
                if url not in md_urls and not _should_skip(url):
                    urls.append((url, line_num))
    return urls


# ── HTTP validation ──────────────────────────────────────────────────────────

_USER_AGENT = "Mozilla/5.0 (compatible; adk-docs-link-checker/1.0)"
_TIMEOUT = 15


def _build_session() -> requests.Session:
    """Build a requests session with retry logic."""
    session = requests.Session()
    retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers["User-Agent"] = _USER_AGENT
    return session


def validate_url(session: requests.Session, url: str) -> tuple[str, int | str]:
    """Check a URL with HEAD, falling back to GET.

    Returns (status, status_code_or_error).
    """
    for method in (session.head, session.get):
        try:
            resp = method(url, timeout=_TIMEOUT, allow_redirects=True)
            if resp.status_code < 400:
                return "PASS", resp.status_code
            # If HEAD returned 4xx/5xx, try GET before failing
            if method == session.head:
                continue
            return "FAIL", resp.status_code
        except requests.RequestException as e:
            if method == session.head:
                continue
            return "FAIL", str(e)
    return "FAIL", "all methods exhausted"


# ── File discovery ───────────────────────────────────────────────────────────


def discover_files(args: list[str]) -> list[str]:
    """Return markdown files to validate.

    If args are provided, use them directly. Otherwise glob skills/**/*.md.
    """
    if args:
        return args
    repo_root = Path(__file__).resolve().parent.parent.parent
    return sorted(glob.glob(str(repo_root / "skills" / "**" / "*.md"), recursive=True))


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    files = discover_files(sys.argv[1:])
    if not files:
        print("No markdown files found.")
        return 0

    # Collect and deduplicate URLs, tracking their source locations
    url_sources: dict[str, list[str]] = {}  # url -> [file:line, ...]
    for filepath in files:
        for url, line_num in extract_urls(filepath):
            loc = f"{filepath}:{line_num}"
            url_sources.setdefault(url, []).append(loc)

    if not url_sources:
        print("No URLs found to validate.")
        return 0

    print(f"Validating {len(url_sources)} unique URL(s) from {len(files)} file(s)...\n")

    session = _build_session()
    failures = 0

    for url, locations in sorted(url_sources.items()):
        status, detail = validate_url(session, url)
        loc_str = locations[0]
        if len(locations) > 1:
            loc_str += f" (+{len(locations) - 1} more)"

        print(f"[{status}] {loc_str}  {url}  ({detail})")

        if status == "FAIL":
            failures += 1

    if failures:
        print(f"\n{failures} link(s) failed validation.")
        return 1

    print(f"\nAll {len(url_sources)} link(s) OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
