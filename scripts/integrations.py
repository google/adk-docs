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

        cards_html = '<div class="tool-card-grid">\n'

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

                card = f"""
  <a href="{link}" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="{icon}" alt="{title}">
    </div>
    <div class="tool-card-content">
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  </a>
"""
                cards_html += card
            except Exception as e:
                log.warning(f"Error processing {file_path}: {e}")

        cards_html += '</div>'
        return cards_html
