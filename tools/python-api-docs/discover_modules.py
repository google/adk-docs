#!/usr/bin/env python3
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

"""Discovers public modules in google.adk and generates Sphinx RST.

Walks the installed google.adk package tree, applies depth and exclusion
rules, and generates the google-adk.rst file for Sphinx API reference docs.

Usage:
    python3 discover_modules.py <output_rst_path>

Example:
    python3 discover_modules.py sphinx_project/source/google-adk.rst
"""

import os
import pkgutil
import sys

# --- Configuration ---
# Adjust these when modules are added, removed, or restructured in adk-python.

# Packages to exclude from documentation entirely.
# These are internal infrastructure modules that are not user-facing.
EXCLUDE = {
    "google.adk",              # root package, nothing to document
    "google.adk.dependencies", # internal import shims for optional deps
    "google.adk.features",     # internal feature flag system
    "google.adk.cli",          # handled by the separate CLI docs script
    "google.adk.labs",         # empty namespace (labs.openai is included via depth-2 rule)
}

# Subpackage prefixes whose children (depth 2) should also be documented.
# By default, only depth-1 modules (google.adk.X) are included.
# Add a new prefix here when a new expandable namespace is introduced
# (e.g., "google.adk.connectors.").
DEPTH_2_PREFIXES = [
    "google.adk.tools.",
    "google.adk.integrations.",
    "google.adk.labs.",
]

# --- Discovery logic ---


def _collect_modules(path, prefix):
    """Return module names from a package path, filtering by depth and exclusion rules."""
    modules = []
    for _importer, name, _ispkg in pkgutil.walk_packages(path, prefix):
        parts = name.split(".")

        # Skip private modules (any component after google.adk starts with _)
        if any(p.startswith("_") for p in parts[2:]):
            continue

        # Skip excluded packages (but allow depth-2 children via DEPTH_2_PREFIXES)
        if name in EXCLUDE or any(
            name.startswith(e + ".") for e in EXCLUDE if e != "google.adk"
        ):
            if not any(name.startswith(p) for p in DEPTH_2_PREFIXES):
                continue

        depth = len(parts) - 2  # relative to google.adk

        if depth == 1:
            modules.append(name)
        elif depth == 2 and any(name.startswith(p) for p in DEPTH_2_PREFIXES):
            modules.append(name)
        # depth > 2: skip (parent's automodule :members: pulls up public symbols)

    return modules


def discover_modules():
    """Walk google.adk and return a sorted list of modules to document.

    Note: pkgutil.walk_packages does not recurse into PEP 420 namespace
    packages (subpackages without an __init__.py; CPython #73444). If a new
    subpackage ships without an __init__.py, its submodules will silently be
    missing here. The fix belongs upstream: ask ENG to add an __init__.py
    rather than reintroducing a walk-around in this script.
    """
    import google.adk

    modules = _collect_modules(google.adk.__path__, "google.adk.")
    modules.sort()
    return modules


def warn_namespace_packages(pkg):
    """Warn about subpackages lacking __init__.py (skipped by walk_packages).

    These PEP 420 namespace packages are silently missed by discover_modules
    (CPython #73444), so their submodules would be absent from the API docs.
    Surface them here so the maintainer can ask ENG to add an __init__.py.
    """
    for base in pkg.__path__:
        for entry in sorted(os.listdir(base)):
            sub = os.path.join(base, entry)
            if (
                os.path.isdir(sub)
                and not entry.startswith(("_", "."))
                and not os.path.exists(os.path.join(sub, "__init__.py"))
                and any(f.endswith(".py") for f in os.listdir(sub))
            ):
                print(
                    f"WARNING: google.adk.{entry} has no __init__.py; its "
                    f"submodules will be missing from the API docs. Ask ENG to "
                    f"add an __init__.py (CPython #73444).",
                    file=sys.stderr,
                )


def generate_rst(modules):
    """Generate RST content with automodule directives for each module."""
    lines = []
    lines.append("Submodules")
    lines.append("----------")
    lines.append("")

    for mod in modules:
        label = f"{mod} module"
        underline = "-" * len(label)

        # Escape underscores in RST headings
        heading = label.replace("_", r"\_")

        lines.append(heading)
        lines.append(underline)
        lines.append("")
        lines.append(f".. automodule:: {mod}")
        lines.append("    :members:")
        lines.append("    :undoc-members:")
        lines.append("    :show-inheritance:")
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <output_rst_path>", file=sys.stderr)
        sys.exit(1)

    output_path = sys.argv[1]

    import google.adk

    warn_namespace_packages(google.adk)

    modules = discover_modules()

    print(f"Discovered {len(modules)} modules:")
    for m in modules:
        print(f"  {m}")

    rst = generate_rst(modules)

    with open(output_path, "w") as f:
        f.write(rst)

    print(f"\nWrote {output_path}")


if __name__ == "__main__":
    main()
