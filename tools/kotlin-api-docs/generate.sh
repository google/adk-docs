#!/usr/bin/env bash
#
# Generates Kotlin API reference documentation for adk-kotlin using Dokka.
# Outputs HTML to docs/api-reference/kotlin/.
#
# This script runs in an isolated temporary directory and does not
# modify any existing adk-kotlin clones or local environments.
#
# Prerequisites: java (JDK 17+), Android SDK (ANDROID_HOME must be set), git
# Run from: adk-docs repository root
#
# Usage: bash tools/kotlin-api-docs/generate.sh <version>
# Example: bash tools/kotlin-api-docs/generate.sh 0.1.0
#
# Dokka 2 note: adk-kotlin moved from Dokka 1.9.20 to 2.2.0 at v0.7.0. Dokka 2
# renamed the generation task and dropped the implicit root aggregation that
# used to produce the unified multi-module site, so this script pins neither.
# See AGGREGATED_MODULES below.

set -e

# Validate arguments
VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 0.1.0"
  exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Version must be in X.Y.Z format (e.g., 0.1.0)"
  exit 1
fi

# Check prerequisites
if ! command -v java &> /dev/null; then
  echo "Error: java is required but not installed."
  echo "  Install with: brew install openjdk@17"
  echo "  Then run: sudo ln -sfn \$(brew --prefix openjdk@17)/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk"
  exit 1
fi

if ! command -v git &> /dev/null; then
  echo "Error: git is required but not installed."
  exit 1
fi

if [[ -z "$ANDROID_HOME" ]]; then
  echo "Error: ANDROID_HOME is not set."
  echo "  Install with: brew install --cask android-commandlinetools"
  echo "  Then run:"
  echo "    export ANDROID_HOME=\"\$(brew --prefix)/share/android-commandlinetools\""
  echo "    yes | sdkmanager --licenses"
  echo "    sdkmanager \"platforms;android-34\""
  echo "  Add to ~/.zshrc: export ANDROID_HOME=\"\$(brew --prefix)/share/android-commandlinetools\""
  exit 1
fi

if [[ ! -d "$ANDROID_HOME" ]]; then
  echo "Error: ANDROID_HOME is set to '$ANDROID_HOME' but that directory does not exist."
  exit 1
fi

# Validate working directory
TARGET_DIR="docs/api-reference/kotlin"
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

# Clone adk-kotlin
echo "Cloning adk-kotlin v${VERSION}..."
git clone --depth 1 --branch "v${VERSION}" https://github.com/google/adk-kotlin adk-kotlin
cd adk-kotlin

# Dokka 2 builds the unified site from an explicit aggregation list on the root
# project; Dokka 1's `dokkaHtmlMultiModule` used to infer it from the subprojects.
# Injecting it into the throwaway clone keeps the whole fix inside adk-docs and
# needs no change to adk-kotlin.
#
# Deliberately excluded:
#   -examples, -examples-android, -examples-java  sample apps, not API surface.
#                                                 -examples also declares a JDK 21
#                                                 toolchain, which fails to
#                                                 auto-provision and stops the build.
#   -firebase, -mlkit                             Android-only library modules. Both
#                                                 are aggregatable and both emit an
#                                                 empty directory -- Dokka 2 produces
#                                                 no pages for their androidMain
#                                                 source sets here. Listing them
#                                                 would imply coverage that does not
#                                                 exist; documenting them needs an
#                                                 adk-kotlin-side Dokka source-set fix.
echo "Injecting Dokka aggregation for the published modules..."
cat >> build.gradle.kts <<'AGGREGATED_MODULES'

// --- injected by adk-docs tools/kotlin-api-docs/generate.sh ---
dependencies {
  dokka(project(":google-adk-kotlin-core"))
  dokka(project(":google-adk-kotlin-a2a"))
  dokka(project(":google-adk-kotlin-integrations"))
  dokka(project(":google-adk-kotlin-litertlm"))
  dokka(project(":google-adk-kotlin-processor"))
  dokka(project(":google-adk-kotlin-webserver"))
  dokka(project(":google-adk-kotlin-testing"))
}
AGGREGATED_MODULES

# Build Dokka HTML docs. The leading colon scopes this to the root project's
# aggregated publication -- without it Gradle runs the task in every subproject,
# including the excluded sample apps.
echo "Building Kotlin API docs with Dokka..."
./gradlew clean :dokkaGeneratePublicationHtml

popd > /dev/null || exit 1

# Copy to output directory
echo "Copying to $TARGET_DIR..."
rm -rf "$TARGET_DIR"/*
cp -r "$WORK_DIR/adk-kotlin/build/dokka/html"/* "$TARGET_DIR/"

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

# The reference sat at 0.5.0 for four releases because nothing ever checked that
# the committed output matched the version it was generated for. Fail loudly
# rather than leave a stale site that looks freshly built.
echo "Verifying rendered version..."
RENDERED=$(grep -A1 'class="library-version"' "$TARGET_DIR/index.html" | tr -d ' \t\r\n' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
if [[ "$RENDERED" != "$VERSION" ]]; then
  echo "Error: index.html renders '${RENDERED:-nothing}' but '$VERSION' was requested."
  exit 1
fi
echo "index.html renders $RENDERED."

echo "Done."
