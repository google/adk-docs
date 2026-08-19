# Kotlin Snippet Validation Tools

This directory contains tools for validating and linting Kotlin code snippets in the `examples/kotlin` directory.

## Tools

### `check_kotlin_snippets.sh`

This script ensures that every `.kt` file within the Kotlin snippets directory is referenced in the `files_to_test.txt` file. This prevents new snippets from being added without being included in the regression test suite.

**Usage:**
```bash
./tools/kotlin-snippets/check_kotlin_snippets.sh
```

### `runner.sh`

This script builds and lints Kotlin snippets using Gradle. It is designed to be run from the project root.

**Usage:**
```bash
# Build snippets
./tools/kotlin-snippets/runner.sh build [file_paths...]

# Lint snippets (enforces Google Style)
./tools/kotlin-snippets/runner.sh lint [file_paths...]
```

If no file paths are provided, it runs the action on the entire `examples/kotlin` project.

## Configuration

### `files_to_test.txt`

This file lists the Kotlin snippet files to be validated. Each line should contain one or more Kotlin file paths relative to the `examples/kotlin/` directory.

### `.editorconfig`

The `examples/kotlin/.editorconfig` file configures `ktlint` to enforce **Google's Kotlin Style Guide**.

## Automated Checks

These tools are automatically run via GitHub Actions on every pull request targeting the `main` branch that modifies Kotlin files.
