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

from langscope import nav

SUPPORTED = {
    "agents/index.md": frozenset({"python", "java"}),
    "agents/managed-agents.md": frozenset({"python"}),
    "community/index.md": frozenset({"python", "typescript", "go", "java", "kotlin"}),
}

NAV = [
    {"Home": "index.md"},
    {"Agents": [
        {"Overview": "agents/index.md"},
        {"Managed agents": "agents/managed-agents.md"},
    ]},
    {"Community": "community/index.md"},
    {"API Reference": [
        {"Python ADK": "api-reference/python/index.html"},
        {"Go ADK": "https://pkg.go.dev/x"},
        {"Overview": "api-reference/index.md"},
    ]},
]


def test_is_scopable():
    assert nav.is_scopable("agents/index.md")
    assert not nav.is_scopable("index.md")
    assert not nav.is_scopable("api-reference/index.md")
    assert not nav.is_scopable("_includes/x.md")
    assert not nav.is_scopable("assets/logo.png")


def test_scope_nav_prefixes_and_prunes():
    out = nav.scope_nav(NAV[1:2], SUPPORTED, "python")
    assert out == [{"Agents": [
        {"Overview": "python/agents/index.md"},
        {"Managed agents": "python/agents/managed-agents.md"},
    ]}]


def test_scope_nav_drops_unsupported_and_empty_sections():
    out = nav.scope_nav(NAV[1:2], SUPPORTED, "go")
    # agents/index.md excludes go, managed-agents excludes go -> section empties
    assert out == []


def test_scope_nav_passes_through_external_html_and_apiref():
    out = nav.scope_nav(NAV[3:4], SUPPORTED, "java")
    assert out == [{"API Reference": [
        {"Python ADK": "api-reference/python/index.html"},
        {"Go ADK": "https://pkg.go.dev/x"},
        {"Overview": "api-reference/index.md"},
    ]}]


def test_scope_nav_drops_two_level_nested_section_when_all_leaves_prune():
    nested = [
        {"Outer": [
            {"Inner": [
                {"Overview": "agents/index.md"},
                {"Managed agents": "agents/managed-agents.md"},
            ]},
        ]},
    ]
    # For 'go', both leaves prune -> Inner empties -> Outer empties -> dropped.
    assert nav.scope_nav(nested, SUPPORTED, "go") == []
    # Sanity: 'python' keeps the full two-level structure.
    assert nav.scope_nav(nested, SUPPORTED, "python") == [
        {"Outer": [
            {"Inner": [
                {"Overview": "python/agents/index.md"},
                {"Managed agents": "python/agents/managed-agents.md"},
            ]},
        ]},
    ]


def test_build_multilang_nav_has_home_plus_five_sections():
    out = nav.build_multilang_nav(NAV, SUPPORTED)
    assert out[0] == {"Home": "index.md"}
    assert [next(iter(d)) for d in out[1:]] == [
        "Python", "TypeScript", "Go", "Java", "Kotlin"
    ]


def test_build_multilang_nav_limited_to_some_languages():
    out = nav.build_multilang_nav(NAV, SUPPORTED, ["go", "python"])
    # Declared order, whatever order the subset is given in.
    assert [next(iter(d)) for d in out[1:]] == ["Python", "Go"]
