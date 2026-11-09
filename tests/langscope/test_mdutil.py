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

from langscope import mdutil


def test_fences_at_any_indent_are_code():
    lines = [
        "text",
        "    ```powershell",
        "    [x]: y",
        "    ```",
        "after",
    ]
    assert mdutil.code_mask(lines) == [False, True, True, True, False]


def test_fence_closes_only_on_same_char_and_length():
    lines = ["````", "```", "~~~", "````", "x"]
    assert mdutil.code_mask(lines) == [True, True, True, True, False]


def test_backtick_fence_info_with_backtick_is_not_a_fence():
    assert mdutil.code_mask(["``` a`b", "x"]) == [False, False]


def test_heading_parses_indent_level_and_strips_attr_list():
    assert mdutil.heading("## Title {#t}") == (0, 2, "Title")
    assert mdutil.heading("    ### Sub") == (4, 3, "Sub")
    assert mdutil.heading("#hashtag") is None


def test_heading_id_uses_explicit_id_or_slug():
    assert mdutil.heading_id("## Gemini Interactions API {#interactions-api}") == (
        "interactions-api")
    assert mdutil.heading_id("### Delivery and deduplication") == (
        "delivery-and-deduplication")
    assert mdutil.heading_id("## Use `VertexAiSessionService`") == (
        "use-vertexaisessionservice")
    assert mdutil.heading_id("## See [docs](x.md)") == "see-docs"


def test_split_frontmatter_and_parse():
    md = "---\nlanguages: [go]\n---\n# T\n"
    fm, body = mdutil.split_frontmatter(md)
    assert fm == "---\nlanguages: [go]\n---\n" and body == "# T\n"
    assert mdutil.frontmatter(md) == {"languages": ["go"]}
    assert mdutil.split_frontmatter("# T\n") == ("", "# T\n")
