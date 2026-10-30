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

from langscope.links import rewrite_links

SUP = {
    "evaluate/index.md": frozenset({"python"}),          # python-only
    "agents/routing.md": frozenset({"typescript"}),      # no python
    "context/index.md": frozenset({"python", "go"}),
}


def test_same_language_doc_link_is_scoped():
    md = "See [ctx](../context/index.md)."
    out = rewrite_links(md, "safety/index.md", "python", SUP)
    assert "(/python/context/)" in out


def test_missing_language_doc_link_falls_back_to_python():
    # go page links to python-only evaluate -> fall back to python
    md = "See [eval](../evaluate/index.md)."
    out = rewrite_links(md, "safety/index.md", "go", SUP)
    assert "(/python/evaluate/)" in out


def test_missing_and_no_python_falls_back_to_first_supported():
    md = "See [routing](routing.md)."
    out = rewrite_links(md, "agents/index.md", "python", SUP)
    assert "(/typescript/agents/routing/)" in out


def test_asset_link_becomes_root_absolute_unscoped():
    md = "![diagram](assets/x.png)"
    out = rewrite_links(md, "integrations/galileo.md", "python", SUP)
    assert "(/integrations/assets/x.png)" in out


def test_updir_asset_link_resolves_against_source_dir():
    md = "![d](../assets/agent.png)"
    out = rewrite_links(md, "deploy/gke.md", "python", SUP)
    assert "(/assets/agent.png)" in out


def test_root_index_link_becomes_slash():
    md = "[home](../index.md)"
    out = rewrite_links(md, "agents/index.md", "python", SUP)
    assert "(/)" in out


def test_anchor_preserved():
    md = "[x](../context/index.md#types)"
    out = rewrite_links(md, "safety/index.md", "go", SUP)
    assert "(/go/context/#types)" in out  # context supports go


def test_external_and_anchor_only_untouched():
    md = "[a](https://example.com) and [b](#local) and [c](/already/abs)"
    out = rewrite_links(md, "x/y.md", "python", SUP)
    assert "https://example.com" in out and "(#local)" in out and "(/already/abs)" in out


def test_links_inside_code_fence_untouched():
    md = "```\n[x](../context/index.md)\n```\n"
    out = rewrite_links(md, "safety/index.md", "python", SUP)
    assert "[x](../context/index.md)" in out


def test_html_img_src_rewritten():
    md = '<img src="assets/x.png" alt="a">'
    out = rewrite_links(md, "integrations/galileo.md", "python", SUP)
    assert 'src="/integrations/assets/x.png"' in out


def test_root_absolute_link_to_a_scoped_page_is_scoped():
    md = "See [ctx](/context/) and [ctx2](/context/index.md#x)."
    out = rewrite_links(md, "safety/index.md", "go", SUP)
    assert "(/go/context/)" in out and "(/go/context/#x)" in out


def test_root_absolute_link_falls_back_when_language_lacks_the_page():
    md = "[eval](/evaluate/)"
    assert "(/python/evaluate/)" in rewrite_links(md, "x/y.md", "go", SUP)


def test_root_absolute_link_follows_the_manual_redirect_map():
    md = "[old](/old/ctx/#types)"
    out = rewrite_links(md, "x/y.md", "go", SUP, {"old/ctx.md": "context/index.md"})
    assert "(/go/context/#types)" in out


def test_root_absolute_non_page_links_are_untouched():
    md = "[api](/api-reference/python/) ![i](/assets/x.png) [s](/go/context/)"
    out = rewrite_links(md, "x/y.md", "go", SUP)
    assert "(/api-reference/python/)" in out and "(/assets/x.png)" in out
    assert "(/go/context/)" in out  # Already scoped.


def test_html_href_root_absolute_is_scoped():
    md = '<a href="/context/">ctx</a>'
    assert 'href="/go/context/"' in rewrite_links(md, "x/y.md", "go", SUP)


def test_directory_link_resolves_against_the_page_url():
    # The page safety/index.md is served at /safety/, so ../context/ is /context/.
    md = "[ctx](../context/)"
    assert "(/go/context/)" in rewrite_links(md, "safety/index.md", "go", SUP)
    # A non-index page is served one level deeper.
    md = "[ctx](../../context/)"
    assert "(/go/context/)" in rewrite_links(md, "safety/other.md", "go", SUP)


def test_links_in_indented_fences_are_untouched():
    md = (
        '=== "Windows"\n\n'
        "    ```powershell\n"
        "    [System.Environment]::SetEnvironmentVariable('K', 'v',\n"
        "      [System.EnvironmentVariableTarget]::User)\n"
        "    ```\n\n"
        "!!! example\n\n"
        "    ```\n"
        "    [user]: ai news\n"
        "    [x](../context/index.md)\n"
        "    ```\n"
    )
    out = rewrite_links(md, "agents/models/litellm.md", "python", SUP)
    assert out == md


def test_reference_definition_needs_a_space_before_the_target():
    md = "[System.Environment]::SetEnvironmentVariable\n[ctx]: ../context/index.md\n"
    out = rewrite_links(md, "safety/index.md", "go", SUP)
    assert "[System.Environment]::SetEnvironmentVariable" in out
    assert "[ctx]: /go/context/" in out


def test_inline_code_spans_are_untouched():
    md = "Use `[x](../context/index.md)` but [y](../context/index.md)."
    out = rewrite_links(md, "safety/index.md", "go", SUP)
    assert "`[x](../context/index.md)`" in out and "[y](/go/context/)" in out


def test_in_page_anchor_lost_to_another_language_points_at_its_view():
    sup = {"agents/models/gemini.md": frozenset({"python", "go"})}
    md = "the [Interactions API](#interactions-api) and [setup](#setup)"
    out = rewrite_links(
        md, "agents/models/gemini.md", "go", sup,
        foreign_anchors={"interactions-api": frozenset({"python"})},
    )
    assert "(/python/agents/models/gemini/#interactions-api)" in out
    assert "(#setup)" in out


def test_lost_anchor_still_links_when_no_built_language_has_it():
    # A build limited to Go: the Python view does not exist locally, but the
    # link must not be a dangling in-page anchor.
    sup = {"p.md": frozenset({"go"})}
    out = rewrite_links("[w](#widgets)", "p.md", "go", sup,
                        foreign_anchors={"widgets": frozenset({"python"})})
    assert "(/python/p/#widgets)" in out


def test_directory_names_with_dots_are_scoped():
    sup = {**SUP, "2.0/index.md": frozenset({"python", "go"})}
    md = "[release](/2.0/) [rel](../../2.0/#install) [img](/2.0/x.png)"
    out = rewrite_links(md, "get-started/go.md", "go", sup)
    assert "(/go/2.0/)" in out and "(/go/2.0/#install)" in out
    assert "(/2.0/x.png)" in out
