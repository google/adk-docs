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

"""Drops the parts of a flattened page that belong to other languages.

Runs after tab flattening and page-banner scoping. The rules are deliberately
conservative: leaving another language's text visible (as the unscoped site
does) is acceptable, removing shared text is not. Only these mark part of a
page as language-specific:

Explicit markers (always honoured):

* A section banner, a ``language-support-tag`` directly under a heading below
  the page lead, scopes that heading's section. In a listed language the
  banner becomes that language's version badge; elsewhere the section goes.
  A banner with the ``langscope-all`` class is only a badge: it is dropped
  where its language is missing, but the section stays.
* A ``langscope-<language>`` class on a heading (``## Setup
  { .langscope-kotlin }``) scopes its section; on an admonition (``!!! note
  langscope-go "Path prefix"``) it scopes the admonition. ``langscope-all``
  exempts the heading or admonition from the heuristics below.

Heuristics (off for a page whose frontmatter sets
``language_heuristics: false``):

* A heading below the page title whose text is only language names
  ("## Python", "## Java and Kotlin") or ends in a parenthesis holding only
  language names ("### Log levels (Python)") scopes its section.
* An admonition titled only languages plus "only" ("Python only", "Go-only",
  "Only Python and TypeScript") is shown only in those languages. When it
  opens a section (directly under the heading), the whole section is scoped.

A rule never removes anything from a page none of whose languages it names:
on a Kotlin-only page, "## Java" stays, since removing it would leave the
content in no view at all. Such skips are reported as ``kept`` removals.

A section runs from its heading to the next heading of the same or a higher
level, so prose placed under a scoped heading goes with it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from langscope import config, mdutil, support

_ADMONITION_RE = re.compile(
    r'^(?P<indent>[ \t]*)(?:!!!|\?\?\?\+?)'
    r'(?P<types>(?:[ \t]+[\w-]+)*)'
    r'(?:[ \t]+"(?P<title>[^"]*)")?[ \t]*$'
)
_ONLY_RE = re.compile(
    r"^(?:(?P<a>.+?)[ \t]*(?:[ \t]|-)only|only[ \t]+(?P<b>.+?))$", re.IGNORECASE)
_TRAILING_PAREN_RE = re.compile(r"\((?P<langs>[^()]+)\)$")

CLASS_PREFIX = "langscope-"
ALL_CLASS = CLASS_PREFIX + "all"
HEURISTICS_KEY = "language_heuristics"


@dataclass(frozen=True)
class Removal:
    """A span of the page removed from (or kept in) one language's view."""

    line: int  # 1-based, in the text given to scope_sections.
    kind: str  # "section banner", "heading", "admonition", "section aside".
    what: str  # The heading or admonition title.
    languages: frozenset[str]
    anchors: tuple[str, ...] = ()  # Heading ids inside the removed span.
    explicit: bool = False  # From a banner or langscope-* class, not a heuristic.
    kept: bool = False  # Not removed: it names none of the page's languages.


def _block_end(lines: list[str], mask: list[bool], start: int) -> int:
    """End of the indented block opened at ``start`` (an admonition)."""
    indent = mdutil.indent_len(lines[start])
    j = start + 1
    last = start
    while j < len(lines):
        if not mdutil.is_blank(lines[j]):
            if mdutil.indent_len(lines[j]) <= indent and not mask[j]:
                break
            last = j
        j += 1
    return last + 1


def _section_end(lines: list[str], mask: list[bool], start: int) -> int:
    """End of the section opened by the heading at ``start``."""
    indent, level, _ = mdutil.heading(lines[start])
    for j in range(start + 1, len(lines)):
        if mask[j] or mdutil.is_blank(lines[j]):
            continue
        if mdutil.indent_len(lines[j]) < indent:
            return j
        h = mdutil.heading(lines[j])
        if h is not None and h[0] == indent and h[1] <= level:
            return j
    return len(lines)


def class_languages(classes: list[str]) -> frozenset[str] | None:
    """Languages named by ``langscope-*`` classes; ALL_KEYS for ``-all``.

    Returns None when no ``langscope-*`` class is present.

    Raises:
        ValueError: for a ``langscope-*`` class naming an unknown language.
    """
    keys: set[str] = set()
    found = False
    for cls in classes:
        if not cls.startswith(CLASS_PREFIX):
            continue
        found = True
        name = cls[len(CLASS_PREFIX):]
        if name == "all":
            return config.ALL_KEYS
        key = config.label_to_key(name)
        if key is None:
            raise ValueError(
                f"class {cls!r} names unknown language {name!r}; expected "
                f"{ALL_CLASS} or {CLASS_PREFIX}<one of "
                f"{', '.join(config.ORDERED_KEYS)}>")
        keys.add(key)
    return frozenset(keys) if found else None


def heading_languages(text: str) -> frozenset[str]:
    """Languages a heading is unambiguously about, by its wording alone.

    "Python", "Java and Kotlin" and "Log levels (Python)" qualify;
    "ADK for Java", "Configure in Python" and "Migrating from Java" do not.
    """
    keys = config.exact_label_keys(text)
    if keys:
        return keys
    m = _TRAILING_PAREN_RE.search(text.strip())
    if m is not None and m.start() > 0:
        return config.exact_label_keys(m.group("langs"))
    return frozenset()


def only_title_languages(title: str) -> frozenset[str]:
    """Languages of an "X only" title ("Go and Java only", "Only Python")."""
    m = _ONLY_RE.match(title.strip())
    if m is None:
        return frozenset()
    return config.exact_label_keys(m.group("a") or m.group("b"))


def _leading_heading(lines: list[str], mask: list[bool], i: int) -> int | None:
    """The heading line ``i`` directly follows (blank lines aside), if any."""
    indent = mdutil.indent_len(lines[i])
    for j in range(i - 1, -1, -1):
        if mdutil.is_blank(lines[j]):
            continue
        h = None if mask[j] else mdutil.heading(lines[j])
        if h is not None and h[0] == indent and h[1] > 1:
            return j
        return None
    return None


def heuristics_enabled(markdown: str) -> bool:
    """False when the page's frontmatter sets ``language_heuristics: false``."""
    return mdutil.frontmatter(markdown).get(HEURISTICS_KEY, True) is not False


def scope_sections(
    markdown: str, lang: str, page_languages: frozenset[str] = config.ALL_KEYS
) -> tuple[str, list[Removal]]:
    """Removes other languages' sections and asides from one language's view."""
    text, removals, _ = scope_sections_mapped(markdown, lang, page_languages)
    return text, removals


def scope_sections_mapped(
    markdown: str, lang: str, page_languages: frozenset[str] = config.ALL_KEYS
) -> tuple[str, list[Removal], list[int]]:
    """Like ``scope_sections``; also maps each output line to its input line.

    ``page_languages`` are the languages the page is generated for. The map
    holds 1-based input line numbers, so later passes can report source
    positions.

    Raises:
        ValueError: for a ``langscope-*`` class naming an unknown language.
    """
    heuristics = heuristics_enabled(markdown)
    fm, body = mdutil.split_frontmatter(markdown)
    base = fm.count("\n")
    lines = body.split("\n")
    mask = mdutil.code_mask(lines)
    headings = [
        i for i, line in enumerate(lines)
        if not mask[i] and mdutil.heading(line) is not None
    ]
    drop = [False] * len(lines)
    removals: list[Removal] = []
    rewrites: dict[int, support.Banner] = {}

    def scope(start: int, end: int, kind: str, what: str, langs,
              explicit: bool) -> None:
        """Removes lines [start, end) unless ``lang`` is in ``langs``."""
        if lang in langs:
            return
        anchors = tuple(
            a for k in range(start, end)
            if not mask[k] and (a := mdutil.heading_id(lines[k].strip()))
        )
        kept = not (langs & page_languages)
        if not kept:
            for k in range(start, end):
                drop[k] = True
        removals.append(Removal(
            base + start + 1, kind, what, frozenset(langs),
            () if kept else anchors, explicit, kept))

    for banner in support.find_banners(lines, mask):
        if lang in banner.languages:
            rewrites[banner.start] = banner
            continue
        owner = _leading_heading(lines, mask, banner.start)
        if owner is None or banner.badge_only:
            # Nothing to scope: drop only the banner, which names other SDKs.
            for k in range(banner.start, banner.end):
                drop[k] = True
            continue
        scope(owner, _section_end(lines, mask, owner), "section banner",
              mdutil.heading(lines[owner])[2], banner.languages, True)

    for h in headings:
        _, level, text = mdutil.heading(lines[h])
        if level == 1:
            continue
        keys = class_languages(mdutil.heading_classes(lines[h]))
        explicit = keys is not None
        if keys is None and heuristics:
            keys = heading_languages(text)
        if keys:
            scope(h, _section_end(lines, mask, h), "heading", text, keys,
                  explicit)

    for i, line in enumerate(lines):
        if mask[i]:
            continue
        m = _ADMONITION_RE.match(line)
        if m is None:
            continue
        title = m.group("title") or ""
        keys = class_languages(m.group("types").split())
        if keys is not None:
            scope(i, _block_end(lines, mask, i), "admonition",
                  title or m.group("types").strip(), keys, True)
            continue
        if not heuristics:
            continue
        keys = only_title_languages(title)
        if not keys:
            continue
        lead = _leading_heading(lines, mask, i)
        if lead is not None:
            # "Python only" opening a section marks the whole section.
            scope(lead, _section_end(lines, mask, lead), "section aside",
                  title, keys, False)
        else:
            scope(i, _block_end(lines, mask, i), "admonition", title, keys,
                  False)

    out: list[str] = []
    origin: list[int] = list(range(1, base + 1))
    after_removal = False
    i = 0
    while i < len(lines):
        if drop[i]:
            after_removal = True
            i += 1
            continue
        banner = rewrites.get(i)
        if banner is not None:
            new = support.filter_banner(lines[banner.start:banner.end], lang)
            out.extend(new)
            origin.extend(
                base + min(banner.start + k, banner.end - 1) + 1
                for k in range(len(new)))
            after_removal = False
            i = banner.end
            continue
        if mdutil.is_blank(lines[i]):
            # Collapse the blank run a removal leaves between its neighbours.
            if after_removal and out and mdutil.is_blank(out[-1]):
                i += 1
                continue
        else:
            after_removal = False
        out.append(lines[i])
        origin.append(base + i + 1)
        i += 1
    removals.sort(key=lambda r: r.line)
    return fm + "\n".join(out), removals, origin
