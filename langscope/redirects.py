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

"""Builds language-scoped redirect maps for the mkdocs-redirects plugin."""
from __future__ import annotations

from langscope import config
from langscope.config import DEFAULT_LANGUAGE
from langscope.nav import is_scopable


def target_language(
    uri: str, supported: dict, languages: frozenset[str] | None = None
) -> str | None:
    """Picks the language a flat URI redirects to: the default, else the first.

    Only ``languages`` (default: all) are candidates; None when the page is
    in none of them.
    """
    active = config.ALL_KEYS if languages is None else languages
    langs = supported.get(uri, config.ALL_KEYS) & active
    if DEFAULT_LANGUAGE in langs:
        return DEFAULT_LANGUAGE
    for key in config.ORDERED_KEYS:
        if key in langs:
            return key
    return None


def build_redirect_map(
    scopable_uris: list[str],
    existing: dict[str, str],
    supported: dict,
    languages: frozenset[str] | None = None,
) -> dict[str, str]:
    """Maps each flat URI (and existing redirect) to its scoped destination.

    Destinations that exist in none of ``languages`` are left out, so a build
    limited to some languages does not point redirects at missing pages.
    """
    out: dict[str, str] = {}
    for uri in scopable_uris:
        lang = target_language(uri, supported, languages)
        if lang is not None:
            out[uri] = f"{lang}/{uri}"
    for src, dest in existing.items():
        path = dest.partition("#")[0]
        if "://" in dest or not is_scopable(path):
            out[src] = dest
            continue
        lang = target_language(path, supported, languages)
        if lang is not None:
            out[src] = f"{lang}/{dest}"
    return out
