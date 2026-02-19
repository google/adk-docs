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

import yaml
import html
from pathlib import Path
from mkdocs.plugins import log

def define_env(env):
    """
    This is the hook for defining variables, macros and filters.

    - variables: the dictionary that contains the environment variables
    - macro: a decorator function, to declare a macro.
    """

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

        # Collect all tags and cards data first
        all_tags = set()
        cards_data = []

        for file_path in files:
            # Skip index.md files as they are usually container pages, not items
            if file_path.name == 'index.md':
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
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
                    frontmatter.get('icon', '/adk-docs/integrations/assets/toolbox.svg'))) # Default icon
                
                tags = frontmatter.get('catalog_tags', [])
                if isinstance(tags, str):
                    tags = [tags]
                
                # Normalize tags to lowercase for consistent filtering
                tags = [t.lower() for t in tags]
                all_tags.update(tags)

                # Calculate relative link
                # mkdocs uses site_url structure. We want /adk-docs/...
                # file_path is absolute. we want relative to docs_dir
                rel_path = file_path.relative_to(docs_dir).with_suffix('')
                # We need to handle index.html vs pretty urls.
                # Assuming standard mkdocs behavior: tools/foo.md -> tools/foo/
                link = f"/adk-docs/{rel_path}/"

                # Ensure icon path is correct (if relative, make it absolute-ish for the site)
                # If icon starts with assets/, prepend /adk-docs/
                if not icon.startswith('/') and not icon.startswith('http'):
                     icon = f"/adk-docs/{icon}"
                
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
        html_parts.append(f'<span class="catalog-filter-label">Filter:</span>')
        html_parts.append(f'<button class="catalog-filter-btn active" data-filter="all">All</button>')
        for tag in sorted_tags:
            safe_tag = html.escape(tag)
            # handle MCP button all caps display exception:
            display_name = "MCP" if tag.lower() == "mcp" else safe_tag.title()
            html_parts.append(f'<button class="catalog-filter-btn" data-filter="{safe_tag}">{display_name}</button>')
        html_parts.append('</div>')

        # Grid
        html_parts.append('<div class="tool-card-grid">')
        for card in cards_data:
            tags_str = " ".join(card['tags'])
            
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
                    const cardTags = (card.getAttribute('data-tags') || '').split(' ');
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
