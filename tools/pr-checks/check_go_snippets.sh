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

# This script ensures that every .go file within the Go snippets directory
# is referenced in the runner.sh script. This prevents new snippets
# from being added without being included in the regression test suite.

# --- Configuration ---
RED='\033[0;31m'
NC='\033[0m' # No Color
EXIT_CODE=0
RUNNER_SCRIPT="tools/go-snippets/runner.sh"

# --- Logic ---
echo "Checking for Go files that are not registered in the runner script..."

# Find all .go files in the snippets directory, excluding _test.go files.
all_go_files=$(find examples/go/snippets -type f -name "*.go" ! -name "*_test.go" | sort)

# Extract all .go file paths from the ALL_FILES array in the runner script.
referenced_files=$(sed -n '/ALL_FILES=/,/)/p' ${RUNNER_SCRIPT} | grep -o '[a-zA-Z0-9/._-]*\.go' | sort | uniq)

# Compare the list of all .go files with the list of referenced files.
# The 'comm' command is used to find lines that are unique to the first file (all_go_files).
unreferenced_files=$(comm -23 <(echo "${all_go_files}") <(echo "${referenced_files}"))

if [[ -n "${unreferenced_files}" ]]; then
  echo -e "${RED}Error: The following Go files were found but are not referenced in ${RUNNER_SCRIPT}:${NC}"
  # Indent the list of files for readability.
  echo "${unreferenced_files}" | sed 's/^/  /'
  echo
  echo "Please add them to the ALL_FILES array in ${RUNNER_SCRIPT} to include them in the regression tests."
  EXIT_CODE=1
else
  echo "All Go files are correctly referenced in the runner script."
fi

exit ${EXIT_CODE}