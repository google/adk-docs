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

import pathlib

from langscope.flatten import flatten, flatten_with_report

DOCS = pathlib.Path(__file__).resolve().parents[2] / "docs"

TABS = (
    "Intro paragraph.\n"
    "\n"
    '=== "Python"\n'
    "\n"
    "    ```python\n"
    "    print(1)\n"
    "    ```\n"
    "\n"
    '=== "Java"\n'
    "\n"
    "    ```java\n"
    "    System.out.println(1);\n"
    "    ```\n"
    "\n"
    "After paragraph.\n"
)


def test_keeps_only_target_language_dedented():
    out = flatten(TABS, "python")
    assert '=== "Python"' not in out
    assert '=== "Java"' not in out
    assert "```python\nprint(1)\n```" in out
    assert "System.out.println" not in out
    assert "Intro paragraph." in out and "After paragraph." in out


def test_missing_target_drops_group():
    out = flatten(TABS, "go")  # no Go tab
    assert "print(1)" not in out
    assert "System.out.println" not in out
    assert "Intro paragraph." in out and "After paragraph." in out


def test_non_language_group_is_untouched():
    md = (
        '=== "pip"\n\n    pip install x\n\n'
        '=== "poetry"\n\n    poetry add x\n'
    )
    out = flatten(md, "python")
    assert '=== "pip"' in out and '=== "poetry"' in out


def test_snippet_line_preserved():
    md = (
        '=== "Go"\n\n'
        "    ```go\n"
        '    --8<-- "examples/go/snippets/context/main.go:x"\n'
        "    ```\n"
    )
    out = flatten(md, "go")
    assert '--8<-- "examples/go/snippets/context/main.go:x"' in out
    assert out.startswith("```go")


def test_tab_nested_in_list_dedents_to_list_level():
    md = (
        "1. Step one:\n"
        "\n"
        '    === "Python"\n'
        "\n"
        "        ```python\n"
        "        x = 1\n"
        "        ```\n"
        "\n"
        '    === "Java"\n'
        "\n"
        "        ```java\n"
        "        int x = 1;\n"
        "        ```\n"
    )
    out = flatten(md, "python")
    assert "1. Step one:" in out
    assert "    ```python" in out  # still indented under the list item
    assert "int x = 1;" not in out


def test_flattening_context_index_drops_other_languages():
    src = (DOCS / "context" / "index.md").read_text(encoding="utf-8")
    py = flatten(src, "python")
    assert '=== "Python"' not in py
    assert "System.out.println" not in py  # Java sample gone
    assert "InvocationContext" in py       # shared prose kept


def test_blank_line_separates_kept_block_from_following_paragraph():
    # Fix 1: a flattened tab block must keep a blank line before the next
    # paragraph (the recursive splice used to strip trailing blanks).
    out = flatten(TABS, "python")
    assert "```\n\nAfter paragraph." in out


def test_tab_marker_inside_code_fence_is_not_parsed():
    # Fix 2: a literal `=== "Go"` inside a fenced code block is example text,
    # not a tab marker; it must survive verbatim.
    md = (
        '=== "Python"\n'
        "\n"
        "    ```\n"
        '    === "Go"\n'
        "    ```\n"
    )
    out = flatten(md, "python")
    assert '=== "Go"' in out          # literal example text survives
    assert '=== "Python"' not in out  # outer language tab still flattened


def test_non_language_group_preserves_tab_indentation():
    # Fix 3: a tab-indented non-language group is reconstructed with its
    # original indentation intact (not rebuilt from a space count).
    md = (
        '\t=== "pip"\n'
        "\n"
        "\t    pip install x\n"
        "\n"
        '\t=== "poetry"\n'
        "\n"
        "\t    poetry add x\n"
    )
    out = flatten(md, "python")
    assert '\t=== "pip"' in out
    assert '\t=== "poetry"' in out


def test_recurses_into_non_language_groups():
    md = (
        '=== "UI Testing"\n\n    Open the UI.\n\n'
        '=== "API Testing (curl)"\n\n'
        '    === "Python"\n\n        py curl\n\n'
        '    === "Go"\n\n        go curl\n'
    )
    out = flatten(md, "python")
    assert '=== "API Testing (curl)"' in out and "py curl" in out
    assert "go curl" not in out and '=== "Python"' not in out


def test_labels_with_a_language_prefix_are_language_tabs():
    md = (
        '=== "Python - adk CLI"\n\n    adk deploy\n\n'
        '=== "Python - gcloud CLI"\n\n    gcloud py\n\n'
        '=== "Go - adkgo CLI"\n\n    adkgo deploy\n\n'
        '=== "Java - gcloud CLI"\n\n    gcloud java\n'
    )
    py = flatten(md, "python")
    # Two Python tabs stay tabs, named by what follows the language.
    assert '=== "adk CLI"' in py and '=== "gcloud CLI"' in py
    assert "adkgo" not in py and "gcloud java" not in py
    go = flatten(md, "go")
    assert "adkgo deploy" in go and "=== " not in go  # One survivor: spliced.


def test_javascript_typescript_label_belongs_to_typescript():
    md = (
        '=== "Python"\n\n    pip install x\n\n'
        '=== "JavaScript / TypeScript"\n\n    npm install x\n'
    )
    assert "npm install x" in flatten(md, "typescript")
    assert "pip install x" not in flatten(md, "typescript")


def test_neutral_tabs_in_a_language_group_are_kept():
    md = (
        '=== "Python"\n\n    py\n\n'
        '=== "Go"\n\n    go\n\n'
        '=== "Notes"\n\n    shared notes\n'
    )
    out = flatten(md, "java")  # No Java tab: the neutral tab survives.
    assert "shared notes" in out and "    py" not in out


def test_dropped_groups_are_reported():
    md = 'Intro.\n\n=== "Python"\n\n    py\n\n=== "Go"\n\n    go\n'
    out, drops, _ = flatten_with_report(md, "kotlin")
    assert len(drops) == 1
    assert drops[0].line == 3 and drops[0].labels == ("Python", "Go")
    assert drops[0].lead_in == "Intro." and not drops[0].placeholder
    assert "Not yet available" not in out


def test_dangling_lead_in_gets_a_placeholder_note():
    md = 'You should see:\n\n=== "Python"\n\n    out\n\n=== "Go"\n\n    out\n'
    out, drops, _ = flatten_with_report(md, "kotlin")
    assert drops[0].placeholder
    assert '!!! note "Not yet available for Kotlin"' in out
    assert "available for Python and Go" in out


def test_anchors_of_discarded_tabs_are_reported():
    md = (
        '=== "Python"\n\n    ### Delivery and deduplication\n\n    text\n\n'
        '=== "Java"\n\n    ### Setup {#java-setup}\n'
    )
    _, _, anchors = flatten_with_report(md, "kotlin")
    assert anchors == {
        "delivery-and-deduplication": frozenset({"python"}),
        "java-setup": frozenset({"java"}),
    }


def test_tab_markers_inside_indented_fences_are_text():
    md = (
        "!!! example\n\n    ```markdown\n"
        '    === "Python"\n\n        x\n    ```\n'
    )
    assert '=== "Python"' in flatten(md, "go")


def test_line_indented_less_than_tab_content_ends_the_group():
    # pymdownx.tabbed only treats lines indented four columns past the marker
    # as tab content; a 2-space bullet after the last tab is shared content.
    md = (
        '=== "Python"\n'
        "\n"
        "    ```python\n"
        "    p\n"
        "    ```\n"
        "\n"
        '=== "Kotlin"\n'
        "\n"
        "    ```kotlin\n"
        "    k\n"
        "    ```\n"
        "\n"
        "  * **Loop:** shared\n"
        "      * **Termination:** also shared\n"
    )
    for lang in ("python", "kotlin", "go"):
        out = flatten(md, lang)
        assert "  * **Loop:** shared" in out, lang
        assert "      * **Termination:** also shared" in out, lang
    assert "k\n" not in flatten(md, "python")
    assert "p\n" not in flatten(md, "kotlin")


def test_less_indented_line_without_blank_line_ends_the_group():
    md = '=== "Python"\n    py text\n   three spaces\n=== "Java"\n    java\n'
    out = flatten(md, "java")
    assert "three spaces" in out
    assert "py text" not in out
    assert "java" in out


def test_nested_group_ends_below_its_own_content_indent():
    md = (
        "1. Step:\n"
        "\n"
        '    === "Python"\n'
        "\n"
        "        py\n"
        "\n"
        '    === "Go"\n'
        "\n"
        "        go\n"
        "\n"
        "      Shared continuation.\n"
    )
    out = flatten(md, "python")
    assert "      Shared continuation." in out
    assert "go" not in out.replace("Shared", "")


def test_tab_characters_count_as_four_columns():
    md = (
        '=== "Go"\n'
        "\n"
        "    ```go\n"
        "    import (\n"
        '      "fmt"\n'
        "\t)\n"
        "    ```\n"
        "\n"
        '=== "Java"\n'
        "\n"
        "    java\n"
        "\n"
        "After.\n"
    )
    out = flatten(md, "go")
    assert out == '```go\nimport (\n  "fmt"\n)\n```\n\nAfter.\n'
    assert "java" not in out


def test_custom_agents_loop_agent_bullet_is_shared():
    src = (DOCS / "agents" / "custom-agents.md").read_text(encoding="utf-8")
    for lang in ("python", "typescript", "go", "java", "kotlin"):
        assert "The loop stops if" in flatten(src, lang), lang


def test_selected_and_new_group_tab_markers():
    md = (
        '=== "Python"\n\n    py\n\n'
        '===+ "Java"\n\n    java\n\n'
        '===! "Python"\n\n    py2\n\n'
        '=== "Go"\n\n    go2\n'
    )
    # `===!` starts a second group, so each group is flattened on its own.
    assert flatten(md, "java") == "java\n"
    assert flatten(md, "go") == "go2\n"
    assert flatten(md, "python") == "py\n\npy2\n"
    neutral = '===+ "Maven"\n\n    m\n\n=== "Gradle"\n\n    g\n'
    assert flatten(neutral, "go") == neutral
