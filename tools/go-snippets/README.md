# Go Snippets Tooling

This directory contains the scripts and configuration for building, running, and testing the Go snippets located in `examples/go/`.

## Overview

The tooling is designed to ensure that all Go snippets are continuously validated and to provide a fast feedback loop for developers. It consists of a unified runner script, a configuration file to manage the list of snippets, and a suite of unit tests for the runner itself.

## Key Components

- **`runner.sh`**: The main script for building and running Go snippets.
- **`files_to_test.txt`**: The configuration file that lists all Go snippets to be tested.
- **`check_go_snippets.sh`**: A PR check script that ensures all `.go` files are registered in `files_to_test.txt`.
- **`runner_test.sh`**: Unit tests for the `runner.sh` script.

---

## Understanding the Test Runner

The `runner.sh` script is the core of this tooling. It is crucial to understand how it identifies which snippets to build, especially when making changes.

*   **Strict Adherence to `files_to_test.txt`:** The runner strictly relies on the `files_to_test.txt` configuration file. When a file is changed in a Pull Request, the runner looks for that file's path (relative to `examples/go/`) as a **substring** within any line of `files_to_test.txt`. If the file is not found (e.g., you added a new file but forgot to register it, or it is an ignored file type), the runner will not trigger a build for that specific change.
*   **Multi-file `package main`:** If a snippet is a `package main` (an executable application) that is split across multiple `.go` source files in the same directory (e.g., `main.go` and `helper.go`), **all of these files must be listed on the same line** in `files_to_test.txt`.
    *   **Correct:** `snippets/mytask/main.go snippets/mytask/helper.go`
    *   **Incorrect:** Listing them on separate lines or omitting the helper. This will cause the `go build` command to fail with "undefined symbol" errors because the compiler won't see the helper file.
*   **Test Files (`_test.go`):** Files ending in `_test.go` are explicitly excluded from `files_to_test.txt` and are ignored by the runner. Consequently, changing a `_test.go` file will **not** automatically trigger a build of the main snippet in that directory. The `go build` command used by the runner ignores test files.

## How to Use

### Automatic Execution (CI/CD)

The scripts are primarily designed to be run automatically by GitHub Actions.

- **On Pull Requests:** When a pull request is opened, two workflows are triggered:
    1.  **Go Snippets Build on PR and Schedule:** This workflow runs `check_go_snippets.sh` to ensure new files are registered. It then intelligently builds **only the `.go` files that were changed** in the PR.
    2.  **Go Build and Test on PR:** This workflow runs a full build of **all** Go snippets and executes any unit tests (`go test ./...`) to ensure that a change has not broken any other part of the Go codebase.

- **Scheduled Runs:** A full regression build of all Go snippets is run automatically every Sunday at 3:00 AM UTC to catch any potential issues.

### Manual Execution

You can also run the scripts locally to test your changes before pushing. All commands should be run from the **root of the repository**.

#### Building All Snippets

To run a full build of every Go snippet listed in `files_to_test.txt`:

```bash
./tools/go-snippets/runner.sh build
```

#### Building Specific Snippets

To build one or more specific Go snippets (for example, if you are working on them and want a quick check):

```bash
./tools/go-snippets/runner.sh build examples/go/snippets/quickstart/main.go
```

#### Running the Unit Tests

To run the unit tests for the `runner.sh` script itself:

```bash
./tools/go-snippets/runner_test.sh
```

---

## Maintaining the Snippet List

### Adding a New Snippet

1.  Create your new `.go` file (e.g., `examples/go/snippets/my-new-snippet/main.go`).
2.  Open `tools/go-snippets/files_to_test.txt`.
3.  Add a new line with the path to your file, relative to the `examples/go/` directory.

    ```
    # In files_to_test.txt
    snippets/my-new-snippet/main.go
    ```

4.  If your snippet is part of a package that requires multiple files to be built together, add them all to the same line:

    ```
    # In files_to_test.txt
    snippets/my-multi-file-snippet/main.go snippets/my-multi-file-snippet/helpers.go
    ```

The `check_go_snippets.sh` script will automatically run on your PR and remind you if you've forgotten to add your new file to the list.
