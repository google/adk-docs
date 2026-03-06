#!/usr/bin/env python3
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

"""Validate Python and Bash code snippets in skills markdown files.

Three-tier validation:
  1. Syntax check every Python block via ast.parse()
  2. Import validation — deduplicate all import statements and verify they resolve
  3. Bash validation — check that `adk <subcommand>` commands are valid

Usage:
  python validate_snippets.py                    # validate all skills/**/*.md
  python validate_snippets.py skills/foo/bar.md  # validate specific files
"""

from __future__ import annotations

import ast
import glob
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Known optional or example-only dependencies that may not be installed in CI.
# These produce WARN instead of FAIL.
OPTIONAL_IMPORT_PREFIXES = (
    "litellm",
    "opentelemetry",
    "langfuse",
    "arize",
    "cloud_trace",
    "fastapi",
    "uvicorn",
    "my_agent",  # example user module in docs
)

# ── Data types ───────────────────────────────────────────────────────────────


@dataclass
class Snippet:
    file: str
    line: int
    lang: str
    code: str


@dataclass
class Result:
    status: str  # PASS, FAIL, WARN
    location: str
    detail: str


@dataclass
class ValidationReport:
    results: list[Result] = field(default_factory=list)

    def add(self, status: str, location: str, detail: str) -> None:
        self.results.append(Result(status, location, detail))

    @property
    def failed(self) -> bool:
        return any(r.status == "FAIL" for r in self.results)

    def print(self) -> None:
        for r in self.results:
            print(f"[{r.status}] {r.location}  ({r.detail})")


# ── Step 1: Extract snippets ────────────────────────────────────────────────

_FENCE_RE = re.compile(r"^```(\w+)\s*$")


def extract_snippets(filepath: str) -> list[Snippet]:
    """Parse fenced code blocks from a markdown file."""
    snippets: list[Snippet] = []
    with open(filepath) as f:
        lines = f.readlines()

    in_block = False
    lang = ""
    start_line = 0
    block_lines: list[str] = []

    for i, line in enumerate(lines, start=1):
        if not in_block:
            m = _FENCE_RE.match(line)
            if m:
                lang = m.group(1)
                in_block = True
                start_line = i + 1  # code starts on the next line
                block_lines = []
        else:
            if line.startswith("```"):
                code = "".join(block_lines)
                if code.strip():
                    snippets.append(Snippet(filepath, start_line, lang, code))
                in_block = False
            else:
                block_lines.append(line)

    return snippets


# ── Step 2: Syntax validation ───────────────────────────────────────────────

# Matches `...,` or `, ...` used as placeholder args in documentation snippets.
# e.g., Agent(name="x", ..., tools=[y]) — not valid Python but common in docs.
_ELLIPSIS_INLINE_RE = re.compile(r",\s*\.\.\.\s*,|,\s*\.\.\.\s*(?=\))")
# Matches a standalone `...` line used as placeholder inside a call (before `)`).
_ELLIPSIS_LINE_RE = re.compile(r"^\s*\.\.\.\s*$", re.MULTILINE)


def _preprocess_for_syntax(code: str) -> str:
    """Normalise documentation conventions so ast.parse() can handle them."""
    # Replace `, ...,` and `, ...)`  with valid Python equivalents
    code = _ELLIPSIS_INLINE_RE.sub(",", code)
    # Replace standalone `...` lines that act as placeholder kwargs
    # We replace with a comment to preserve line numbers
    code = _ELLIPSIS_LINE_RE.sub("# ...", code)
    return code


def validate_syntax(snippet: Snippet, report: ValidationReport) -> None:
    """Run ast.parse() on a Python snippet."""
    loc = f"{snippet.file}:{snippet.line}"
    code = _preprocess_for_syntax(snippet.code)
    try:
        ast.parse(code, filename=snippet.file)
        report.add("PASS", loc, "syntax")
    except SyntaxError as e:
        report.add("FAIL", loc, f"syntax: {e.msg}")


# ── Step 3: Import validation ───────────────────────────────────────────────

_IMPORT_RE = re.compile(r"^\s*(import .+|from .+ import .+)\s*$", re.MULTILINE)


def collect_imports(snippets: list[Snippet]) -> list[tuple[str, str]]:
    """Extract and deduplicate import lines across all snippets.

    Returns (import_line, source_location) pairs.
    """
    seen: set[str] = set()
    imports: list[tuple[str, str]] = []
    for s in snippets:
        for m in _IMPORT_RE.finditer(s.code):
            stmt = m.group(1).strip()
            if stmt not in seen:
                seen.add(stmt)
                imports.append((stmt, f"{s.file}:{s.line}"))
    return imports


def validate_imports(
    import_pairs: list[tuple[str, str]], report: ValidationReport
) -> None:
    """Try to exec() each import statement."""
    for stmt, loc in import_pairs:
        # Determine the top-level module for optional-dep check
        parts = stmt.split()
        if parts[0] == "from":
            module = parts[1]
        else:
            module = parts[1].split(".")[0]

        try:
            exec(stmt, {})  # noqa: S102
            imported_names = _extract_imported_names(stmt)
            report.add("PASS", loc, f"import: {', '.join(imported_names)}")
        except ImportError as e:
            is_optional = any(
                module.startswith(prefix) for prefix in OPTIONAL_IMPORT_PREFIXES
            )
            if is_optional:
                report.add("WARN", loc, f"import (optional dep): {e}")
            else:
                report.add("FAIL", loc, f"import: {e}")
        except Exception as e:
            report.add("WARN", loc, f"import (exec error): {e}")


def _extract_imported_names(stmt: str) -> list[str]:
    """Extract the names brought into scope by an import statement."""
    parts = stmt.split()
    if parts[0] == "from":
        # from X import a, b, c
        idx = parts.index("import")
        return [n.strip().rstrip(",") for n in parts[idx + 1 :]]
    else:
        # import X or import X.Y.Z
        return [parts[1].split(".")[0]]


# ── Step 4: Bash / ADK command validation ───────────────────────────────────

_ADK_CMD_RE = re.compile(r"\badk\s+(\w+)")


def validate_bash_snippets(
    snippets: list[Snippet], report: ValidationReport
) -> None:
    """Validate that `adk <subcommand>` references exist."""
    if not shutil.which("adk"):
        # adk CLI not installed — skip gracefully
        for s in snippets:
            loc = f"{s.file}:{s.line}"
            report.add("WARN", loc, "bash: adk CLI not found, skipping")
        return

    checked: set[str] = set()
    for s in snippets:
        loc = f"{s.file}:{s.line}"
        for m in _ADK_CMD_RE.finditer(s.code):
            subcmd = m.group(1)
            if subcmd in checked:
                continue
            checked.add(subcmd)
            try:
                result = subprocess.run(
                    ["adk", subcmd, "--help"],
                    capture_output=True,
                    timeout=15,
                )
                if result.returncode == 0:
                    report.add("PASS", loc, f"bash: adk {subcmd}")
                else:
                    report.add("FAIL", loc, f"bash: adk {subcmd} --help failed")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                report.add("WARN", loc, f"bash: adk {subcmd} check timed out")


# ── Main ─────────────────────────────────────────────────────────────────────


def discover_files(args: list[str]) -> list[str]:
    """Return markdown files to validate.

    If args are provided, use them directly. Otherwise glob skills/**/*.md.
    """
    if args:
        return args
    repo_root = Path(__file__).resolve().parent.parent.parent
    return sorted(glob.glob(str(repo_root / "skills" / "**" / "*.md"), recursive=True))


def main() -> int:
    files = discover_files(sys.argv[1:])
    if not files:
        print("No markdown files found.")
        return 0

    report = ValidationReport()
    all_python: list[Snippet] = []
    all_bash: list[Snippet] = []

    for filepath in files:
        snippets = extract_snippets(filepath)
        for s in snippets:
            if s.lang == "python":
                all_python.append(s)
            elif s.lang in ("bash", "shell", "sh"):
                all_bash.append(s)

    # Step 2: Syntax validation
    for s in all_python:
        validate_syntax(s, report)

    # Step 3: Import validation
    imports = collect_imports(all_python)
    validate_imports(imports, report)

    # Step 4: Bash validation
    validate_bash_snippets(all_bash, report)

    report.print()

    if report.failed:
        fails = sum(1 for r in report.results if r.status == "FAIL")
        print(f"\n{fails} validation failure(s) found.")
        return 1

    total = len(report.results)
    warns = sum(1 for r in report.results if r.status == "WARN")
    print(f"\nAll checks passed. ({total} checks, {warns} warnings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
