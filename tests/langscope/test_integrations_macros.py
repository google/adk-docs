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

"""Checks the language-aware macros in scripts/integrations.py."""

import importlib.util
import pathlib
import types

REPO = pathlib.Path(__file__).resolve().parents[2]

LANGSCOPE = {
    "default": "python",
    "lang_keys": ["python", "go"],
    "languages": [{"key": "python", "label": "Python"},
                  {"key": "go", "label": "Go"}],
}


def _macros(tmp_path, page_uri, langscope=LANGSCOPE):
    spec = importlib.util.spec_from_file_location(
        "integrations_macros", REPO / "scripts" / "integrations.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    macros = {}
    env = types.SimpleNamespace(
        conf={"docs_dir": str(tmp_path),
              "extra": {"langscope": langscope} if langscope else {}},
        page=types.SimpleNamespace(file=types.SimpleNamespace(src_uri=page_uri)),
        macro=lambda fn: macros.setdefault(fn.__name__, fn),
    )
    module.define_env(env)
    return macros


def _integrations(tmp_path):
    d = tmp_path / "integrations"
    d.mkdir()
    (d / "py-only.md").write_text(
        "# Py tool\n\n<div class=\"language-support-tag\">"
        "<span class=\"lst-python\">Python</span></div>\n")
    (d / "everywhere.md").write_text("# Everywhere\n")


def test_catalog_in_a_language_view_lists_and_links_that_language(tmp_path):
    _integrations(tmp_path)
    out = _macros(tmp_path, "go/integrations/index.md")["render_catalog"](
        "integrations/*.md")
    assert 'href="/go/integrations/everywhere/"' in out
    assert "py-only" not in out


def test_catalog_outside_language_views_keeps_flat_links(tmp_path):
    _integrations(tmp_path)
    out = _macros(tmp_path, "integrations/index.md", None)["render_catalog"](
        "integrations/*.md")
    assert 'href="/integrations/everywhere/"' in out
    assert 'href="/integrations/py-only/"' in out


def test_sdk_picker_lists_built_languages(tmp_path):
    out = _macros(tmp_path, "index.md")["sdk_picker"]()
    assert 'href="python/get-started/"' in out and 'href="go/get-started/"' in out
    assert "icon-go.svg" in out and "kotlin" not in out


def test_sdk_picker_without_language_scoping(tmp_path):
    out = _macros(tmp_path, "index.md", None)["sdk_picker"]()
    assert 'href="get-started/"' in out
