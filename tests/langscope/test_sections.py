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

import pytest

from langscope import sections

BANNER_PY = (
    '<div class="language-support-tag">'
    '<span class="lst-supported">Supported in ADK</span>'
    '<span class="lst-python">Python v1.0</span></div>'
)


def scope(md, lang):
    return sections.scope_sections(md, lang)[0]


def test_section_banner_drops_its_section_elsewhere():
    md = (
        "# Context\n\nShared.\n\n## Render UI Widgets\n\n"
        f"{BANNER_PY}\n\nPython-only widgets.\n\n### Detail\n\nMore.\n\n"
        "## Next\n\nShared again.\n"
    )
    go = scope(md, "go")
    assert "Render UI Widgets" not in go and "Python-only widgets" not in go
    assert "Detail" not in go  # Subsections go with the section.
    assert "Shared." in go and "## Next" in go and "Shared again." in go


def test_section_banner_kept_and_narrowed_in_its_language():
    md = (
        "# T\n\n## Both\n\n"
        '<div class="language-support-tag"><span class="lst-python">Python v1</span>'
        '<span class="lst-go">Go v2</span></div>\n\nText\n'
    )
    py = scope(md, "python")
    assert "Text" in py and "Python v1" in py and "Go v2" not in py


def test_section_banner_inside_a_tab_scopes_the_tab_section():
    md = (
        '=== "Python"\n\n    ## Delivery\n\n    '
        '<div class="language-support-tag"><span class="lst-java">Java</span></div>\n\n'
        "    Java text.\n\n    ## Other\n\n    Kept.\n"
    )
    out = scope(md, "python")
    assert "Java text." not in out and "## Other" in out and "Kept." in out


def test_orphan_section_banner_is_removed_alone():
    md = (
        "Intro.\n\n"
        '    <div class="language-support-tag"><span class="lst-go">Go</span></div>\n\n'
        "Kept.\n"
    )
    out = scope(md, "python")
    assert "language-support-tag" not in out and "Intro." in out and "Kept." in out


def test_heading_naming_a_language_scopes_its_section():
    md = (
        "# Logging\n\n## Python\n\npy text\n\n## Java\n\njava text\n\n"
        "### Log levels (Python)\n\nlevels\n\n## Common\n\nshared\n"
    )
    java = scope(md, "java")
    assert "py text" not in java and "levels" not in java
    assert "java text" in java and "shared" in java
    py = scope(md, "python")
    assert "java text" not in py and "levels" not in py  # Nested in "## Java".


def test_page_title_naming_a_language_is_not_scoped():
    md = "# Build live streaming agent with Python\n\nBody\n"
    assert "Body" in scope(md, "go")


def test_headings_that_only_mention_a_language_are_not_scoped():
    for title in (
        "ADK for Java", "Option 2: Configure in Python",
        "Quick Start: Enabling Observability in Kotlin", "Migrating from Java",
        "Calling Python tools from Go", "Go further", "ADK Python 1.x",
    ):
        md = f"# T\n\n## {title}\n\nbody\n"
        assert "body" in scope(md, "typescript"), title


def test_admonition_titles_that_mention_a_language_are_not_scoped():
    md = (
        '# T\n\nText.\n\n!!! note "Go: API path prefix"\n\n    Go detail.\n\n'
        '??? tip "Kotlin support"\n    Kotlin detail.\n\n'
        '!!! note "Requires ADK Python 2.4 or higher"\n\n    py qualifier\n\n'
        '!!! note "Go flags differ from Python/TypeScript"\n\n    go flags\n\n'
        'After.\n'
    )
    java = scope(md, "java")
    for text in ("Go detail.", "Kotlin detail.", "py qualifier", "go flags"):
        assert text in java


def test_only_title_forms():
    for title, keys in (
        ("Python only", {"python"}), ("Go-only", {"go"}),
        ("Only Python and TypeScript", {"python", "typescript"}),
        ("Java / Kotlin only", {"java", "kotlin"}),
        ("ONLY for Search in ADK Python v1.15.0 and lower", set()),
        ("Not available in Go", set()), ("Applies to only Java ADK", set()),
    ):
        assert sections.only_title_languages(title) == keys, title


def test_only_admonition_with_capitalised_or_missing_type():
    md = '!!! Note "TypeScript only"\n\n    ts\n\n??? "Python only"\n\n    py\n\nend\n'
    out = scope(md, "kotlin")
    assert "    ts" not in out and "    py" not in out and "end" in out


def test_admonition_class_marker_scopes_the_admonition():
    md = (
        '!!! note langscope-go "Path prefix"\n\n    Go detail.\n\n'
        '!!! warning langscope-java langscope-kotlin\n\n    JVM detail.\n\n'
        'end\n'
    )
    py = scope(md, "python")
    assert "Go detail." not in py and "JVM detail." not in py and "end" in py
    assert "JVM detail." in scope(md, "kotlin")


def test_heading_class_marker_scopes_the_section():
    md = (
        "# T\n\n## Test using Python { .langscope-python }\n\npy\n\n"
        "### Sub\n\nmore py\n\n## Shared\n\nshared\n"
    )
    go = scope(md, "go")
    assert "py\n" not in go and "more py" not in go and "shared" in go
    _, removals = sections.scope_sections(md, "go")
    assert removals[0].explicit and removals[0].kind == "heading"


def test_langscope_all_exempts_from_the_heuristics():
    md = (
        '# T\n\n## Java { .langscope-all }\n\nfor everyone\n\n'
        '!!! note langscope-all "Python only"\n\n    also everyone\n'
    )
    go = scope(md, "go")
    assert "for everyone" in go and "also everyone" in go


def test_unknown_class_marker_is_an_error():
    with pytest.raises(ValueError, match="langscope-rust"):
        sections.scope_sections("## A { .langscope-rust }\n\nx\n", "go")


def test_frontmatter_can_turn_the_heuristics_off():
    md = (
        "---\nlanguage_heuristics: false\n---\n# T\n\n## Java\n\nj\n\n"
        '!!! note "Go only"\n\n    g\n\n## Marked { .langscope-java }\n\nm\n'
    )
    py = scope(md, "python")
    assert "\nj\n" in py and "    g" in py
    assert "\nm" not in py  # Explicit markers still apply.


def test_nothing_is_removed_for_languages_the_page_lacks():
    md = (
        "# Kotlin page\n\n## Java\n\nfor Java users\n\n"
        '!!! note "Python only"\n\n    py\n\n## Python { .langscope-python }\n\nm\n'
    )
    kt = frozenset({"kotlin"})
    out, removals = sections.scope_sections(md, "kotlin", kt)
    assert "for Java users" in out and "    py" in out and "\nm" in out
    assert removals and all(r.kept for r in removals)
    assert all(r.anchors == () for r in removals)


def test_banner_not_directly_under_a_heading_drops_only_itself():
    md = (
        f"# T\n\n## Mixed\n\nShared intro.\n\n{BANNER_PY}\n\nmore\n\n"
        "## Next\n\nx\n"
    )
    go = scope(md, "go")
    assert "Shared intro." in go and "more" in go
    assert "language-support-tag" not in go


def test_badge_only_banner_does_not_scope_its_section():
    md = (
        "# T\n\n## Filter\n\n"
        '<div class="language-support-tag langscope-all">'
        '<span class="lst-kotlin">Kotlin v0.7.0</span></div>\n\n'
        "Every SDK filters.\n"
    )
    py = scope(md, "python")
    assert "Every SDK filters." in py and "Kotlin v0.7.0" not in py
    kt = scope(md, "kotlin")
    assert "Kotlin v0.7.0" in kt


def test_language_only_aside_opening_a_section_scopes_the_section():
    md = (
        "# GKE\n\n## Option 1\n\nboth\n\n"
        "## Option 2: `adk deploy gke`\n\n!!! note \"Python only\"\n\n"
        "    Only the Python CLI has it.\n\n### Syntax\n\npython stuff\n\n"
        "## Test\n\nshared\n"
    )
    go = scope(md, "go")
    assert "Option 2" not in go and "python stuff" not in go
    assert "both" in go and "shared" in go
    assert "python stuff" in scope(md, "python")


def test_only_aside_mid_section_scopes_itself():
    md = '## S\n\ntext\n\n!!! note "Python only"\n\n    py\n\nmore\n'
    go = scope(md, "go")
    assert "text" in go and "more" in go and "    py" not in go


def test_code_fences_are_left_alone():
    md = "## Go\n\n```\n## Python\n```\n"
    out = scope(md, "go")
    assert "## Python" in out


def test_removals_report_lines_and_anchors():
    md = "# T\n\n## Kotlin {#kt}\n\nx\n\n### Gradle\n\ny\n"
    _, removals = sections.scope_sections(md, "go")
    assert [r.line for r in removals] == [3]
    assert removals[0].kind == "heading" and not removals[0].explicit
    assert removals[0].anchors == ("kt", "gradle")
    assert removals[0].languages == frozenset({"kotlin"})


def test_mapped_variant_maps_output_lines_to_input_lines():
    md = "---\na: 1\n---\n# T\n\n## Java\n\nj\n\n## Shared\n\ns\n"
    out, _, origin = sections.scope_sections_mapped(md, "go")
    lines = out.split("\n")
    assert len(origin) == len(lines)
    src = md.split("\n")
    for i, line in enumerate(lines):
        assert src[origin[i] - 1] == line


def test_blank_runs_collapse_only_around_removals():
    md = "a\n\n\n\nb\n\n!!! note \"Go only\"\n    g\n\nc\n"
    out = scope(md, "python")
    assert "a\n\n\n\nb" in out  # Untouched spacing elsewhere.
    assert "b\n\nc" in out
