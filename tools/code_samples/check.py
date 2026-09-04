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

"""Check the Python code samples in the documentation.

Two questions are asked of every sample:

  Does it parse?  A sample a reader cannot paste into a file and run is a bug,
  and several have shipped that way.

  Do the names it imports from google.adk still exist?  This is what rots
  quietly when the library renames or moves something, because the prose keeps
  reading correctly while the code stops working.

Nothing is imported or executed from the samples themselves. They construct
agents and call live endpoints, so running one in CI would be both slow and
billable. Only the library is imported, which is what any reader does.

A sample lifted out of prose is often not a whole module, and that is fine.
Three shapes are recognised and excused:

  fragment   a method body, or a block that only makes sense indented under
             something the page shows above it
  pseudocode "..." or "<...>" standing in for omitted code, or a notebook
             magic such as !pip
  signature  a def or a class listed with no body, to describe an interface

Run it over the whole tree, or pass paths to check only those files.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import collections
import importlib
import pathlib
import re
import sys
import textwrap
import warnings

import fences

# Importing parts of google.adk emits experimental-feature and deprecation
# notices. They are about the library, not about the samples, and they bury the
# output that matters.
warnings.filterwarnings("ignore")

DOCS = pathlib.Path("docs")
PY_LANGUAGES = {"python", "py"}
WATCHED_PACKAGE = "google.adk"

ELISION = re.compile(r"^\s*\.\.\.\s*,?\s*$|<\.\.\.|\.\.\.\s*>|^\s*[!%][A-Za-z]")
ELISION_INLINE = re.compile(r"[(,]\s*\.\.\.\s*[,)]")
NEEDS_BODY = re.compile(r"expected an indented block")
BUILTINS = frozenset(dir(builtins))


class Defect(collections.namedtuple("Defect", "path line kind detail")):
    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.kind}: {self.detail}"


# --------------------------------------------------------------------------
# Does it parse?
# --------------------------------------------------------------------------


def _compiles(source: str) -> str | None:
    try:
        compile(source, "<sample>", "exec")
        return None
    except SyntaxError as exc:
        return f"line {exc.lineno}: {exc.msg}"
    except ValueError as exc:
        return str(exc)


def _is_pseudocode(source: str) -> bool:
    return any(
        ELISION.search(line) or ELISION_INLINE.search(line)
        for line in source.split("\n")
    )


def _body_omitted(source: str, error: str) -> bool:
    """True when a block's body was written as comments, or left out."""
    if not NEEDS_BODY.search(error):
        return False
    match = re.search(r"line (\d+):", error)
    if not match:
        return False
    lines = source.split("\n")
    index = int(match.group(1)) - 1
    if index >= len(lines):
        return True
    rest = [l for l in lines[index:] if l.strip()]
    # The reported line is often the header's own closing paren.
    if rest and re.sub(r"\s+#.*$", "", rest[0]).rstrip().endswith(":"):
        rest = rest[1:]
    return not rest or all(l.lstrip().startswith("#") for l in rest)


def check_parses(source: str) -> str | None:
    """Return a defect description, or None if the sample is acceptable."""
    error = _compiles(source)
    if error is None:
        return None

    flat = textwrap.dedent(source)
    if flat != source and _compiles(flat) is None:
        return None

    indented = textwrap.indent(flat, "    ")
    for wrapper in ("if True:\n", "class _C:\n", "async def _f():\n"):
        if _compiles(wrapper + indented) is None:
            return None
    # An excerpt from inside an async loop may use await, break and continue.
    deeper = textwrap.indent(flat, "        ")
    if _compiles(f"async def _f():\n    while True:\n{deeper}") is None:
        return None

    if _is_pseudocode(source) or _body_omitted(source, error):
        return None
    return error


# --------------------------------------------------------------------------
# Do the imported names exist?
# --------------------------------------------------------------------------

_module_cache: dict[str, object | None] = {}


def _load(name: str) -> object | None:
    if name not in _module_cache:
        try:
            _module_cache[name] = importlib.import_module(name)
        except Exception:  # noqa: BLE001 - any failure means "cannot resolve"
            _module_cache[name] = None
    return _module_cache[name]


def _has_attribute(module_name: str, module: object, attribute: str) -> bool:
    try:
        if hasattr(module, attribute):
            return True
    except ImportError:
        # A lazy loader that raises has still declared the name; it only needs
        # an optional dependency that is not installed here.
        return True
    except Exception:  # noqa: BLE001
        return True
    return _load(f"{module_name}.{attribute}") is not None


def check_imports(source: str) -> list[str]:
    """Return descriptions of any google.adk import that cannot be resolved."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []  # the parse check already reported on this sample

    problems: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level or not (node.module or "").startswith(WATCHED_PACKAGE):
                continue
            module = _load(node.module)
            if module is None:
                problems.append(f"no module named {node.module!r}")
                continue
            for alias in node.names:
                if alias.name != "*" and not _has_attribute(node.module, module, alias.name):
                    problems.append(f"{node.module} has no {alias.name!r}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(WATCHED_PACKAGE) and _load(alias.name) is None:
                    problems.append(f"no module named {alias.name!r}")
    return problems


# --------------------------------------------------------------------------


def check_file(path: pathlib.Path, root: pathlib.Path) -> list[Defect]:
    defects: list[Defect] = []
    for fence in fences.parse(path):
        if fence.language not in PY_LANGUAGES or fence.is_pointer:
            continue
        source = fences.resolve_includes(fence.text, root).strip("\n")
        if not source:
            continue
        error = check_parses(source)
        if error:
            defects.append(Defect(path, fence.start_line, "does not parse", error))
            continue
        for problem in check_imports(source):
            defects.append(Defect(path, fence.start_line, "unresolved import", problem))
    return defects


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=pathlib.Path,
                        help="markdown files to check; defaults to all of docs/")
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."),
                        help="repository root, used to resolve snippet includes")
    args = parser.parse_args(argv)

    targets = args.paths or sorted((args.root / DOCS).rglob("*.md"))
    targets = [p for p in targets if p.suffix == ".md" and p.is_file()]

    defects: list[Defect] = []
    for path in targets:
        defects.extend(check_file(path, args.root))

    print(f"checked {len(targets)} page(s)")
    if not defects:
        print("no defects")
        return 0

    by_kind = collections.Counter(d.kind for d in defects)
    print(f"{len(defects)} defect(s): " + ", ".join(f"{v} {k}" for k, v in by_kind.items()))
    print()
    for defect in defects:
        print(defect)
    print()
    print("Each sample above either cannot be parsed, or imports a name that")
    print("google-adk no longer provides. Fix the sample, or if it is meant to")
    print("be illustrative rather than runnable, mark the omitted part with")
    print("'...' so it is recognised as pseudocode.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
