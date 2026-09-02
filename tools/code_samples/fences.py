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

"""Pull fenced code blocks out of the documentation.

Blocks are frequently nested inside tabbed sections, so a fence can be indented
by four or eight columns, and its body carries that indentation on every line.
Both are handled here so the rest of the tooling sees the code as an author
wrote it.
"""

from __future__ import annotations

import dataclasses
import pathlib
import re

FENCE = re.compile(r"^(?P<indent>[ \t]*)(?P<ticks>`{3,}|~{3,})(?P<info>.*)$")
SNIPPET_INCLUDE = "--8<--"


def _columns(text: str, upto: int) -> int:
    """Display width of the first `upto` characters, tabs expanding to four."""
    col = 0
    for ch in text[:upto]:
        col = col + (4 - col % 4) if ch == "\t" else col + 1
    return col


@dataclasses.dataclass(frozen=True)
class Fence:
    """One fenced code block."""

    path: pathlib.Path
    start_line: int  # 1-based line of the opening fence
    language: str
    body: tuple[str, ...]  # dedented to column zero

    @property
    def text(self) -> str:
        return "\n".join(self.body)

    @property
    def is_pointer(self) -> bool:
        """True when the block only pulls in an external snippet file."""
        lines = [line for line in self.body if line.strip()]
        return bool(lines) and all(l.startswith(SNIPPET_INCLUDE) for l in lines)


def _dedent(body: list[str], indent: str) -> list[str]:
    """Strip the fence's own indentation, never the code's."""
    width = _columns(indent, len(indent))
    if not width:
        return body
    out = []
    for line in body:
        cut = 0
        while cut < len(line) and line[cut] in " \t" and _columns(line, cut + 1) <= width:
            cut += 1
        out.append(line[cut:])
    return out


def parse(path: pathlib.Path) -> list[Fence]:
    """Return every fenced block in one markdown file."""
    lines = path.read_text(encoding="utf-8").split("\n")
    fences: list[Fence] = []
    i = 0
    while i < len(lines):
        opening = FENCE.match(lines[i])
        if not opening or opening.group("ticks")[0] in opening.group("info"):
            i += 1
            continue
        indent, ticks = opening.group("indent"), opening.group("ticks")

        # A closing fence sits at the same indentation. A more deeply indented
        # run of backticks is content, which is how a sample that quotes fenced
        # markdown inside a string survives intact.
        close = None
        j = i + 1
        while j < len(lines):
            line = lines[j]
            if line.startswith(indent):
                rest = line[len(indent):].rstrip()
                if rest and set(rest) == {ticks[0]} and len(rest) >= len(ticks):
                    close = j
                    break
            j += 1
        if close is None:
            i += 1
            continue

        body = lines[i + 1 : close]
        # Another fence opening at this indentation means the block was never
        # closed cleanly and any boundary here is a guess, so skip it.
        ambiguous = any(
            (m := FENCE.match(l)) and m.group("indent") == indent and m.group("info").strip()
            for l in body
        )
        if not ambiguous:
            info = opening.group("info").strip()
            language = info.split(" ", 1)[0].split("{", 1)[0].strip().lower()
            fences.append(
                Fence(
                    path=path,
                    start_line=i + 1,
                    language=language,
                    body=tuple(_dedent(body, indent)),
                )
            )
        i = close + 1
    return fences


def resolve_includes(text: str, root: pathlib.Path, depth: int = 0) -> str:
    """Expand `--8<--` snippet includes so a block can be read as real code."""
    if depth > 5:
        return text
    section_marker = re.compile(r"--8<--\s+\[(start|end):([^\]]+)\]")
    include = re.compile(r'^(?P<indent>\s*)--8<--\s+"(?P<spec>[^"]+)"\s*$')

    out: list[str] = []
    for line in text.split("\n"):
        m = include.match(line)
        if not m:
            if not section_marker.search(line):
                out.append(line)
            continue
        target, _, section = m.group("spec").partition(":")
        ref = root / target
        if not ref.is_file():
            out.append(line)
            continue
        inner = ref.read_text(encoding="utf-8").split("\n")
        if section:
            picked, inside = [], False
            for l in inner:
                sm = section_marker.search(l)
                if sm and sm.group(2).strip() == section.strip():
                    inside = sm.group(1) == "start"
                    continue
                if inside:
                    picked.append(l)
            inner = picked
        expanded = resolve_includes("\n".join(inner), root, depth + 1).split("\n")
        pad = m.group("indent")
        out.extend(pad + l if l.strip() else l for l in expanded)
    return "\n".join(out)
