#!/usr/bin/env bash
#
# Generates Java API reference documentation for adk-java using Maven Javadoc.
# Outputs HTML to docs/api-reference/java/.
#
# This script runs in an isolated temporary directory and does not
# modify any existing adk-java clones or local environments.
#
# Prerequisites: java (JDK 17+), jar, git
#
# CI builds this on the JDK pinned in update-java-api-docs.yaml, and the
# Javadoc tool version is stamped into every generated page, so a build on
# a different JDK produces a diff on every file. Match that pin when
# running by hand and you are comparing output.
# Run from: adk-docs repository root
#
# Usage: bash tools/java-api-docs/generate.sh <version>
# Example: bash tools/java-api-docs/generate.sh 1.10.1

set -euo pipefail
shopt -s failglob

# Validate arguments
VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 1.10.1"
  exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Version must be in X.Y.Z format (e.g., 1.10.1)"
  exit 1
fi

# Check prerequisites
for cmd in java jar git; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: $cmd is required but not installed."
    if [[ "$cmd" == "java" || "$cmd" == "jar" ]]; then
      echo "  Install with: brew install openjdk@26"
    fi
    exit 1
  fi
done

# Validate working directory
TARGET_DIR="docs/api-reference/java"
if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: Run this script from the adk-docs repository root."
  exit 1
fi
TARGET_ABS_DIR="$(cd "$TARGET_DIR" && pwd)"

# Create temp workspace
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT
echo "Using temp workspace: $WORK_DIR"

# Build docs in temp workspace
pushd "$WORK_DIR" > /dev/null

# Clone adk-java
echo "Cloning adk-java v${VERSION}..."
git clone --depth 1 --branch "v${VERSION}" https://github.com/google/adk-java adk-java
cd adk-java

# The footer Javadoc stamps on every page.
#
# adk-java's pom has no project-level <organization> and no <inceptionYear> --
# the only <organization> in it is inside <developers>, which is a different
# field and not one the Javadoc plugin reads. Its default footer is
# "Copyright {inceptionYear}-{currentYear} {organizationName}. All rights
# reserved.", so with two of those three empty the published pages have been
# carrying "Copyright (c) 1980. All rights reserved." -- no owner, and a year
# that is the ZIP epoch rather than a date anything happened.
#
# Rather than wait on an upstream pom change, set the footer here. The year is
# the year of the release being documented, taken from the tag we just checked
# out, not the year the build happens to run: these pages are committed to
# this repository, so a footer that followed the wall clock would rewrite
# every one of them the first time anybody rebuilt an old version.
RELEASE_YEAR=$(git -C "$WORK_DIR/adk-java" log -1 --format=%cd --date=format:%Y)
if [[ ! "$RELEASE_YEAR" =~ ^[0-9]{4}$ ]]; then
  echo "Error: could not read the release year from the adk-java tag." >&2
  exit 1
fi
JAVADOC_BOTTOM="Copyright &#169; ${RELEASE_YEAR} Google LLC."
echo "Footer: ${JAVADOC_BOTTOM}"

# Build aggregated Javadoc JAR
echo "Building Java API docs with Maven Javadoc..."
./mvnw -B --no-transfer-progress clean javadoc:aggregate-jar \
  -Dbottom="${JAVADOC_BOTTOM}"

# Resolve the aggregate javadoc jar, asserting there is exactly one match.
javadoc_jars=("$WORK_DIR"/adk-java/target/google-adk-parent-*-javadoc.jar)
if [[ ${#javadoc_jars[@]} -ne 1 ]]; then
  echo "Error: Expected exactly one javadoc jar, found ${#javadoc_jars[@]}:" >&2
  printf '  %s\n' "${javadoc_jars[@]}" >&2
  exit 1
fi

popd > /dev/null

# Extract to output directory
echo "Extracting to $TARGET_DIR..."
rm -rf "${TARGET_ABS_DIR:?}"/*
pushd "$TARGET_ABS_DIR" > /dev/null
jar -xf "${javadoc_jars[0]}"
# The extracted jar contains a META-INF directory (just MANIFEST.MF build
# metadata, no documentation) that should not be published.
rm -rf META-INF
popd > /dev/null

# Add Google Analytics tag to generated HTML files
echo "Adding Google Analytics tag..."
GA_TAG_FILE=$(mktemp)
cat > "$GA_TAG_FILE" <<'EOF'
<!-- Google Analytics tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-DKHZS27PHP"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag("js", new Date());
    gtag("config", "G-DKHZS27PHP");
  </script>
EOF
GA_TAG=$(<"$GA_TAG_FILE")
rm -f "$GA_TAG_FILE"
export GA_TAG
find "$TARGET_DIR" -name '*.html' -print0 | while IFS= read -r -d '' file; do
  awk 'BEGIN{tag=ENVIRON["GA_TAG"]} {sub(/<head>/, "<head>\n" tag)}1' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
done

# Verify that index.html renders the requested version
echo "Verifying rendered version..."
RENDERED=$(grep -oE 'Maven Parent POM [0-9]+\.[0-9]+\.[0-9]+ API' "$TARGET_DIR/index.html" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
if [[ "$RENDERED" != "$VERSION" ]]; then
  echo "Error: index.html renders '${RENDERED:-nothing}' but '$VERSION' was requested." >&2
  exit 1
fi
echo "index.html renders $RENDERED."

echo "Done."
