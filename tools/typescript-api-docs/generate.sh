#!/usr/bin/env bash
#
# Generates TypeScript API reference documentation for adk-js using TypeDoc.
# Outputs HTML to docs/api-reference/typescript/.
#
# This script runs in an isolated temporary directory and does not
# modify any existing adk-js clones or local Node environments. The npm
# cache is redirected into the temp workspace, so nothing on the host is
# modified (no global installs, no changes to ~/.npm).
#
# Prerequisites: node (18+), npm, git
# Run from: adk-docs repository root
#
# The <version> is the @google/adk (core) package version; the script clones
# the corresponding adk-vX.Y.Z release tag.
#
# Usage: bash tools/typescript-api-docs/generate.sh <version>
# Example: bash tools/typescript-api-docs/generate.sh 1.5.0

set -e

# Validate arguments
VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 1.5.0"
  exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Version must be in X.Y.Z format (e.g., 1.5.0)"
  exit 1
fi

# Check prerequisites
for cmd in node npm git; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: $cmd is required but not installed."
    if [[ "$cmd" == "node" || "$cmd" == "npm" ]]; then
      echo "  Install with: brew install node"
    fi
    exit 1
  fi
done

# Validate working directory
TARGET_DIR="docs/api-reference/typescript"
if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: Run this script from the adk-docs repository root."
  exit 1
fi

# Create temp workspace
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT
echo "Using temp workspace: $WORK_DIR"

# Isolate the npm cache inside the temp workspace so the host's ~/.npm is
# left untouched (throwaway, clean-room build).
export npm_config_cache="$WORK_DIR/.npm-cache"

# Build docs in temp workspace
pushd "$WORK_DIR" > /dev/null || exit 1

# Clone adk-js
#
# adk-js is a release-please monorepo with per-package, linked-version tags.
# The core package (@google/adk, whose sources feed the TypeDoc docs) is
# tagged adk-vX.Y.Z. All component tags for a release point to the same
# commit, so adk-v<version> is the correct, package-aligned ref.
echo "Cloning adk-js adk-v${VERSION}..."
git clone --depth 1 --branch "adk-v${VERSION}" https://github.com/google/adk-js adk-js
cd adk-js

# Install dependencies (reproducible; package-lock.json ships in the repo)
echo "Installing dependencies..."
npm ci

# Build TypeDoc HTML docs (writes to api-reference/typescript/ in the clone).
# --includeVersion appends the @google/adk package version (from core/package.json,
# which matches the cloned adk-v<version> tag) to the header title.
echo "Building TypeScript API docs with TypeDoc..."
npm run docs:generate -- --includeVersion

popd > /dev/null || exit 1

# Copy to output directory
echo "Copying to $TARGET_DIR..."
rm -rf "$TARGET_DIR"/*
cp -r "$WORK_DIR/adk-js/api-reference/typescript"/* "$TARGET_DIR/"

# Add Google Analytics tag to generated HTML files
echo "Adding Google Analytics tag..."
GA_TAG_FILE=$(mktemp)
cat > "$GA_TAG_FILE" <<'EOF'
<!-- Google Analytics tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-DKHZS27PHP"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-DKHZS27PHP');
</script>
EOF
GA_TAG=$(<"$GA_TAG_FILE")
rm -f "$GA_TAG_FILE"
export GA_TAG
find "$TARGET_DIR" -name '*.html' -print0 | while IFS= read -r -d '' file; do
  awk 'BEGIN{tag=ENVIRON["GA_TAG"]} {gsub(/<\/head>/, "\n" tag "\n</head>")}1' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
done

echo "Done."
