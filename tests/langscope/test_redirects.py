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

from langscope import redirects

SUP = {
    "agents/index.md": frozenset({"python", "java"}),
    "runtime/api-server.md": frozenset({"python"}),
    "integrations/index.md": frozenset({"python"}),
    "agents/routing.md": frozenset({"typescript"}),  # no python
}


def test_flat_pages_redirect_to_default_scope():
    out = redirects.build_redirect_map(
        ["agents/index.md", "runtime/api-server.md"], {}, SUP
    )
    assert out["agents/index.md"] == "python/agents/index.md"
    assert out["runtime/api-server.md"] == "python/runtime/api-server.md"


def test_page_without_python_redirects_to_first_supported():
    out = redirects.build_redirect_map(["agents/routing.md"], {}, SUP)
    assert out["agents/routing.md"] == "typescript/agents/routing.md"


def test_existing_manual_redirects_are_retargeted():
    out = redirects.build_redirect_map(
        ["runtime/api-server.md"],
        {"get-started/local-testing.md": "runtime/api-server.md"},
        SUP,
    )
    assert out["get-started/local-testing.md"] == "python/runtime/api-server.md"


def test_non_scopable_destinations_pass_through():
    out = redirects.build_redirect_map(
        [], {"tools/index.md": "integrations/index.md"}, SUP
    )
    # integrations/index.md IS scopable -> retargeted
    assert out["tools/index.md"] == "python/integrations/index.md"


def test_manual_redirect_with_fragment_keeps_it():
    out = redirects.build_redirect_map(
        [], {"old.md": "agents/index.md#tools"}, SUP)
    assert out["old.md"] == "python/agents/index.md#tools"


def test_external_redirects_pass_through():
    out = redirects.build_redirect_map([], {"x.md": "https://example.com/"}, SUP)
    assert out["x.md"] == "https://example.com/"


def test_subset_of_languages_retargets_or_omits():
    out = redirects.build_redirect_map(
        list(SUP), {"old.md": "runtime/api-server.md"}, SUP,
        frozenset({"java", "typescript"}),
    )
    assert out["agents/index.md"] == "java/agents/index.md"
    assert out["agents/routing.md"] == "typescript/agents/routing.md"
    # Python-only pages are not built, so nothing redirects to them.
    assert "runtime/api-server.md" not in out and "old.md" not in out


def test_target_language_prefers_default_then_declared_order():
    assert redirects.target_language("agents/index.md", SUP) == "python"
    assert redirects.target_language("agents/routing.md", SUP) == "typescript"
    assert redirects.target_language("unknown.md", SUP) == "python"
