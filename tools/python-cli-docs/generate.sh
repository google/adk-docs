#!/usr/bin/env bash
#
# Generates CLI reference documentation for adk-python using Sphinx and
# sphinx-click. Outputs HTML to docs/api-reference/cli/.
#
# This script runs in an isolated temporary directory and does not
# modify any existing adk-python clones or Python environments.
#
# Prerequisites: uv, git, make
# Run from: adk-docs repository root
#
# Usage: bash tools/python-cli-docs/generate.sh <version>
# Example: bash tools/python-cli-docs/generate.sh 1.24.0

set -e

# Validate arguments
VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 1.24.0"
  exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Version must be in X.Y.Z format (e.g., 1.24.0)"
  exit 1
fi

# Check prerequisites
for cmd in uv git make; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: $cmd is required but not installed."
    exit 1
  fi
done

# Validate working directory
TARGET_DIR="docs/api-reference/cli"
if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: Run this script from the adk-docs repository root."
  exit 1
fi

# Create temp workspace
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT
echo "Using temp workspace: $WORK_DIR"

# Build docs in temp workspace
pushd "$WORK_DIR" > /dev/null || exit 1

# Set up Python environment
uv venv
source .venv/bin/activate

# Clone and install adk-python
echo "Cloning adk-python v${VERSION}..."
git clone --depth 1 --branch "v${VERSION}" https://github.com/google/adk-python adk-python
uv pip install sphinx sphinx-click ./adk-python

# Configure Sphinx
echo "Configuring Sphinx..."
mkdir docs_build && cd docs_build
sphinx-quickstart -q -p "ADK CLI" -a "Google" -v "${VERSION}" --ext-autodoc
echo "extensions.append('sphinx_click')" >> conf.py
echo "html_sidebars = {'**': ['searchbox.html']}" >> conf.py

# Add Google Analytics via Sphinx template
mkdir -p _templates
cat > _templates/layout.html <<'TMPL'
{% extends "!layout.html" %}
{% block extrahead %}
{{ super() }}
<!-- Google Analytics tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-DKHZS27PHP"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-DKHZS27PHP');
</script>
{% endblock %}
TMPL

# Write RST file
cat > index.rst <<EOF
ADK CLI documentation
=====================

This page contains the auto-generated command-line reference for ADK ${VERSION}.

.. contents::
   :local:
   :depth: 2

.. click:: google.adk.cli.cli_tools_click:main
   :prog: adk
   :nested: full
EOF

# Build HTML
echo "Building HTML..."
make html

popd > /dev/null || exit 1

# Copy to output directory
echo "Copying to $TARGET_DIR..."
rm -rf "$TARGET_DIR"/*
cp -r "$WORK_DIR/docs_build/_build/html"/* "$TARGET_DIR/"

echo "Done."
