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

"""Generates per-language documentation views from single-source pages.

Every scopable page is emitted once per SDK it supports, under
``/<language>/...``, with content tabs flattened, other languages' sections
dropped and links rewritten. The flat URLs become redirect stubs that pick
the reader's saved language.

Set ``MKDOCS_LANGSCOPE_LANGUAGES=python,go`` to build only some languages,
for a faster local loop (``MKDOCS_LANGSCOPE_SKIP=1`` builds only the default
language).
"""
from __future__ import annotations

import dataclasses
import fnmatch
import json
import logging
import os
import posixpath
import shutil
import sys
from pathlib import Path, PurePosixPath

# Hooks are loaded by path, not as a package; make the repo root (parent of
# this file's directory) importable so ``import langscope`` resolves.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mkdocs.exceptions import PluginError
from mkdocs.plugins import event_priority
from mkdocs.structure.files import File

from langscope import config as lsconfig
from langscope import flatten as flattenmod
from langscope import links as linksmod
from langscope import mdutil
from langscope import nav as navmod
from langscope import redirects as redirectsmod
from langscope import sections as sectionsmod
from langscope import support as supportmod

log = logging.getLogger("mkdocs.hooks.language_scope")

LANGUAGES_ENV = "MKDOCS_LANGSCOPE_LANGUAGES"
SKIP_ENV = "MKDOCS_LANGSCOPE_SKIP"  # "1": shorthand for the default language.

# Per-build state, reset in on_config.
ACTIVE: list[str] = []  # Language keys built, in declared order.
SUPPORTED: dict[str, frozenset[str]] = {}  # Source URI -> languages built.
# Source URI -> all its languages. Links use this so a build limited to some
# languages still links other-language pages where the full site has them.
ALL_SUPPORTED: dict[str, frozenset[str]] = {}
ALIASES: dict[str, str] = {}  # Retired source URI -> replacement (manual map).
REDIRECTS: dict[str, str] = {}  # Flat source URI -> scoped destination.
GEN_TO_SRC: dict[str, str] = {}  # Generated URI -> source URI.
LLMS_SECTIONS: dict[str, list[str]] = {}  # As authored in mkdocs.yml.
PAGE_TITLES: dict[str, str] = {}  # Rendered page src URI -> title.
LANG_SECTIONS: dict[str, object] = {}  # Language key -> its nav Section.


def active_languages() -> list[str]:
    """The languages to build, from ``MKDOCS_LANGSCOPE_LANGUAGES`` or all."""
    raw = os.environ.get(LANGUAGES_ENV, "").strip()
    if not raw and os.environ.get(SKIP_ENV) == "1":
        raw = lsconfig.DEFAULT_LANGUAGE
    if not raw:
        return list(lsconfig.ORDERED_KEYS)
    keys = []
    for item in raw.split(","):
        key = lsconfig.label_to_key(item)
        if key is None:
            raise PluginError(
                f"{LANGUAGES_ENV} names unknown language {item.strip()!r}; "
                f"expected some of {', '.join(lsconfig.ORDERED_KEYS)}."
            )
        keys.append(key)
    return [k for k in lsconfig.ORDERED_KEYS if k in keys]


def _scan_supported(docs_dir: str, exclude) -> dict[str, frozenset[str]]:
    root = Path(docs_dir)
    result: dict[str, frozenset[str]] = {}
    for path in root.rglob("*.md"):
        uri = path.relative_to(root).as_posix()
        if not navmod.is_scopable(uri):
            continue
        if exclude is not None and exclude.match_file(uri):
            continue
        text = path.read_text(encoding="utf-8")
        try:
            result[uri] = supportmod.supported_languages(text)
        except ValueError as error:
            raise PluginError(f"{uri}: {error}") from error
    return result


def _sort_key(uri: str):
    """MkDocs' file order: a directory's index first, subdirectories after."""
    parts = PurePosixPath(uri).parts
    return (parts[:-1], parts[-1] != "index.md", parts[-1])


def on_config(config):
    ACTIVE[:] = active_languages()
    active = frozenset(ACTIVE)
    for state in (SUPPORTED, ALL_SUPPORTED, ALIASES, REDIRECTS, GEN_TO_SRC, LLMS_SECTIONS,
                  PAGE_TITLES, LANG_SECTIONS):
        state.clear()

    scanned = _scan_supported(config["docs_dir"], config.get("exclude_docs"))
    ALL_SUPPORTED.update(scanned)
    # Languages outside the build are invisible to every pass below.
    SUPPORTED.update({uri: langs & active for uri, langs in scanned.items()})

    config["nav"] = navmod.build_multilang_nav(config["nav"], SUPPORTED, ACTIVE)

    redirects_plugin = config["plugins"].get("redirects")
    if redirects_plugin is not None:
        existing = dict(redirects_plugin.config.get("redirect_maps") or {})
        ALIASES.update(existing)
        REDIRECTS.update(redirectsmod.build_redirect_map(
            sorted(SUPPORTED), existing, SUPPORTED, active))
        redirects_plugin.config["redirect_maps"] = dict(REDIRECTS)

    llms_plugin = config["plugins"].get("llmstxt")
    if llms_plugin is not None:
        LLMS_SECTIONS.update(llms_plugin.config["sections"])
        # Have the plugin convert every generated page (for the "View as
        # Markdown" buttons) plus the unscoped pages the sections name;
        # on_post_build then writes the per-language indexes.
        pages = [f"{lang}/{uri}" for uri in sorted(SUPPORTED, key=_sort_key)
                 for lang in ACTIVE if lang in SUPPORTED[uri]]
        for entries in LLMS_SECTIONS.values():
            for entry in entries:
                name = next(iter(entry)) if isinstance(entry, dict) else entry
                if "*" not in name and not navmod.is_scopable(name):
                    pages.append(name)
        llms_plugin.config["sections"] = {"Pages": pages}

    config["extra"]["langscope"] = {
        "default": lsconfig.DEFAULT_LANGUAGE,
        "lang_keys": list(ACTIVE),
        "languages": [
            {"key": key, "label": lsconfig.LABELS[key]} for key in ACTIVE
        ],
    }
    return config


def _report(uri: str, lang: str, drops, removals) -> None:
    label = lsconfig.LABELS[lang]
    if drops:
        lines = ", ".join(
            f"{d.line}{' (placeholder note)' if d.placeholder else ''}"
            for d in drops)
        log.info(
            "language_scope: %s: %d tab group(s) with no %s tab left out of "
            "the %s view, at line %s", uri, len(drops), label, label, lines,
        )
    for r in removals:
        names = ", ".join(lsconfig.LABELS[k] for k in lsconfig.ORDERED_KEYS
                          if k in r.languages)
        rule = "marker" if r.explicit else "heuristic"
        if r.kept:
            log.info(
                "language_scope: %s: line %d: %s %r (%s) names only %s, none of "
                "the page's languages; kept in every view", uri, r.line,
                r.kind, r.what, rule, names)
        else:
            log.info(
                "language_scope: %s: line %d: %s %r (%s, for %s) left out of "
                "the %s view", uri, r.line, r.kind, r.what, rule, names, label)


@dataclasses.dataclass
class _Stats:
    tab_groups: int = 0
    sections: int = 0  # Section and admonition removals, per view.
    kept: int = 0
    orphans: int = 0  # Source spans that reach no view.


STATS = _Stats()


def scope_content(text: str, lang: str, page_languages: frozenset[str]):
    """Scopes a page's content to ``lang``, before links are rewritten.

    Returns (text, drops, removals, foreign anchors).
    """
    # Sections first, so tab groups inside removed sections are not reported.
    content = supportmod.scope_page_banners(text, lang)
    content, removals, origin = sectionsmod.scope_sections_mapped(
        content, lang, page_languages)
    content, drops, foreign = flattenmod.flatten_with_report(content, lang)
    drops = [
        dataclasses.replace(d, line=origin[d.line - 1] if d.line <= len(origin) else d.line)
        for d in drops
    ]
    for removal in removals:
        for anchor in removal.anchors:
            foreign[anchor] = foreign.get(anchor, frozenset()) | removal.languages
    return content, drops, removals, foreign


def render_scoped(text: str, uri: str, lang: str,
                  page_languages: frozenset[str] | None = None):
    """Builds one language's view of a source page.

    Returns (text, drops, removals, text before link rewriting).
    """
    if page_languages is None:
        page_languages = ALL_SUPPORTED.get(uri, lsconfig.ALL_KEYS)
    content, drops, removals, foreign = scope_content(
        text, lang, page_languages)
    # An anchor some remaining heading still provides is not lost.
    lines = content.split("\n")
    mask = mdutil.code_mask(lines)
    for i, line in enumerate(lines):
        if not mask[i]:
            foreign.pop(mdutil.heading_id(line.strip()), None)
    linked = linksmod.rewrite_links(
        content, uri, lang, ALL_SUPPORTED, ALIASES, foreign)
    return linked, drops, removals, content


def orphaned_spans(source: str, views: list[str]) -> list[tuple[int, int, str]]:
    """Source spans whose text reaches none of ``views``.

    Compares stripped lines, ignoring blank lines, tab markers, support
    banners and lines without a letter or digit (fences, braces). Returns
    (first line, last line, first line's text) per span, 1-based. Lines that
    are compared and found keep two missing lines in separate spans.
    """
    seen: set[str] = set()
    for view in views:
        seen.update(line.strip() for line in view.split("\n"))
    fm, body = mdutil.split_frontmatter(source)
    base = fm.count("\n")
    lines = body.split("\n")
    skip = [False] * len(lines)
    for banner in supportmod.find_banners(lines):
        for k in range(banner.start, banner.end):
            skip[k] = True
    spans: list[tuple[int, int, str]] = []
    open_span = False
    for i, line in enumerate(lines):
        text = line.strip()
        if (skip[i] or not any(c.isalnum() for c in text)
                or flattenmod.TAB_RE.match(line)):
            continue
        if text in seen:
            open_span = False
        elif open_span:
            first, _, what = spans[-1]
            spans[-1] = (first, base + i + 1, what)
        else:
            spans.append((base + i + 1, base + i + 1, text))
            open_span = True
    return spans


# Run before other plugins (notably ``redirects`` and ``llmstxt``) so the
# generated per-language files exist when they snapshot the documentation pages.
@event_priority(100)
def on_files(files, config):
    stats = STATS
    stats.__init__()
    for uri, langs in SUPPORTED.items():
        src_file = files.get_file_from_path(uri)
        if src_file is None:
            continue
        text = src_file.content_string
        page_languages = ALL_SUPPORTED[uri]
        views = []
        for lang in ACTIVE:
            if lang not in langs:
                continue
            try:
                content, drops, removals, unlinked = render_scoped(
                    text, uri, lang, page_languages)
            except ValueError as error:
                raise PluginError(f"{uri}: {error}") from error
            views.append(unlinked)
            _report(uri, lang, drops, removals)
            stats.tab_groups += len(drops)
            stats.sections += sum(not r.kept for r in removals)
            stats.kept += sum(r.kept for r in removals)
            gen = File.generated(config, f"{lang}/{uri}", content=content)
            files.append(gen)
            GEN_TO_SRC[gen.src_uri] = uri
        files.remove(src_file)
        # Only a build with all of a page's languages can tell what no view has.
        if views and page_languages <= frozenset(ACTIVE):
            for first, last, what in orphaned_spans(text, views):
                stats.orphans += 1
                # A warning, so `mkdocs build --strict` fails: such content
                # is invisible on the site.
                log.warning(
                    "language_scope: %s: lines %d-%d reach no language view "
                    "(tabs or sections for languages the page does not "
                    "support?): %.70s", uri, first, last, what)

    log.info(
        "language_scope: generated %d pages in %s from %d sources. Left out "
        "of a view: %d tab groups with no tab for its language, %d sections "
        "or admonitions for other languages; %d language-specific sections "
        "kept because they name none of the page's languages; %d source "
        "spans reach no view (all listed above)",
        len(GEN_TO_SRC), ", ".join(ACTIVE), len(SUPPORTED), stats.tab_groups,
        stats.sections, stats.kept, stats.orphans,
    )
    return files


def _language_of(url: str) -> str | None:
    seg = url.split("/", 1)[0]
    return seg if seg in ACTIVE else None


def on_nav(nav, config, files):
    """Indexes each language's nav section and fixes shared pages' parents.

    Pages outside the language scopes (the API reference) sit in every
    language's nav, so MkDocs leaves them parented under the last language.
    Re-parent them under the default language, whose tabs they render with.
    """
    by_label = {lsconfig.LABELS[key]: key for key in ACTIVE}
    for item in nav.items:
        key = by_label.get(getattr(item, "title", None))
        if key is not None and item.is_section:
            LANG_SECTIONS[key] = item
    home = LANG_SECTIONS.get(lsconfig.DEFAULT_LANGUAGE) or next(
        iter(LANG_SECTIONS.values()), None)
    if home is not None:
        def reparent(section):
            for child in section.children:
                if child.is_page and _language_of(child.url) is None:
                    child.parent = section
                if child.is_section:
                    reparent(child)
        reparent(home)
    return nav


def on_page_context(context, page, config, nav):
    PAGE_TITLES[page.file.src_uri] = page.title or ""
    lang = _language_of(page.url)
    section = LANG_SECTIONS.get(lang or lsconfig.DEFAULT_LANGUAGE) or next(
        iter(LANG_SECTIONS.values()), None)
    if section is not None:
        # Tabs and sidebar render the active language's subtree only.
        context["langscope_nav"] = [nav.items[0], *section.children]
    if lang is not None:
        # Keep previous/next within the reader's language.
        if page.previous_page and _language_of(page.previous_page.url) != lang:
            page.previous_page = None
        if page.next_page and _language_of(page.next_page.url) != lang:
            page.next_page = None

    src = GEN_TO_SRC.get(page.file.src_uri)
    if src is None:
        return context
    # MkDocs' default canonical URL (site_url + page.url) is already the page
    # itself: every language view is distinct content, so none defers to
    # another. Only the edit link needs the real source path.
    edit_uri = config.get("edit_uri")
    repo_url = (config.get("repo_url") or "").rstrip("/")
    if edit_uri and repo_url:
        page.edit_url = f"{repo_url}/{edit_uri}{src}"
    return context


_STUB = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Redirecting...</title>
    <link rel="canonical" href="{canonical}">
    <meta name="robots" content="noindex">
    <script>
    (function () {{
      var langs = {langs}, pick = null;
      var tab = location.hash.slice(1).match(/^([a-z]+)(?:_\\d+)?$/);
      if (tab && langs.indexOf(tab[1]) >= 0) pick = tab[1];
      if (!pick) {{
        try {{
          var saved = localStorage.getItem("adk-lang");
          if (langs.indexOf(saved) >= 0) pick = saved;
        }} catch (e) {{}}
      }}
      location.replace("{root}" + (pick || "{default}") + "/{path}" +
        location.search + (location.hash || "{frag}"));
    }})();
    </script>
    <meta http-equiv="refresh" content="0; url={fallback}">
</head>
<body>
You're being redirected to a <a href="{fallback}">new destination</a>.
</body>
</html>
"""


def _stub_html(stub_dir: str, dest: str, site_url: str) -> str:
    """A redirect page to scoped ``dest`` that prefers the saved language."""
    lang, _, rest = dest.partition("/")
    target, _, frag = rest.partition("#")
    path = linksmod.md_to_dir_url(target)
    langs = [k for k in ACTIVE if k in SUPPORTED.get(target, frozenset())]
    depth = len([p for p in stub_dir.split("/") if p])
    root = "../" * depth
    fallback = f"{root}{lang}/{path}" + (f"#{frag}" if frag else "")
    return _STUB.format(
        canonical=f"{site_url}/{lang}/{path}",
        langs=json.dumps(langs),
        root=root,
        default=lang,
        path=path,
        frag=f"#{frag}" if frag else "",
        fallback=fallback,
    )


def _write_stubs(config) -> None:
    site_dir = Path(config["site_dir"])
    site_url = (config.get("site_url") or "").rstrip("/")
    for src, dest in REDIRECTS.items():
        if "://" in dest or _language_of(dest) is None:
            continue
        html_path = File(src, "", "", config["use_directory_urls"]).dest_uri
        stub_dir = posixpath.dirname(html_path)
        out = site_dir / html_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_stub_html(stub_dir, dest, site_url), encoding="utf-8")
    # Scope roots (/go/) have no page of their own: send them to get-started.
    for lang in ACTIVE:
        index = site_dir / lang / "index.html"
        if index.exists() or "get-started/index.md" not in SUPPORTED:
            continue
        if lang not in SUPPORTED["get-started/index.md"]:
            continue
        index.write_text(
            _STUB_ROOT.format(canonical=f"{site_url}/{lang}/get-started/"),
            encoding="utf-8",
        )


_STUB_ROOT = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Redirecting...</title>
    <link rel="canonical" href="{canonical}">
    <meta name="robots" content="noindex">
    <script>location.replace("get-started/" + location.search + location.hash)</script>
    <meta http-equiv="refresh" content="0; url=get-started/">
</head>
<body>
You're being redirected to <a href="get-started/">Get started</a>.
</body>
</html>
"""


def _section_entries(patterns: list, uris: list[str]) -> list[tuple[str, str]]:
    """Expands an llmstxt section's entries over ``uris`` -> (uri, description)."""
    out: list[tuple[str, str]] = []
    for entry in patterns:
        if isinstance(entry, dict):
            pattern, desc = next(iter(entry.items()))
        else:
            pattern, desc = entry, ""
        matches = fnmatch.filter(uris, pattern) if "*" in pattern else [pattern]
        out.extend((uri, desc) for uri in matches if (uri, desc) not in out)
    return out


def _write_llms(config) -> None:
    """Writes /<lang>/llms(-full).txt, the root indexes, and flat .md copies.

    The llmstxt plugin converts every page to Markdown; this replaces its
    single index with one per language, plus a root index that keeps each
    flat URL's page (in its redirect target language) and links the
    per-language indexes.
    """
    llms = config["plugins"].get("llmstxt")
    if llms is None or not LLMS_SECTIONS:
        return
    site_dir = Path(config["site_dir"])
    base = (llms.config.get("base_url") or config["site_url"] or "").rstrip("/")
    full_name = llms.config.get("full_output")
    header = f"# {config['site_name']}\n\n"
    if config.get("site_description"):
        header += f"> {config['site_description']}\n\n"
    if llms.config.get("markdown_description"):
        header += f"{llms.config['markdown_description']}\n\n"

    sources = sorted(
        [*SUPPORTED, *(u for u in PAGE_TITLES if u not in GEN_TO_SRC)],
        key=_sort_key,
    )

    def md_rel(uri: str) -> str:
        return linksmod.md_to_dir_url(uri) + "index.md"

    def page(scoped_uri: str):
        md = site_dir / md_rel(scoped_uri)
        if scoped_uri not in PAGE_TITLES or not md.is_file():
            return None
        return PAGE_TITLES[scoped_uri], f"{base}/{md_rel(scoped_uri)}", md

    def write(dest: Path, title: str, chooser, preface: str = "") -> None:
        index = header.replace(f"# {config['site_name']}", title, 1) + preface
        full = index
        for name, patterns in LLMS_SECTIONS.items():
            index += f"## {name}\n\n"
            parts = []
            for uri, desc in _section_entries(patterns, sources):
                found = chooser(uri)
                if found is None:
                    continue
                page_title, url, md = found
                index += f"- [{page_title}]({url}){': ' + desc if desc else ''}\n"
                parts.append(md.read_text(encoding="utf-8"))
            index += "\n"
            full += f"# {name}\n\n" + "\n".join(parts)
        dest.parent.mkdir(parents=True, exist_ok=True)
        (dest / "llms.txt").write_text(index, encoding="utf-8")
        if full_name:
            (dest / full_name).write_text(full, encoding="utf-8")

    def scoped(lang: str):
        def choose(uri: str):
            if uri not in SUPPORTED:
                return page(uri)  # Unscoped (API reference): in every index.
            return page(f"{lang}/{uri}") if lang in SUPPORTED[uri] else None
        return choose

    def flat(uri: str):
        if uri not in SUPPORTED:
            return page(uri)
        lang = redirectsmod.target_language(uri, SUPPORTED)
        return page(f"{lang}/{uri}") if lang else None

    for lang in ACTIVE:
        write(site_dir / lang, f"# {config['site_name']} for "
              f"{lsconfig.LABELS[lang]}", scoped(lang))
    preface = "## SDK languages\n\n" + "".join(
        f"- [{lsconfig.LABELS[k]}]({base}/{k}/llms.txt): the documentation "
        f"for ADK {lsconfig.LABELS[k]}"
        + (f" ([full text]({base}/{k}/{full_name}))" if full_name else "")
        + "\n"
        for k in ACTIVE
    ) + "\n"
    write(site_dir, f"# {config['site_name']}", flat, preface)

    # The flat URLs used to serve Markdown too; keep them working.
    for uri in SUPPORTED:
        lang = redirectsmod.target_language(uri, SUPPORTED)
        if lang is None:
            continue
        src = site_dir / md_rel(f"{lang}/{uri}")
        dst = site_dir / md_rel(uri)
        if src.is_file() and dst.parent.is_dir():
            shutil.copyfile(src, dst)


# After ``redirects`` (its stubs are replaced) and ``llmstxt`` (its output is
# regrouped); before ``pagefind`` gets nothing from either, so order with it
# does not matter.
@event_priority(-100)
def on_post_build(config):
    _write_stubs(config)
    _write_llms(config)
