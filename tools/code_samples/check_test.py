# Copyright 2025 Google LLC
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

"""Tests for the code sample checker.

Two halves, and the second matters as much as the first. A checker that
reports nothing because it is broken looks exactly like a checker that reports
nothing because the samples are fine, so every defect class it claims to catch
is planted here and asserted on.

Run with: python -m pytest tools/code_samples/check_test.py
"""

from __future__ import annotations

import pathlib
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import check  # noqa: E402
import fences  # noqa: E402


def page(tmp_path: pathlib.Path, markdown: str) -> pathlib.Path:
    path = tmp_path / "page.md"
    path.write_text(textwrap.dedent(markdown), encoding="utf-8")
    return path


def defects(tmp_path: pathlib.Path, markdown: str) -> list[check.Defect]:
    return check.check_file(page(tmp_path, markdown), tmp_path)


# ---------------------------------------------------------------- caught ---


def test_catches_unparseable_sample(tmp_path):
    found = defects(tmp_path, """
        ```python
        def broken(
        ```
        """)
    assert len(found) == 1
    assert found[0].kind == "does not parse"


def test_catches_unindented_class_body(tmp_path):
    found = defects(tmp_path, """
        ```python
        class Thing:
        def method(self):
            return 1
        ```
        """)
    assert [d.kind for d in found] == ["does not parse"]


def test_catches_await_in_sync_function(tmp_path):
    found = defects(tmp_path, """
        ```python
        def tool():
            result = await something()
            return result
        ```
        """)
    assert [d.kind for d in found] == ["does not parse"]


def test_catches_module_that_does_not_exist(tmp_path):
    found = defects(tmp_path, """
        ```python
        from google.adk.no_such_module import Thing
        ```
        """)
    assert [d.kind for d in found] == ["unresolved import"]


def test_catches_name_that_does_not_exist(tmp_path):
    found = defects(tmp_path, """
        ```python
        from google.adk.agents import NoSuchAgentClass
        ```
        """)
    assert [d.kind for d in found] == ["unresolved import"]


def test_reports_the_line_of_the_opening_fence(tmp_path):
    found = defects(tmp_path, """
        Some prose.

        ```python
        from google.adk.agents import NoSuchAgentClass
        ```
        """)
    assert found[0].line == 4


def test_catches_a_sample_nested_in_a_tab(tmp_path):
    found = defects(tmp_path, """
        === "Python"

            ```python
            from google.adk.agents import NoSuchAgentClass
            ```
        """)
    assert [d.kind for d in found] == ["unresolved import"]


# ---------------------------------------------------------------- passed ---


def test_accepts_a_whole_module(tmp_path):
    assert not defects(tmp_path, """
        ```python
        from google.adk.agents import LlmAgent

        agent = LlmAgent(name="demo", model="gemini-flash-latest")
        ```
        """)


def test_accepts_a_method_body_fragment(tmp_path):
    assert not defects(tmp_path, """
        ```python
        self.counter += 1
        print(self.counter)
        ```
        """)


def test_accepts_pseudocode_with_elision(tmp_path):
    assert not defects(tmp_path, """
        ```python
        agent = LlmAgent(
            name="demo",
            ...
        )
        ```
        """)


def test_accepts_a_signature_listing(tmp_path):
    assert not defects(tmp_path, """
        ```python
        async def before_model_callback(
            self, *, callback_context, llm_request
        ) -> None:
        ```
        """)


def test_accepts_an_await_excerpt_from_a_loop(tmp_path):
    assert not defects(tmp_path, """
        ```python
        async for event in runner.run_async(...):
            if event.is_final_response():
                break
            await handle(event)
        ```
        """)


def test_ignores_non_python_blocks(tmp_path):
    assert not defects(tmp_path, """
        ```go
        this is not python at all (((
        ```

        ```bash
        pip install google-adk
        ```
        """)


def test_ignores_a_block_that_only_includes_a_snippet(tmp_path):
    assert not defects(tmp_path, """
        ```python
        --8<-- "examples/python/does/not/matter.py"
        ```
        """)


# ------------------------------------------------------------ fence parse ---


def test_fence_survives_backticks_inside_a_string(tmp_path):
    found = fences.parse(page(tmp_path, '''
        ```python
        PROMPT = """
              ```tool_code
              nested and indented
              ```
        """
        ```
        '''))
    assert len(found) == 1
    assert "nested and indented" in found[0].text


def test_fence_skips_a_block_that_never_closes_cleanly(tmp_path):
    """A fence closed at the wrong indentation swallows what follows.

    Opening at six columns and "closing" at eight means the block never
    terminates, so the next opener gets absorbed into its body. Rather than
    guess a boundary, the parser reports nothing for the whole ambiguous run.
    Reporting nothing is right: any guess would produce defects against code
    the author never wrote.
    """
    path = tmp_path / "page.md"
    path.write_text(
        "      ```python\n      x = 1\n        ```\n\n      ```python\n      y = 2\n      ```\n",
        encoding="utf-8",
    )
    assert fences.parse(path) == []


def test_dedent_measures_columns_not_characters(tmp_path):
    path = tmp_path / "page.md"
    # Fence at four columns; body line indented with a tab, which is four
    # columns, then real code indentation on top.
    path.write_text("    ```python\n\tif True:\n\t    pass\n    ```\n", encoding="utf-8")
    body = fences.parse(path)[0].text
    assert body.split("\n")[0] == "if True:"
    assert body.split("\n")[1] == "    pass"
