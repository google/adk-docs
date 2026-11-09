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

"""Reads which SDKs a page supports, and rewrites its support banners.

A ``language-support-tag`` banner placed before a page's second heading is a
page banner: it declares the languages the whole page is generated for. A
banner further down is a section banner and scopes only its section (see
``langscope.sections``). Frontmatter ``languages:`` overrides page banners,
for language-specific pages that carry no banner.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from langscope import config, mdutil

_BANNER_START_RE = re.compile(
    r'^[ \t]*<div\b[^>]*\bclass="(?:[^"]*\s)?language-support-tag(?:\s[^"]*)?"'
)
_LST_CLASS_RE = re.compile(r'class="lst-([a-z]+)"')
_CLASS_ATTR_RE = re.compile(r'\bclass="(?P<classes>[^"]*)"')
_SPAN_RE = re.compile(r'<span class="lst-(?P<key>[a-z]+)"[^>]*>.*?</span>', re.DOTALL)
_TITLE_ATTR_RE = re.compile(r'\s+title="[^"]*"')


@dataclass(frozen=True)
class Banner:
    start: int  # First line index.
    end: int  # One past the last line index.
    indent: int
    languages: frozenset[str]
    # Has the ``langscope-all`` class: a version badge that scopes nothing.
    badge_only: bool = False


def find_banners(lines: list[str], mask: list[bool] | None = None) -> list[Banner]:
    """Finds every support banner outside fenced code, with any attributes."""
    if mask is None:
        mask = mdutil.code_mask(lines)
    banners: list[Banner] = []
    i = 0
    while i < len(lines):
        if mask[i] or not _BANNER_START_RE.match(lines[i]):
            i += 1
            continue
        j = i
        while j < len(lines) and "</div>" not in lines[j]:
            j += 1
        end = min(j + 1, len(lines))
        text = "\n".join(lines[i:end])
        keys = frozenset(
            k for k in _LST_CLASS_RE.findall(text) if k in config.ALL_KEYS
        )
        classes = _CLASS_ATTR_RE.search(lines[i]).group("classes").split()
        banners.append(Banner(
            i, end, mdutil.indent_len(lines[i]), keys, "langscope-all" in classes))
        i = end
    return banners


def _second_heading(lines: list[str], mask: list[bool]) -> int:
    seen = 0
    for i, line in enumerate(lines):
        if not mask[i] and mdutil.heading(line) is not None:
            seen += 1
            if seen == 2:
                return i
    return len(lines)


def page_banners(lines: list[str], mask: list[bool] | None = None) -> list[Banner]:
    """Banners in the page lead: unindented and before the second heading."""
    if mask is None:
        mask = mdutil.code_mask(lines)
    limit = _second_heading(lines, mask)
    return [
        b for b in find_banners(lines, mask) if b.indent == 0 and b.start < limit
    ]


def frontmatter_languages(markdown: str) -> frozenset[str] | None:
    """Returns the frontmatter ``languages:`` override, or None if unset.

    Raises:
        ValueError: if it names a language that is not configured.
    """
    meta = mdutil.frontmatter(markdown)
    if "languages" not in meta:
        return None
    value = meta["languages"]
    items = [value] if isinstance(value, str) else list(value or [])
    keys = set()
    for item in items:
        key = config.label_to_key(str(item))
        if key is None:
            raise ValueError(
                f"frontmatter 'languages' names unknown language {item!r}; "
                f"expected some of {', '.join(config.ORDERED_KEYS)}"
            )
        keys.add(key)
    return frozenset(keys)


def supported_languages(markdown: str) -> frozenset[str]:
    """Returns the languages a page is generated for.

    The frontmatter override wins; otherwise the page banners decide, and a
    page with no page banner is generated for every language.
    """
    override = frontmatter_languages(markdown)
    if override is not None:
        return override
    _, body = mdutil.split_frontmatter(markdown)
    banners = page_banners(body.split("\n"))
    if not banners:
        return config.ALL_KEYS
    keys: set[str] = set()
    for banner in banners:
        keys |= banner.languages
    # A banner with no recognizable language span declares support for none.
    return frozenset(keys)


def filter_banner(lines: list[str], lang: str) -> list[str]:
    """Narrows a banner to one language's version badge.

    Other languages' spans and the ``title`` tooltip (which describes
    cross-language support) go; ``lst-supported`` and ``lst-preview`` stay.
    """
    text = "\n".join(lines)
    text = _SPAN_RE.sub(
        lambda m: m.group(0)
        if m.group("key") not in config.ALL_KEYS or m.group("key") == lang
        else "",
        text,
    )
    first, sep, rest = text.partition(">")
    text = _TITLE_ATTR_RE.sub("", first) + sep + rest
    return text.split("\n")


def scope_page_banners(markdown: str, lang: str) -> str:
    """Rewrites the page banners for one language's view of the page.

    Banners that include ``lang`` become its version badge; banners that do
    not (possible only under a frontmatter override) are removed.
    """
    fm, body = mdutil.split_frontmatter(markdown)
    lines = body.split("\n")
    out: list[str] = []
    cursor = 0
    for banner in page_banners(lines):
        out.extend(lines[cursor:banner.start])
        if lang in banner.languages:
            out.extend(filter_banner(lines[banner.start:banner.end], lang))
        cursor = banner.end
    out.extend(lines[cursor:])
    return fm + "\n".join(out)
