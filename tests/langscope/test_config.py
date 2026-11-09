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

from langscope import config


def test_five_languages_in_canonical_order():
    assert [lang.key for lang in config.LANGUAGES] == [
        "python", "typescript", "go", "java", "kotlin"
    ]
    assert config.ORDERED_KEYS == tuple(lang.key for lang in config.LANGUAGES)


def test_default_language_is_python():
    assert config.DEFAULT_LANGUAGE == "python"


def test_all_keys_is_frozenset():
    assert config.ALL_KEYS == frozenset(
        {"python", "typescript", "go", "java", "kotlin"}
    )


def test_labels_come_from_languages():
    assert config.LABELS == {lang.key: lang.label for lang in config.LANGUAGES}


def test_label_to_key_matches_case_insensitively_and_aliases():
    assert config.label_to_key("Python") == "python"
    assert config.label_to_key("TypeScript") == "typescript"
    assert config.label_to_key("golang") == "go"
    assert config.label_to_key("Bash") is None


def test_parse_label_reads_a_leading_language_token():
    assert config.parse_label("Python - adk CLI") == (frozenset({"python"}), "adk CLI")
    assert config.parse_label("Go - adkgo CLI") == (frozenset({"go"}), "adkgo CLI")
    assert config.parse_label("Python (Telegram)") == (frozenset({"python"}), "Telegram")


def test_parse_label_joins_language_runs():
    assert config.parse_label("JavaScript / TypeScript") == (
        frozenset({"typescript"}), "")
    assert config.parse_label("JavaScript / TypeScript (Telegram)") == (
        frozenset({"typescript"}), "Telegram")
    assert config.parse_label("Java and Kotlin") == (
        frozenset({"java", "kotlin"}), "")


def test_parse_label_ignores_non_language_labels():
    assert config.parse_label("Gemini - Google AI Studio")[0] == frozenset()
    assert config.parse_label("API Testing (curl)")[0] == frozenset()
    assert config.parse_label("Maven")[0] == frozenset()
    # A language word that runs on into prose is not a language tab.
    assert config.parse_label("Go further")[0] == frozenset()


def test_exact_label_keys():
    assert config.exact_label_keys("Python and TypeScript") == frozenset(
        {"python", "typescript"})
    assert config.exact_label_keys("Python - adk CLI") == frozenset()
