"""MkDocs post-build hook: flatten per-page Markdown from ``page/index.md`` to
``page.md``.

Registered via the top-level ``hooks:`` list in ``mkdocs.yml``. Runs after the
``mkdocs-llmstxt`` plugin (see the ``event_priority`` on ``on_post_build``).
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath


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
