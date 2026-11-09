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

from langscope import config, support

BANNER = (
    '<div class="language-support-tag">\n'
    '  <span class="lst-supported">Supported in ADK</span>'
    '<span class="lst-python">Python v0.1.0</span>'
    '<span class="lst-java">Java v0.1.0</span>\n'
    '</div>\n'
)


def test_banner_lists_only_declared_languages():
    md = f"# Title\n\n{BANNER}\nBody\n"
    assert support.supported_languages(md) == frozenset({"python", "java"})


def test_no_banner_means_all_languages():
    assert support.supported_languages("# Title\n\nBody\n") == config.ALL_KEYS


def test_preview_and_supported_spans_are_not_languages():
    md = (
        '<div class="language-support-tag">'
        '<span class="lst-supported">x</span>'
        '<span class="lst-preview">y</span>'
        '<span class="lst-go">Go</span></div>\n'
    )
    assert support.supported_languages(md) == frozenset({"go"})


def test_banner_without_language_spans_scopes_to_none():
    md = (
        '<div class="language-support-tag">'
        '<span class="lst-supported">x</span>'
        '<span class="lst-preview">y</span></div>\n'
    )
    result = support.supported_languages(md)
    assert result == frozenset()
    assert result != config.ALL_KEYS


def test_banner_with_attributes_is_recognised():
    md = (
        "# Agent Runtime\n\n"
        '<div class="language-support-tag" title="Agent Runtime currently '
        'supports Python and Go.">\n'
        '  <span class="lst-supported">Supported in ADK</span>'
        '<span class="lst-python">Python</span><span class="lst-go">Go</span>\n'
        "</div>\n\nBody\n"
    )
    assert support.supported_languages(md) == frozenset({"python", "go"})


def test_banner_with_extra_classes_is_recognised():
    md = '<div id="x" class="wide language-support-tag"><span class="lst-go">Go</span></div>\n'
    assert support.supported_languages(md) == frozenset({"go"})


def test_section_banner_does_not_scope_the_page():
    md = (
        f"# Title\n\n{BANNER}\nIntro\n\n## Section\n\nText\n\n"
        "## Kotlin bit\n\n"
        '<div class="language-support-tag"><span class="lst-kotlin">Kotlin</span></div>\n'
    )
    assert support.supported_languages(md) == frozenset({"python", "java"})


def test_indented_banner_is_not_a_page_banner():
    md = "# Title\n\n=== \"Python\"\n\n    " + BANNER.replace("\n", "\n    ")
    assert support.supported_languages(md) == config.ALL_KEYS


def test_banner_before_first_heading_is_a_page_banner():
    # evaluate/custom_metrics.md has no H1: the banner leads the page.
    md = f"{BANNER}\n## Custom metrics\n\nText\n\n## More\n"
    assert support.supported_languages(md) == frozenset({"python", "java"})


def test_banner_in_code_fence_is_ignored():
    md = "# T\n\n```html\n" + BANNER + "```\n"
    assert support.supported_languages(md) == config.ALL_KEYS


def test_frontmatter_languages_override_banners():
    md = f"---\nlanguages: [go]\n---\n\n# Go quickstart\n\n{BANNER}"
    assert support.supported_languages(md) == frozenset({"go"})


def test_frontmatter_languages_accepts_a_string_and_labels():
    md = "---\nlanguages: TypeScript\n---\n\n# T\n"
    assert support.supported_languages(md) == frozenset({"typescript"})


def test_frontmatter_unknown_language_raises():
    md = "---\nlanguages: [cobol]\n---\n\n# T\n"
    try:
        support.supported_languages(md)
    except ValueError as error:
        assert "cobol" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_filter_banner_keeps_one_language_badge_and_status():
    lines = [
        '<div class="language-support-tag" title="Python and Go only">',
        ('<span class="lst-supported">Supported in ADK</span>'
         '<span class="lst-python">Python v1.2</span>'
         '<span class="lst-go">Go v0.3</span>'
         '<span class="lst-preview">Preview</span>'),
        "</div>",
    ]
    out = "\n".join(support.filter_banner(lines, "go"))
    assert "Go v0.3" in out and "Python" not in out
    assert "lst-supported" in out and "lst-preview" in out
    assert "title=" not in out
    assert len(out.split("\n")) == len(lines)  # Line count is preserved.


def test_scope_page_banners_rewrites_only_page_banners():
    md = (
        f"# Title\n\n{BANNER}\n## Later\n\n"
        '<div class="language-support-tag"><span class="lst-python">Python</span>'
        '<span class="lst-java">Java</span></div>\n'
    )
    out = support.scope_page_banners(md, "java")
    head, _, tail = out.partition("## Later")
    assert "Java v0.1.0" in head and "Python v0.1.0" not in head
    assert "lst-python" in tail  # Section banners are scope_sections' job.


def test_scope_page_banners_drops_banner_excluded_by_frontmatter():
    md = f"---\nlanguages: [go]\n---\n\n# Title\n\n{BANNER}\nBody\n"
    out = support.scope_page_banners(md, "go")
    assert "language-support-tag" not in out
    assert out.startswith("---\nlanguages: [go]\n---\n")
