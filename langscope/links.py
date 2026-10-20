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

"""Rewrites a scoped page's internal links to absolute, scoped URLs.

A generated page lives one directory deeper than its source, so relative
links would break; flat root-absolute links (``/agents/``) would bounce
through a redirect stub into the default language. Both are rewritten to
``/<lang>/...`` when they resolve to a scoped page, falling back to another
language when the target page does not exist in this one.
"""
from __future__ import annotations

import posixpath
import re

from langscope import config, mdutil
from langscope.config import DEFAULT_LANGUAGE
from langscope.nav import is_scopable

_MD_LINK_RE = re.compile(r"(\]\()\s*([^)\s]+)")
_REF_DEF_RE = re.compile(r"^([ \t]*\[[^\]]+\]:[ \t]+)(\S+)(.*)$")
_HTML_ATTR_RE = re.compile(r'\b(src|href)\s*=\s*(["\'])(.*?)\2')
_CODE_SPAN_RE = re.compile(r"(`+)(?:.+?)\1")
# Leave these untouched: scheme:, //host, #anchor, data:
_LEAVE_RE = re.compile(r"^(?:[a-z][a-z0-9+.\-]*:|//|#)", re.IGNORECASE)


def pick_language(target_uri: str, lang: str, supported: dict) -> str:
    """The language to link ``target_uri`` in from a page in ``lang``."""
    langs = supported.get(target_uri)
    if langs is None or lang in langs:
        return lang
    if DEFAULT_LANGUAGE in langs:
        return DEFAULT_LANGUAGE
    for key in config.ORDERED_KEYS:
        if key in langs:
            return key
    return DEFAULT_LANGUAGE


def md_to_dir_url(path: str) -> str:
    """'agents/index.md'->'agents/', 'agents/foo.md'->'agents/foo/', 'index.md'->''."""
    no_ext = path.removesuffix(".md")
    if no_ext == "index":
        return ""
    if no_ext.endswith("/index"):
        return no_ext[: -len("index")]
    return no_ext + "/"


def resolve_source(path: str, supported: dict, aliases: dict) -> str | None:
    """Maps a docs-relative path or directory URL to a scoped source page.

    ``aliases`` maps retired source paths to their replacements (the manual
    redirect map), so links to old URLs land on the new page directly.
    """
    if path.endswith(".md"):
        candidates = [path]
    else:
        # Directory names may hold dots ("2.0/"); assets never match a page.
        stem = path.rstrip("/")
        if not stem:
            return None
        candidates = [f"{stem}.md", f"{stem}/index.md"]
    for candidate in candidates:
        if candidate in supported:
            return candidate
        alias = aliases.get(candidate, "").partition("#")[0]
        if alias in supported:
            return alias
    return None


def _rewrite_target(
    raw: str, source_uri: str, lang: str, supported: dict, aliases: dict,
    foreign: dict | None = None,
) -> str:
    if raw.startswith("#") and foreign and raw[1:] in foreign:
        # The section exists only in other languages' views of this page.
        langs = (supported.get(source_uri, frozenset()) & foreign[raw[1:]]
                 or foreign[raw[1:]])
        use = pick_language(source_uri, "", {source_uri: langs})
        return f"/{use}/{md_to_dir_url(source_uri)}{raw}"
    if _LEAVE_RE.match(raw):
        return raw
    frag = ""
    m = re.search(r"[#?]", raw)
    if m:
        frag = raw[m.start():]
        raw = raw[: m.start()]
    if not raw:
        return frag
    if raw.startswith("/"):
        path = posixpath.normpath(raw).lstrip("/")
        if raw.endswith("/") and path not in ("", "."):
            path += "/"
        if path.split("/", 1)[0] in config.ALL_KEYS:
            return raw + frag  # Already scoped.
        target = resolve_source(path, supported, aliases)
        if target is None:
            return raw + frag  # Not a scoped page: an asset, API reference...
    else:
        # MkDocs resolves links to files against the source file, but a
        # directory URL such as ``../agents/`` is left for the browser to
        # resolve against the page URL.
        is_file = not raw.endswith("/") and "." in posixpath.basename(raw)
        base = posixpath.dirname(source_uri) if is_file else md_to_dir_url(source_uri)
        path = posixpath.normpath(posixpath.join(base, raw)).lstrip("/")
        if path == ".":
            path = ""
        if raw.endswith("/") and path:
            path += "/"
        target = resolve_source(path, supported, aliases)
        if target is None:
            if path.endswith(".md"):
                return "/" + md_to_dir_url(path) + frag
            return "/" + path + frag
    if not is_scopable(target):
        return "/" + md_to_dir_url(target) + frag
    use = pick_language(target, lang, supported)
    return f"/{use}/{md_to_dir_url(target)}{frag}"


def _rewrite_segment(text: str, source_uri, lang, supported, aliases, foreign) -> str:
    def target(raw: str) -> str:
        return _rewrite_target(raw, source_uri, lang, supported, aliases, foreign)

    text = _MD_LINK_RE.sub(lambda m: m.group(1) + target(m.group(2)), text)
    return _HTML_ATTR_RE.sub(
        lambda m: f"{m.group(1)}={m.group(2)}{target(m.group(3))}{m.group(2)}",
        text,
    )


def _rewrite_line(line: str, source_uri, lang, supported, aliases, foreign) -> str:
    ref = _REF_DEF_RE.match(line)
    if ref:
        return (
            ref.group(1)
            + _rewrite_target(
                ref.group(2), source_uri, lang, supported, aliases, foreign)
            + ref.group(3)
        )
    # Rewrite only outside inline code spans.
    out: list[str] = []
    cursor = 0
    for span in _CODE_SPAN_RE.finditer(line):
        out.append(_rewrite_segment(
            line[cursor:span.start()], source_uri, lang, supported, aliases,
            foreign))
        out.append(span.group(0))
        cursor = span.end()
    out.append(_rewrite_segment(
        line[cursor:], source_uri, lang, supported, aliases, foreign))
    return "".join(out)


def rewrite_links(
    markdown: str,
    source_uri: str,
    lang: str,
    supported: dict,
    aliases: dict | None = None,
    foreign_anchors: dict | None = None,
) -> str:
    """Rewrites the internal links of ``source_uri``'s view in ``lang``.

    ``foreign_anchors`` maps in-page anchors that this view lost (their
    section belongs to other languages) to those languages; links to them
    point at a language view that still has the section.
    """
    aliases = aliases or {}
    lines = markdown.split("\n")
    mask = mdutil.code_mask(lines)
    out = [
        line if mask[i] else _rewrite_line(
            line, source_uri, lang, supported, aliases, foreign_anchors)
        for i, line in enumerate(lines)
    ]
    return "\n".join(out)
