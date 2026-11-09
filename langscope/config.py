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

"""The SDK languages, and how docs name them in tab labels and titles.

This module is the single source of truth for the language list: the hook
publishes it to templates as ``config.extra.langscope`` and the browser
scripts read it back from the rendered switcher.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Lang:
    key: str  # Also the URL scope: /<key>/...
    label: str  # Display name, and the canonical spelling in prose.
    aliases: tuple[str, ...] = ()  # Other spellings seen in tab labels.


LANGUAGES: list[Lang] = [
    Lang("python", "Python"),
    Lang("typescript", "TypeScript", ("ts", "javascript", "js")),
    Lang("go", "Go", ("golang",)),
    Lang("java", "Java"),
    Lang("kotlin", "Kotlin"),
]

DEFAULT_LANGUAGE: str = "python"

ALL_KEYS: frozenset[str] = frozenset(lang.key for lang in LANGUAGES)

# Language keys in declared (fallback-priority) order.
ORDERED_KEYS: tuple[str, ...] = tuple(lang.key for lang in LANGUAGES)

LABELS: dict[str, str] = {lang.key: lang.label for lang in LANGUAGES}

# Every spelling, lowercased, mapped to its language key.
_ALIASES: dict[str, str] = {}
for _lang in LANGUAGES:
    for _name in (_lang.key, _lang.label, *_lang.aliases):
        _ALIASES[_name.lower()] = _lang.key

# Longest first so "javascript" wins over "java" and "golang" over "go".
_TOKEN = "|".join(
    re.escape(name) for name in sorted(_ALIASES, key=len, reverse=True)
)
# A run of language names at the start of a label, joined by "/", ",", "&" or
# "and": "Python", "JavaScript / TypeScript", "Python and Go". A qualifier may
# follow only after punctuation ("Python - adk CLI", "Python (Discord)"), so a
# label such as "Go further" is not mistaken for a language tab.
_LEADING_RE = re.compile(
    rf"^\s*(?P<run>(?:{_TOKEN})(?:\s*(?:/|,|&|\band\b)\s*(?:{_TOKEN}))*)"
    rf"(?![\w+#])(?P<rest>(?:\s*[-\u2013\u2014:(/|,].*)?)\s*$",
    re.IGNORECASE | re.DOTALL,
)
_TOKEN_RE = re.compile(rf"(?<![\w]){_TOKEN}(?![\w+#])", re.IGNORECASE)

def parse_label(label: str) -> tuple[frozenset[str], str]:
    """Splits a tab label into the languages it leads with and the remainder.

    ``"Python"`` -> ({python}, ""); ``"Python - adk CLI"`` -> ({python},
    "adk CLI"); ``"JavaScript / TypeScript (Telegram)"`` -> ({typescript},
    "Telegram"); ``"Maven"`` -> (frozenset(), "Maven").
    """
    m = _LEADING_RE.match(label)
    if not m:
        return frozenset(), label.strip()
    keys = frozenset(
        _ALIASES[tok.lower()] for tok in _TOKEN_RE.findall(m.group("run"))
    )
    rest = m.group("rest").strip()
    rest = rest.lstrip("-\u2013\u2014:/|, ").strip()
    if rest.startswith("(") and rest.endswith(")"):
        rest = rest[1:-1].strip()
    return keys, rest


def label_to_key(label: str) -> str | None:
    """Maps a label that is exactly one language name to its key, else None."""
    return _ALIASES.get(label.strip().lower())


def exact_label_keys(label: str) -> frozenset[str]:
    """Languages a label consists of entirely ("Python", "Java / Kotlin")."""
    keys, rest = parse_label(label)
    return keys if keys and not rest else frozenset()
