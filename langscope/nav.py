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

"""Scopes the mkdocs nav tree into per-language subtrees, pruning empties."""
from __future__ import annotations

from langscope.config import LANGUAGES


def is_scopable(src_uri: str) -> bool:
    """Reports whether a source URI gets a per-language scoped copy."""
    return (
        src_uri.endswith(".md")
        and src_uri != "index.md"
        and not src_uri.startswith(("_includes/", "api-reference/"))
    )


def _scope_path(
    path: str, supported: dict[str, frozenset[str]], lang: str
) -> str | None:
    """Prefixes a path with the language slug, or None if unsupported."""
    if "://" in path or not is_scopable(path):
        return path  # external link, .html, index.md, api-reference -> as-is
    langs = supported.get(path)
    if langs is not None and lang not in langs:
        return None
    return f"{lang}/{path}"


def _scope_item(item, supported, lang):
    """Scopes one nav entry (string, page, or section), pruning if empty."""
    if isinstance(item, str):
        return _scope_path(item, supported, lang)
    (title, value), = item.items()
    if isinstance(value, list):
        children = scope_nav(value, supported, lang)
        return {title: children} if children else None
    scoped = _scope_path(value, supported, lang)
    return {title: scoped} if scoped is not None else None


def scope_nav(items: list, supported: dict[str, frozenset[str]], lang: str) -> list:
    """Scopes a nav item list for one language, dropping pruned entries."""
    out = []
    for item in items:
        scoped = _scope_item(item, supported, lang)
        if scoped is not None:
            out.append(scoped)
    return out


def build_multilang_nav(
    nav: list,
    supported: dict[str, frozenset[str]],
    languages: list[str] | None = None,
) -> list:
    """Builds the top-level nav: Home, then one scoped section per language.

    ``languages`` limits the sections to those keys (default: all).
    """
    home = nav[0]
    rest = nav[1:]
    result = [home]
    for language in LANGUAGES:
        if languages is not None and language.key not in languages:
            continue
        result.append({language.label: scope_nav(rest, supported, language.key)})
    return result
