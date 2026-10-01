#!/usr/bin/env bash
#
# Generates REST API reference documentation for adk-python by extracting
# the OpenAPI spec from the FastAPI app and rendering it with Swagger UI
# (loaded from CDN). Outputs to docs/api-reference/rest/.
#
# This script runs in an isolated temporary directory and does not
# modify any existing adk-python clones or Python environments.
#
# Prerequisites: uv, git
# Run from: adk-docs repository root
#
# Usage: bash tools/python-rest-api-docs/generate.sh <version>
# Example: bash tools/python-rest-api-docs/generate.sh 1.27.0

set -e

# Validate arguments
VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 1.27.0"
  exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Version must be in X.Y.Z format (e.g., 1.27.0)"
  exit 1
fi

# Check prerequisites
for cmd in uv git; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: $cmd is required but not installed."
    exit 1
  fi
done

# Validate working directory
TARGET_DIR="docs/api-reference/rest"
if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: Run this script from the adk-docs repository root."
  exit 1
fi

# Create temp workspace
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT
echo "Using temp workspace: $WORK_DIR"

pushd "$WORK_DIR" > /dev/null || exit 1

# --- Extract OpenAPI spec from adk-python ---

uv venv
source .venv/bin/activate

echo "Cloning adk-python v${VERSION}..."
git clone --depth 1 --branch "v${VERSION}" https://github.com/google/adk-python adk-python
uv pip install ./adk-python

echo "Extracting OpenAPI spec..."
python3 -c "
import json, tempfile, os

os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'FALSE'

from google.adk.cli.fast_api import get_fast_api_app

with tempfile.TemporaryDirectory() as agents_dir:
    app = get_fast_api_app(agents_dir=agents_dir, web=False, use_local_storage=False)
    spec = app.openapi()
    spec['info']['title'] = 'ADK REST API Reference'
    spec['info']['version'] = '${VERSION}'
    print(json.dumps(spec, indent=2))
" > openapi.json

echo "Extracted $(python3 -c "import json; d=json.load(open('openapi.json')); print(len(d.get('paths', {})))") endpoints."

# --- Generate index.html with Swagger UI from CDN ---

cat > index.html <<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ADK REST API Reference</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
  <!-- Google Analytics tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-DKHZS27PHP"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-DKHZS27PHP');
  </script>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: "./openapi.json",
      dom_id: "#swagger-ui",
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis],
      layout: "BaseLayout"
    });
  </script>
</body>
</html>
HTML

popd > /dev/null || exit 1

# --- Copy to output directory ---

echo "Copying to $TARGET_DIR..."
rm -rf "$TARGET_DIR"/*
cp "$WORK_DIR/openapi.json" "$TARGET_DIR/"
cp "$WORK_DIR/index.html" "$TARGET_DIR/"

echo "Done."
