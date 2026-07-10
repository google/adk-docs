"""MkDocs post-build hook: flatten per-page Markdown from ``page/index.md`` to
``page.md``.

Registered via the top-level ``hooks:`` list in ``mkdocs.yml``. Runs after the
``mkdocs-llmstxt`` plugin (see the ``event_priority`` on ``on_post_build``).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path, PurePosixPath

import mkdocs.plugins


def flat_md_target(rel_path: str) -> str | None:
    """Map a generated Markdown file's site-relative path to its flat target.

    Args:
        rel_path: Path of the generated file relative to ``site_dir``, POSIX form.

    Returns:
        The new site-relative path (e.g. ``agents/config.md``), or ``None`` if
        the file must stay in place (root ``index.md`` or a non-``index.md`` file).
    """
    p = PurePosixPath(rel_path)
    if p.name != "index.md":
        return None
    parent = p.parent
    if parent in (PurePosixPath("."), PurePosixPath("")):
        return None  # root site/index.md stays as-is
    return f"{parent.as_posix()}.md"


def rewrite_index_links(text: str, site_url: str) -> str:
    """Rewrite ``{site_url}/<path>/index.md`` links to ``{site_url}/<path>.md``.

    The bare homepage link ``{site_url}/index.md`` has no intermediate path
    segment and is left unchanged. Scoping to ``site_url`` avoids corrupting
    unrelated URLs that merely contain the substring ``index.md``.
    """
    base = site_url.rstrip("/")
    pattern = re.compile(re.escape(base) + r"/([^\s)]+?)/index\.md")
    return pattern.sub(lambda m: f"{base}/{m.group(1)}.md", text)


log = logging.getLogger("mkdocs.hooks.flatten_md")


@mkdocs.plugins.event_priority(-100)
def on_post_build(config, **kwargs) -> None:  # noqa: ARG001
    """Rename generated ``index.md`` files to flat ``page.md`` and fix links.

    Priority ``-100`` ensures this runs after the ``mkdocs-llmstxt`` plugin's
    own ``on_post_build`` (lower priority runs later).
    """
    site_dir = Path(config["site_dir"])
    site_url = config["site_url"]

    # Pass 1: rename <dir>/index.md -> <dir>.md (root index.md is left alone).
    renamed = 0
    for md_path in list(site_dir.rglob("index.md")):
        rel = md_path.relative_to(site_dir).as_posix()
        target_rel = flat_md_target(rel)
        if target_rel is None:
            continue
        md_path.replace(site_dir / target_rel)
        renamed += 1

    # Pass 2: rewrite site-internal .../index.md links in all text outputs.
    # Load-bearing assumption: internal .md links are absolute {site_url}/... URLs
    # because mkdocs-llmstxt normalizes them via its _convert_to_absolute_link, so
    # rewrite_index_links only handles absolute links; relative .../index.md links
    # are not expected here.
    rewritten = 0
    targets = list(site_dir.rglob("*.md"))
    for extra in ("llms.txt", "llms-full.txt"):
        extra_path = site_dir / extra
        if extra_path.exists():
            targets.append(extra_path)
    for path in targets:
        text = path.read_text(encoding="utf8")
        new_text = rewrite_index_links(text, site_url)
        if new_text != text:
            path.write_text(new_text, encoding="utf8")
            rewritten += 1

    log.info(
        "flatten_md: renamed %d markdown file(s), rewrote links in %d file(s)",
        renamed,
        rewritten,
    )
