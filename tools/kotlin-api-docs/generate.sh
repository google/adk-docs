#!/usr/bin/env bash
#
# Generates Kotlin API reference documentation for adk-kotlin using Dokka.
# Outputs HTML to docs/api-reference/kotlin/.
#
# This script runs in an isolated temporary directory and does not
# modify any existing adk-kotlin clones or local environments.
#
# Prerequisites: java (JDK 17+), ANDROID_HOME, git, gradle
# Run from: adk-docs repository root
#
# Usage: bash tools/kotlin-api-docs/generate.sh <version>
# Example: bash tools/kotlin-api-docs/generate.sh 0.1.0

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

if ! command -v gradle &> /dev/null; then
  echo "Error: gradle is required but not installed."
  echo "  Install with: brew install gradle"
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

# Workaround: Remove Bazel BUILD file if present. On macOS (case-insensitive
# filesystem), this file conflicts with Gradle's build/ output directory.
if [[ -f "BUILD" ]]; then
  echo "Removing Bazel BUILD file (macOS case-insensitive filesystem workaround)..."
  rm -f BUILD
fi

# Workaround: Regenerate Gradle wrapper if the checked-in gradlew script
# references a non-standard classpath
if grep -q "wrapper_files" gradlew 2>/dev/null; then
  GRADLE_VERSION=$(grep distributionUrl gradle/wrapper/gradle-wrapper.properties \
    | sed 's|.*gradle-\(.*\)-bin.zip|\1|')
  echo "Fixing non-standard Gradle wrapper (regenerating for Gradle ${GRADLE_VERSION})..."
  gradle wrapper --gradle-version "$GRADLE_VERSION"
fi

# Build Dokka HTML docs (multi-module generates a unified site with module index)
echo "Building Kotlin API docs with Dokka..."
./gradlew clean dokkaHtmlMultiModule

popd > /dev/null || exit 1

# Copy to output directory
echo "Copying to $TARGET_DIR..."
rm -rf "$TARGET_DIR"/*
cp -r "$WORK_DIR/adk-kotlin/build/dokka/htmlMultiModule"/* "$TARGET_DIR/"

echo "Done."
