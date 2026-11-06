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

"""Flattens content-tab groups down to one language's view.

A tab group is a language group when any tab label leads with a language
name ("Python", "Python - adk CLI", "JavaScript / TypeScript"). In a
language's view such a group keeps the tabs for that language plus any
language-neutral tabs: one survivor is spliced in as plain content, several
stay a tab group with the language prefix trimmed from their labels. Groups
with no language label are kept as tabs, but their bodies are still flattened
so language groups nested inside them are scoped too.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from langscope import mdutil
from langscope.config import LABELS, ORDERED_KEYS, parse_label

# `===+` selects a tab by default; `===!` starts a new group even right after
# another tab.
TAB_RE = re.compile(
    r'^(?P<indent>[ \t]*)===(?P<flags>[+!]{0,2}) +"(?P<label>[^"]*)"[ \t]*$')

# Python-Markdown expands tabs to this many columns, and tab content must be
# indented by this much more than its `=== "..."` marker.
TAB_LENGTH = 4


def _expand_indent(line: str) -> str:
    """Expands tab characters in ``line``'s leading whitespace to spaces."""
    stripped = line.lstrip(" \t")
    return line[: len(line) - len(stripped)].expandtabs(TAB_LENGTH) + stripped


def _indent(line: str) -> int:
    """The column ``line``'s text starts at, with tabs expanded."""
    return mdutil.indent_len(_expand_indent(line))


@dataclass(frozen=True)
class Drop:
    """A language group that had nothing for the target language."""

    line: int  # 1-based line of the group's first tab marker.
    labels: tuple[str, ...]
    lead_in: str  # The nearest non-blank line above the group.
    placeholder: bool = False  # Whether a "not available" note replaced it.


def _placeholder(indent: str, lang: str, available: frozenset[str]) -> list[str]:
    """A note standing in for an example that has no ``lang`` version."""
    names = [LABELS[k] for k in ORDERED_KEYS if k in available]
    listed = names[0] if len(names) == 1 else (
        ", ".join(names[:-1]) + " and " + names[-1])
    return [
        f'{indent}!!! note "Not yet available for {LABELS[lang]}"',
        "",
        (f"{indent}    This example has no {LABELS[lang]} version yet. It is "
         f"available for {listed}; switch SDK at the top of the page to see it."),
        "",
    ]


def _dedent_body(body: list[str], indent_len: int) -> list[str]:
    """Removes four spaces of tab-content indentation, preserving nesting."""
    prefix = " " * (indent_len + TAB_LENGTH)
    out: list[str] = []
    for line in body:
        if line.strip() == "":
            out.append("")
            continue
        if "\t" in line[: len(line) - len(line.lstrip(" \t"))]:
            line = _expand_indent(line)
        out.append(line[TAB_LENGTH:] if line.startswith(prefix) else line)
    return out


def _note_anchors(body: list[str], keys: frozenset[str], anchors: dict) -> None:
    """Records the heading ids in a discarded tab body, with its languages."""
    mask = mdutil.code_mask(body)
    for k, line in enumerate(body):
        if not mask[k]:
            anchor = mdutil.heading_id(line.strip())
            if anchor:
                anchors[anchor] = anchors.get(anchor, frozenset()) | keys


def _flatten_lines(
    lines: list[str], lang: str, drops: list[Drop], offset: int,
    anchors: dict | None = None,
) -> list[str]:
    if anchors is None:
        anchors = {}
    out: list[str] = []
    i = 0
    n = len(lines)
    fences = mdutil.FenceTracker()
    while i < n:
        line = lines[i]
        # Inside a fenced code block, `=== "..."` is ordinary text.
        m = None if fences.inside else TAB_RE.match(line)
        if not m:
            fences.feed(line)
            out.append(line)
            i += 1
            continue

        group_line = i
        indent_len = _indent(line)
        group: list[tuple[str, str, list[str], int]] = []
        while i < n:
            mm = TAB_RE.match(lines[i])
            if not mm or _indent(lines[i]) != indent_len or (
                    group and "!" in mm.group("flags")):
                break
            # The marker up to its label, keeping any `+`/`!` flags.
            indent = mm.group("indent") + "===" + mm.group("flags")
            label = mm.group("label")
            body_start = i + 1
            i += 1
            # Like pymdownx.tabbed (and Python-Markdown's detab), the body ends
            # at the first non-blank line indented less than the marker plus
            # four columns; such a line is shared content after the group.
            while i < n and (
                lines[i].strip() == ""
                or _indent(lines[i]) >= indent_len + TAB_LENGTH
            ):
                i += 1
            group.append((indent, label, lines[body_start:i], offset + body_start))

        parsed = [(parse_label(lbl), (ind, lbl, body, at)) for ind, lbl, body, at in group]
        if not any(keys for (keys, _), _ in parsed):
            for _, (ind, lbl, body, at) in parsed:
                out.append(f'{ind} "{lbl}"')
                out.extend(_flatten_lines(body, lang, drops, at, anchors))
            continue

        for (keys, _), (_, _, body, _) in parsed:
            if keys and lang not in keys:
                _note_anchors(body, keys, anchors)
        kept = [
            (rest, tab) for (keys, rest), tab in parsed if not keys or lang in keys
        ]
        if not any(lang in keys for (keys, _), _ in parsed):
            lead_in = next(
                (ln.strip() for ln in reversed(out) if ln.strip()), ""
            )
            # Prose that introduces the example ("...the following output:")
            # would dangle; say the example is missing instead.
            dangling = all(keys for (keys, _), _ in parsed) and lead_in.endswith(":")
            drops.append(Drop(
                offset + group_line + 1, tuple(lbl for _, lbl, _, _ in group),
                lead_in, dangling))
            if dangling:
                available = frozenset().union(*(keys for (keys, _), _ in parsed))
                out.extend(_placeholder(m.group("indent"), lang, available))
            if all(keys for (keys, _), _ in parsed):
                continue

        if len(kept) == 1:
            _, (_, _, body, at) = kept[0]
            spliced = _flatten_lines(
                _dedent_body(body, indent_len), lang, drops, at, anchors)
            # The blank line before the tab marker already separates this block
            # from the preceding content; drop the block's own leading blanks,
            # but keep trailing blanks so it stays apart from what follows.
            while spliced and spliced[0] == "":
                spliced.pop(0)
            out.extend(spliced)
            continue

        for rest, (ind, lbl, body, at) in kept:
            out.append(f'{ind} "{rest or lbl}"')
            out.extend(_flatten_lines(body, lang, drops, at, anchors))

    return out


def flatten_with_report(
    markdown: str, lang: str
) -> tuple[str, list[Drop], dict[str, frozenset[str]]]:
    """Flattens ``markdown`` for ``lang``.

    Also returns the language groups that had no tab for ``lang``, and the
    heading anchors that only other languages' tabs held (anchor ->
    languages), so links to them can point at a view that has them.
    """
    drops: list[Drop] = []
    anchors: dict[str, frozenset[str]] = {}
    out = _flatten_lines(markdown.splitlines(), lang, drops, 0, anchors)
    return "\n".join(out).strip("\n") + "\n", drops, anchors


def flatten(markdown: str, lang: str) -> str:
    """Flattens ``markdown`` for ``lang``."""
    return flatten_with_report(markdown, lang)[0]
