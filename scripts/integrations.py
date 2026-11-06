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

import html
import sys
from pathlib import Path

import yaml
from mkdocs.plugins import log

# The macros plugin imports this module by path; make the repo root (and so
# the langscope package) importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langscope import support as langscope_support


def _langscope(env):
    """The language-scoping settings the hook publishes, or None if off."""
    return (env.conf.get('extra') or {}).get('langscope')


def _page_language(env):
    """The SDK scope of the page being rendered (python/...), or None."""
    scope = _langscope(env)
    page = getattr(env, 'page', None)
    if not scope or page is None:
        return None
    seg = page.file.src_uri.split('/', 1)[0]
    return seg if seg in scope['lang_keys'] else None

def define_env(env):
    """
    This is the hook for defining variables, macros and filters.

    - variables: the dictionary that contains the environment variables
    - macro: a decorator function, to declare a macro.
    """

    @env.macro
    def sdk_picker():
        """Renders one get-started button per SDK, for the homepage."""
        scope = _langscope(env)
        if not scope:
            return '<a href="get-started/" class="btn btn-primary">Start building</a>'
        parts = ['<div class="adk-sdk-grid">']
        for lang in scope['languages']:
            key = html.escape(lang['key'])
            label = html.escape(lang['label'])
            parts.append(
                f'<a class="adk-sdk-card" href="{key}/get-started/" data-adk-lang="{key}">'
                f'<img src="assets/icon-{key}.svg" alt="" width="32" height="32">'
                f'<span>{label}</span></a>'
            )
        parts.append('</div>')
        return ''.join(parts)

    @env.macro
    def render_catalog(path_filter):
        """
        Renders a grid of tool cards based on markdown files matching the path_filter.

        Args:
            path_filter: A glob pattern relative to the docs directory, e.g., "tools/google-cloud/*.md"
        """
        # docs_dir is usually where mkdocs.yml is, or explicitly set.
        # env.conf['docs_dir'] is the absolute path to docs.
        docs_dir = Path(env.conf['docs_dir'])
        files = sorted(docs_dir.glob(path_filter))
        # In a language view, list only integrations that support the
        # language, and link their pages in it.
        lang = _page_language(env)

        # Collect all tags and cards data first
        all_tags = set()
        cards_data = []

        for file_path in files:
            # Skip index.md files as they are usually container pages, not items
            if file_path.name == 'index.md':
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
                if lang and lang not in langscope_support.supported_languages(content):
                    continue
                # Simple frontmatter extraction
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                    else:
                        frontmatter = {}
                else:
                    frontmatter = {}

                # Get metadata
                title = frontmatter.get('catalog_title', frontmatter.get('title'))
                # If title not in frontmatter, try to find first H1
                if not title:
                    for line in content.splitlines():
                        if line.startswith('# '):
                            title = line[2:].strip()
                            break
                # Fallback to filename
                if not title:
                    title = file_path.stem.replace('-', ' ').title()

                description = frontmatter.get('catalog_description',
                    frontmatter.get('description', ''))
                icon = frontmatter.get('catalog_icon',
                    frontmatter.get('tool_icon',
                    frontmatter.get('icon', '/integrations/assets/toolbox.svg'))) # Default icon

                tags = frontmatter.get('catalog_tags', [])
                if isinstance(tags, str):
                    tags = [tags]

                # Normalize tags to lowercase for consistent filtering
                tags = [t.lower() for t in tags]
                all_tags.update(tags)

                # Calculate root-relative link from file path
                rel_path = file_path.relative_to(docs_dir).with_suffix('')
                link = f"/{lang}/{rel_path}/" if lang else f"/{rel_path}/"

                # Ensure icon path is root-relative
                if not icon.startswith('/') and not icon.startswith('http'):
                     icon = f"/{icon}"

                cards_data.append({
                    'title': title,
                    'description': description,
                    'icon': icon,
                    'link': link,
                    'tags': tags
                })

            except Exception as e:
                log.warning(f"Error processing {file_path}: {e}")

        # Sort tags alphabetically
        sorted_tags = sorted(list(all_tags))

        # ID for this specific catalog instance to avoid conflicts if multiple are on page
        catalog_id = "catalog-integrations"

        # Generate HTML
        html_parts = []

        # Styles in docs/stylesheets/custom.css

        # Filter Buttons
        html_parts.append(f'<div class="catalog-filter-bar" id="{catalog_id}-filters">')
        html_parts.append('<span class="catalog-filter-label">Filter:</span>')
        html_parts.append('<button class="catalog-filter-btn active" data-filter="all">All</button>')
        for tag in sorted_tags:
            safe_tag = html.escape(tag)
            # handle MCP button all caps display exception:
            display_name = "MCP" if tag.lower() == "mcp" else safe_tag.title()
            html_parts.append(f'<button class="catalog-filter-btn" data-filter="{safe_tag}">{display_name}</button>')
        html_parts.append('</div>')

        # Grid
        html_parts.append('<div class="tool-card-grid">')
        for card in cards_data:
            tags_str = ",".join(card['tags'])

            # Escape content to prevent XSS
            safe_tags = html.escape(tags_str)
            safe_link = html.escape(card['link'])
            safe_icon = html.escape(card['icon'])
            safe_title = html.escape(card['title'])
            safe_desc = html.escape(card['description'])

            card_html = f"""
<a href="{safe_link}" class="tool-card" data-tags="{safe_tags}">
    <div class="tool-card-image-wrapper">
        <img src="{safe_icon}" alt="{safe_title}">
    </div>
    <div class="tool-card-content">
        <h3>{safe_title}</h3>
        <p>{safe_desc}</p>
    </div>
</a>
"""
            html_parts.append(card_html)
        html_parts.append('</div>')

        # JavaScript
        html_parts.append(f"""
<script>
    (function() {{
        function initCatalog() {{
            const filterContainer = document.getElementById('{catalog_id}-filters');
            if (!filterContainer) return;

            const buttons = filterContainer.querySelectorAll('.catalog-filter-btn');
            const cards = document.querySelectorAll('.tool-card');

            function filterCards(filterValue) {{
                // Update buttons
                buttons.forEach(btn => {{
                    if (btn.getAttribute('data-filter') === filterValue) {{
                        btn.classList.add('active');
                    }} else {{
                        btn.classList.remove('active');
                    }}
                }});

                // Filter cards
                cards.forEach(card => {{
                    const cardTags = (card.getAttribute('data-tags') || '').split(',');
                    if (filterValue === 'all' || cardTags.includes(filterValue)) {{
                        card.style.display = 'flex'; // Restore flex display
                    }} else {{
                        card.style.display = 'none';
                    }}
                }});
            }}

            // Click handlers
            buttons.forEach(btn => {{
                btn.addEventListener('click', () => {{
                    const filter = btn.getAttribute('data-filter');
                    filterCards(filter);

                    // Optional: Update URL without reload
                    const url = new URL(window.location);
                    if (filter === 'all') {{
                        url.searchParams.delete('topic');
                    }} else {{
                        url.searchParams.set('topic', filter);
                    }}
                    window.history.pushState({{}}, '', url);
                }});
            }});

            // Check URL param on load
            const urlParams = new URLSearchParams(window.location.search);
            const topic = urlParams.get('topic');
            if (topic) {{
                // Validate topic exists in buttons to avoid empty states if possible
                // or just try to filter
                const matchingBtn = Array.from(buttons).find(btn => btn.getAttribute('data-filter') === topic);
                if (matchingBtn) {{
                    filterCards(topic.toLowerCase());
                }}
            }}
        }}

        // Run immediately if DOM is ready, otherwise wait for DOMContentLoaded
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initCatalog);
        }} else {{
            initCatalog();
        }}
    }})();
</script>
        """)

        return "\n".join(html_parts)
