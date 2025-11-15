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
#    Example: ./tools/go-snippets/runner.sh run

# --- Configuration ---
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
EXIT_CODE=0
SNIPPETS_FILE="tools/go-snippets/files_to_test.txt"

# --- Helper Function ---
# execute_and_check executes a command, captures the output,
# and prints a formatted, colored status message.
#
# @param {string} command - The full command to execute.
# @param {string} display_name - A user-friendly name for the command/file.
execute_and_check() {
  local command=$1
  local display_name=$2

  # Capture the run output and exit code.
  local output
  output=$(eval ${command} 2>&1)
  local exit_code=$?

  if [ ${exit_code} -eq 0 ]; then
    # Print PASS status in green if run is successful.
    echo -e "[${GREEN}PASS${NC}] ${display_name}"
  else
    # Print FAIL status in red and the indented error message.
    echo -e "[${RED}FAIL${NC}] ${display_name}"
    echo "${output}" | sed 's/^/  /'
    # Set the script's exit code to 1 to fail the CI check.
    EXIT_CODE=1
  fi
}

# --- Main Logic ---

if [[ "$1" != "build" && "$1" != "run" ]]; then
  echo "Usage: $0 <build|run> [file1 file2 ...]"
  exit 1
fi

ACTION=$1
shift

# Run go mod tidy once for the entire examples/go module
(cd examples/go && go mod tidy)
if [ $? -ne 0 ]; then
  echo -e "[${RED}FAIL${NC}] go mod tidy failed in examples/go"
  EXIT_CODE=1
fi

if [ "$#" -gt 0 ]; then
  echo "Running targeted Go snippet ${ACTION} for changed files..."
  echo
  for file in "$@"; do
    # Find the line in snippets.txt that contains the changed file
    line=$(grep "${file#examples/go/}" ${SNIPPETS_FILE})
    if [ "${ACTION}" == "build" ]; then
      command_to_execute="go build ${line}"
    elif [ "${ACTION}" == "run" ]; then
      command_to_execute="go run ${line}"
    fi
    
    if [[ -n "${command_to_execute}" ]]; then
      execute_and_check "(cd examples/go && ${command_to_execute})" "${file}"
    fi
  done
else
  echo "Running full Go snippet ${ACTION}..."
  echo
  while IFS= read -r line; do
    command_to_execute=""
    if [ "${ACTION}" == "build" ]; then
      command_to_execute="go build ${line}"
    elif [ "${ACTION}" == "run" ]; then
      command_to_execute="go run ${line}"
    fi
    
    if [[ -n "${command_to_execute}" ]]; then
      execute_and_check "(cd examples/go && ${command_to_execute})" "${line}"
    fi
  done < "${SNIPPETS_FILE}"
fi

echo
echo "Script finished."
exit ${EXIT_CODE}