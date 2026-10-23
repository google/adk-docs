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

"""Builds the fixture site with the hook and checks the generated output."""

import os
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

FIXTURE = pathlib.Path(__file__).resolve().parent / "fixture"


def _run(tmp_path, env=None, cwd=FIXTURE):
    site = tmp_path / "site"
    result = subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "-f", "mkdocs.yml",
         "-d", str(site), "--strict"],
        cwd=cwd, capture_output=True, text=True, check=False,
        env={**os.environ, "MKDOCS_LANGSCOPE_LANGUAGES": "",
             "MKDOCS_LANGSCOPE_SKIP": "", **(env or {})},
    )
    return site, result


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    site, result = _run(tmp_path_factory.mktemp("full"))
    assert result.returncode == 0, result.stderr
    return site, result.stderr


@pytest.fixture(scope="module")
def site(built):
    return built[0]


def read(site, path):
    return (site / path).read_text(encoding="utf-8")


def test_generates_per_language_pages(site):
    assert (site / "python" / "agents" / "index.html").is_file()
    assert (site / "java" / "agents" / "index.html").is_file()
    # The banner (with a title attribute) limits agents.md to Python and Java.
    assert not (site / "go" / "agents" / "index.html").exists()


def test_neutral_page_appears_in_all_five(site):
    for lang in ("python", "typescript", "go", "java", "kotlin"):
        assert (site / lang / "neutral" / "index.html").is_file()


def test_frontmatter_languages_limits_a_page(site):
    assert (site / "go" / "quick-go" / "index.html").is_file()
    assert not (site / "python" / "quick-go" / "index.html").exists()


def test_excluded_docs_are_not_scanned(site):
    # drafts/bad.md names an unknown language; scanning it would fail the build.
    assert not (site / "python" / "drafts").exists()


def test_flattened_page_has_one_language_and_its_badge(site):
    html = read(site, "python/agents/index.html")
    assert "a = 1" in html and "int a = 1" not in html
    assert "Python v1.0" in html and "Java v0.5" not in html
    assert "Agents support Python and Java." not in html


def test_section_banner_and_aside_scope_content(site):
    go = read(site, "go/neutral/index.html")
    assert "Only for Python readers." not in go and "Kotlin aside." not in go
    assert "adkgo run" in go and "adk run<" not in go
    py = read(site, "python/neutral/index.html")
    assert "Only for Python readers." in py and "adkgo run" not in py


def test_dropped_group_gets_a_note_and_a_log_line(built):
    site, log = built
    assert "Not yet available for Kotlin" in read(site, "kotlin/neutral/index.html")
    assert "neutral.md: 2 tab group(s) with no Kotlin tab" in log


def test_removals_are_logged(built):
    _, log = built
    assert re.search(
        r"neutral\.md: line \d+: section banner 'Widgets' \(marker, for "
        r"Python\) left out of the Go view", log)
    assert re.search(
        r"neutral\.md: line \d+: admonition 'Kotlin only' \(heuristic, for "
        r"Kotlin\) left out of the Python view", log)
    assert re.search(r"\d+ sections or admonitions for other languages", log)


def test_content_in_no_view_fails_a_strict_build(built, tmp_path):
    _, log = built
    assert "0 source spans reach no view" in log
    # A Go tab on a page that only supports Python and Java reaches no view.
    fixture = tmp_path / "fixture"
    shutil.copytree(FIXTURE, fixture)
    hook = FIXTURE.parents[2] / "hooks" / "language_scope.py"
    config = fixture / "mkdocs.yml"
    config.write_text(config.read_text(encoding="utf-8").replace(
        "../../../hooks/language_scope.py", str(hook)), encoding="utf-8")
    agents = fixture / "docs" / "agents.md"
    agents.write_text(agents.read_text(encoding="utf-8")
                      + '\n=== "Go"\n\n    go tool has no view\n',
                      encoding="utf-8")
    _, result = _run(tmp_path, cwd=fixture)
    assert result.returncode != 0
    assert re.search(
        r"WARNING +- +language_scope: agents\.md: lines 29-29 reach no "
        r"language view .*go tool has no view", result.stderr)
    assert "1 source spans reach no view" in result.stderr


def test_links_are_scoped_and_code_is_untouched(site):
    go = read(site, "go/neutral/index.html")
    assert 'href="/go/get-started/"' in go  # Root-absolute link scoped.
    assert 'href="/go/neutral/"' in go  # Through the manual redirect map.
    assert 'href="/python/agents/"' in go  # No Go agents page: fall back.
    assert "[System.Environment]::SetEnvironmentVariable" in go


def test_lost_in_page_anchor_links_to_a_view_that_has_it(site):
    go = read(site, "go/neutral/index.html")
    assert 'href="/python/neutral/#widgets"' in go
    assert 'href="#widgets"' in read(site, "python/neutral/index.html")


def test_pages_are_self_canonical(site):
    html = read(site, "go/neutral/index.html")
    assert '<link rel="canonical" href="https://example.com/go/neutral/"' in html


def test_edit_link_points_at_the_source_file(site):
    html = read(site, "go/neutral/index.html")
    assert "https://github.com/example/docs/edit/main/docs/neutral.md" in html
    assert "docs/go/neutral.md" not in html


def test_flat_url_is_a_language_aware_redirect(site):
    html = read(site, "agents/index.html")
    assert "Redirecting" in html and "a = 1" not in html
    assert '["python", "java"]' in html  # Candidates for the saved language.
    assert 'localStorage.getItem("adk-lang")' in html
    assert 'url=../python/agents/' in html  # No-JS fallback: default language.
    assert '<link rel="canonical" href="https://example.com/python/agents/">' in html


def test_manual_redirect_keeps_its_fragment(site):
    html = read(site, "moved/index.html")
    assert 'url=../python/agents/#tools' in html


def test_scope_root_redirects_to_get_started(site):
    html = read(site, "go/index.html")
    assert 'url=get-started/' in html


def test_root_index_stays_unscoped(site):
    assert (site / "index.html").is_file()
    assert (site / "api-reference" / "index.html").is_file()


def test_per_language_llms_txt(site):
    go = read(site, "go/llms.txt")
    assert go.startswith("# Fixture for Go")
    assert "https://example.com/go/quick-go/index.md" in go
    assert "agents/index.md" not in go  # No Go view.
    assert "https://example.com/api-reference/index.md" in go  # Shared page.
    assert (site / "go" / "llms-full.txt").is_file()
    assert "a = 1" in read(site, "python/llms-full.txt")


def test_root_llms_txt_links_languages_and_flat_pages(site):
    root = read(site, "llms.txt")
    assert "https://example.com/go/llms.txt" in root
    assert "https://example.com/python/agents/index.md" in root
    assert "https://example.com/go/quick-go/index.md" in root  # Go-only page.


def test_markdown_views_exist_for_every_language(site):
    assert (site / "kotlin" / "neutral" / "index.md").is_file()
    # The old flat .md URL still serves the default-language Markdown.
    assert "a = 1" in read(site, "agents/index.md")


def test_language_subset_build(tmp_path):
    site, result = _run(tmp_path, {"MKDOCS_LANGSCOPE_LANGUAGES": "go"})
    assert result.returncode == 0, result.stderr
    assert (site / "go" / "neutral" / "index.html").is_file()
    assert not (site / "python").exists()
    # agents.md is in no built language: no redirect to a missing page.
    assert not (site / "agents" / "index.html").exists()
    assert "https://example.com/go/llms.txt" in read(site, "llms.txt")
    # Links to pages outside the build still use their full-site URL.
    assert 'href="/python/agents/"' in read(site, "go/neutral/index.html")


def test_skip_builds_only_the_default_language(tmp_path):
    site, result = _run(tmp_path, {"MKDOCS_LANGSCOPE_SKIP": "1"})
    assert result.returncode == 0, result.stderr
    assert (site / "python" / "neutral" / "index.html").is_file()
    assert not (site / "go").exists()


def test_unknown_language_fails_the_build(tmp_path):
    _, result = _run(tmp_path, {"MKDOCS_LANGSCOPE_LANGUAGES": "python,cobol"})
    assert result.returncode != 0
    assert re.search(r"unknown language 'cobol'", result.stderr)


def _hook():
    import importlib.util
    path = FIXTURE.parents[2] / "hooks" / "language_scope.py"
    spec = importlib.util.spec_from_file_location("language_scope_hook", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # Dataclasses look their module up.
    spec.loader.exec_module(module)
    return module


def test_orphaned_spans_finds_lines_no_view_has():
    hook = _hook()
    source = (
        "---\nx: 1\n---\n# T\n\nshared\n\n=== \"Java\"\n\n    ```java\n"
        "    int a = 1;\n    int b = 2;\n    ```\n\nshared again\n\ngone\n"
    )
    views = ["# T\n\nshared\n\nshared again\n"]
    assert hook.orphaned_spans(source, views) == [
        (10, 12, "```java"), (17, 17, "gone")]
    assert hook.orphaned_spans(source, [source]) == []
