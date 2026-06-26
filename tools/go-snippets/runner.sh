#!/bin/bash
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

# This script builds and runs Go snippets. It is designed to be run from the project root.
#
# It can run in two modes:
# 1. Targeted Mode: If file paths are provided as arguments, it runs only those files.
#    This is used in PR checks to test only the changed files.
#    Example: ./tools/go-snippets/runner.sh build examples/go/snippets/quickstart/main.go
#
# 2. Full Regression Mode: If no arguments are provided, it runs a predefined
#    list of all Go snippets in the repository. This is used for scheduled weekly tests.
#    Example: ./tools/go-snippets/runner.sh build

# --- Configuration ---
# Define color codes for colored output.
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Global exit code for the script. It is set to 1 if any test fails.
EXIT_CODE=0

# The configuration file that lists all Go snippets to be tested.
SNIPPETS_FILE="tools/go-snippets/files_to_test.txt"

# --- Helper Functions ---

# should_process_line determines if a line from the snippets file should be processed.
# It returns 0 (success) for valid lines and 1 (failure) for comments or empty lines.
#
# @param {string} line - The line to check.
# @returns {int} 0 if the line should be processed, 1 otherwise.
should_process_line() {
  local line=$1
  # Remove all whitespace from the line to correctly handle lines with only spaces or tabs.
  local trimmed_line=$(echo "${line}" | tr -d '[:space:]')
  # Return failure (1) if the trimmed line is empty or starts with a hash.
  if [[ -z "${trimmed_line}" || "${trimmed_line}" =~ ^# ]]; then
    return 1
  else
    return 0
  fi
}

# find_snippet_line searches the SNIPPETS_FILE for a given Go file path.
# It returns any line from the snippets file that contains the relative path of the changed Go file
# as a substring.
#
# For `package main` snippets split across multiple files, all source files must be listed on the
# same line in `files_to_test.txt` for `go build` to succeed (e.g., `main.go helper.go`).
#
# @param {string} file_path_from_root - The full path to the Go file relative to the project root (e.g., "examples/go/snippets/quickstart/main.go").
# @returns {string} The matching line from SNIPPETS_FILE, or an empty string if not found.
find_snippet_line() {
  local file_path_from_root=$1
  # The SNIPPETS_FILE contains paths relative to 'examples/go/', so we strip that prefix from the input path.
  local relative_path=${file_path_from_root#examples/go/}
  # First, filter out all commented lines, then search for the relative path.
  grep -v '^\s*#' "${SNIPPETS_FILE}" | grep "${relative_path}"
}

# get_command_for_action constructs the appropriate Go command based on the action.
# It specifically handles stripping arguments for the 'build' action.
#
# @param {string} action - The action to perform ("build" or "run").
# @param {string} line - The line from the snippets file, which may include arguments.
# @returns {string} The fully formed Go command.
get_command_for_action() {
  local action=$1
  local line=$2
  local command=""

  if [ "${action}" == "build" ]; then
    # For 'build', extract only the file paths, ignoring any arguments.
    # 'go build' does not accept application arguments, so they must be stripped.
    local files_to_build=$(echo "${line}" | awk '{for(i=1;i<=NF;i++) if($i ~ /\.go$/) printf "%s ", $i}')
    command="go build ${files_to_build}"
  elif [ "${action}" == "run" ]; then
    # For 'run', use the line as is, as 'go run' will pass arguments to the application.
    command="go run ${line}"
  fi
  echo "${command}"
}

# execute_and_check executes a command and prints a formatted status message.
#
# @param {string} command - The full command to execute.
# @param {string} display_name - A user-friendly name for the command/file.
execute_and_check() {
  local command=$1
  local display_name=$2

  # Log the exact command being executed for debugging and transparency.
  echo "Executing: ${command}"

  # 'eval' is used to correctly execute the command string, which may contain quotes and other special characters.
  local output
  output=$(eval ${command} 2>&1)
  local exit_code=$?

  if [ ${exit_code} -eq 0 ]; then
    echo -e "[${GREEN}PASS${NC}] ${display_name}"
  else
    echo -e "[${RED}FAIL${NC}] ${display_name}"
    # Indent the error output for better readability.
    echo "${output}" | sed 's/^/  /'
    # Set the global exit code to indicate failure.
    EXIT_CODE=1
  fi
}

# --- Main Logic ---

# This check prevents the main logic from running if the script is being sourced (e.g., by the test script).
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  # Validate the first argument is either 'build' or 'run'.
  if [[ "$1" != "build" && "$1" != "run" ]]; then
    echo "Usage: $0 <build|run> [file1 file2 ...]"
    exit 1
  fi

  ACTION=$1
  shift # Remove the first argument, so '$@' contains only the file paths.

  # Update to the latest version of the ADK.
  # This ensures that we are always testing against the most recent release.
  execute_and_check "(cd examples/go && go get google.golang.org/adk@latest)" "Updating google.golang.org/adk to latest"
  if [ ${EXIT_CODE} -ne 0 ]; then
    exit ${EXIT_CODE} # Exit immediately if go get failed.
  fi

  # Ensure all Go module dependencies are tidy before running any builds or tests.
  # This is run from the 'examples/go' directory where the go.mod file is located.
  (cd examples/go && go mod tidy)
  if [ $? -ne 0 ]; then
    echo -e "[${RED}FAIL${NC}] go mod tidy failed in examples/go"
    exit 1 # Exit immediately if dependencies are not clean.
  fi

  # Check if file paths were provided as arguments (Targeted Mode).
  if [ "$#" -gt 0 ]; then
    echo "Running targeted Go snippet ${ACTION} for changed files..."
    echo
    for file in "$@"; do
      # Find the corresponding line in the snippets file for the changed file.
      line=$(find_snippet_line "${file}")
      if [[ -z "${line}" ]]; then
        echo -e "[${RED}FAIL${NC}] ${file}"
        echo "  Error: No corresponding entry found in ${SNIPPETS_FILE}."
        EXIT_CODE=1
        continue # Skip to the next file.
      fi
      
      # Construct the appropriate build or run command.
      command_to_execute=$(get_command_for_action "${ACTION}" "${line}")
      if [[ -n "${command_to_execute}" ]]; then
        # Execute the command from the 'examples/go' directory.
        execute_and_check "(cd examples/go && ${command_to_execute})" "${file}"
      fi
    done
  else
    # If no file paths were provided, run in Full Regression Mode.
    echo "Running full Go snippet ${ACTION}..."
    echo
    # Read the snippets file line by line.
    while IFS= read -r line; do
      # Skip empty lines and comments.
      if ! should_process_line "${line}"; then
        continue
      fi
      
      command_to_execute=$(get_command_for_action "${ACTION}" "${line}")
      if [[ -n "${command_to_execute}" ]]; then
        execute_and_check "(cd examples/go && ${command_to_execute})" "${line}"
      fi
    done < "${SNIPPETS_FILE}"
  fi

  echo
  echo "Script finished."
  # Exit with the final status code (0 for success, 1 for failure).
  exit ${EXIT_CODE}
fi
