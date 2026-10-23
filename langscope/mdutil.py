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

"""Line-level Markdown helpers shared by the langscope passes."""
from __future__ import annotations

import re

import yaml
from markdown.extensions.toc import slugify

_FENCE_OPEN_RE = re.compile(r"^[ \t]*(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
_HEADING_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<hashes>#{1,6})[ \t]+(?P<text>.*?)[ \t#]*$")
_ATTR_LIST_RE = re.compile(r"\s*\{[^}]*\}\s*$")
_EXPLICIT_ID_RE = re.compile(r"\{[^}]*#(?P<id>[\w-]+)[^}]*\}\s*$")
_INLINE_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_FRONTMATTER_RE = re.compile(r"\A---[ \t]*\n(?P<body>.*?\n)?---[ \t]*(?:\n|\Z)", re.DOTALL)


class FenceTracker:
    """Tracks whether successive lines sit inside a fenced code block.

    Fences are recognised at any indentation, so code blocks nested in lists,
    admonitions and content tabs count too. A fence closes on a line holding
    only the same fence character, at least as many times as it opened.
    """

    def __init__(self) -> None:
        self._fence: str | None = None

    @property
    def inside(self) -> bool:
        return self._fence is not None

    def feed(self, line: str) -> bool:
        """Consumes a line; returns True if it is code or a fence delimiter."""
        if self._fence is None:
            m = _FENCE_OPEN_RE.match(line)
            if m is None:
                return False
            if m.group("fence")[0] == "`" and "`" in m.group("info"):
                return False  # Inline code such as ```x``` is not a fence.
            self._fence = m.group("fence")
            return True
        stripped = line.strip()
        char = self._fence[0]
        if len(stripped) >= len(self._fence) and stripped == char * len(stripped):
            self._fence = None
        return True


def code_mask(lines: list[str]) -> list[bool]:
    """Returns, per line, whether it is fenced code (delimiters included)."""
    tracker = FenceTracker()
    return [tracker.feed(line) for line in lines]


def indent_len(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def is_blank(line: str) -> bool:
    return line.strip() == ""


def heading(line: str) -> tuple[int, int, str] | None:
    """Returns (indent, level, text) for an ATX heading line, else None.

    Any trailing ``{#id .class}`` attribute list is dropped from the text.
    """
    m = _HEADING_RE.match(line)
    if m is None:
        return None
    text = _ATTR_LIST_RE.sub("", m.group("text")).strip()
    return len(m.group("indent")), len(m.group("hashes")), text


def heading_classes(line: str) -> list[str]:
    """The ``.class`` names in a heading's trailing attribute list."""
    if heading(line) is None:
        return []
    m = _ATTR_LIST_RE.search(line.rstrip(" \t#"))
    if m is None:
        return []
    return re.findall(r"(?<![\w-])\.([\w-]+)", m.group(0))


def heading_id(line: str) -> str | None:
    """The anchor id a heading line gets: its ``{#id}``, else the TOC slug.

    Approximates Python-Markdown's toc slugify on the source text, which is
    enough to match the ids that in-page links use.
    """
    h = heading(line)
    if h is None:
        return None
    m = _EXPLICIT_ID_RE.search(line)
    if m:
        return m.group("id")
    text = _INLINE_LINK_RE.sub(r"\1", h[2]).replace("`", "")
    return slugify(text, "-") or None


def split_frontmatter(markdown: str) -> tuple[str, str]:
    """Splits a page into (frontmatter block including fences, body)."""
    m = _FRONTMATTER_RE.match(markdown)
    if m is None:
        return "", markdown
    return markdown[: m.end()], markdown[m.end():]


def frontmatter(markdown: str) -> dict:
    """Parses the page's YAML frontmatter; {} when absent or not a mapping."""
    m = _FRONTMATTER_RE.match(markdown)
    if m is None or not m.group("body"):
        return {}
    try:
        data = yaml.safe_load(m.group("body"))
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}
