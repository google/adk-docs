#!/bin/bash
# Copyright 2026 Google LLC
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

# This script ensures that every .kt file within the Kotlin snippets directory
# is referenced in the files_to_test.txt file. This prevents new snippets
# from being added without being included in the regression test suite.

# --- Configuration ---
RED='\033[0;31m'
NC='\033[0m' # No Color
EXIT_CODE=0
SNIPPETS_FILE="tools/kotlin-snippets/files_to_test.txt"

# --- Logic ---
echo "Checking for Kotlin files that are not registered in ${SNIPPETS_FILE}..."

# Find all .kt files in the snippets directory, excluding test files if any.
all_kotlin_files=$(find examples/kotlin -type f -name "*.kt" ! -name "*Test.kt" | sed 's|examples/kotlin/||' | sort)

# Extract all .kt file paths from the snippets file, ignoring comments.
referenced_files=$(grep -v '^\s*#' "${SNIPPETS_FILE}" | grep -o '[a-zA-Z0-9/._-]*\.kt' | sort | uniq)

# Compare the list of all .kt files with the list of referenced files.
unreferenced_files=$(comm -23 <(echo "${all_kotlin_files}") <(echo "${referenced_files}"))

if [[ -n "${unreferenced_files}" ]]; then
  echo -e "${RED}Error: The following Kotlin files were found but are not referenced in ${SNIPPETS_FILE}:${NC}"
  # Indent the list of files for readability.
  echo "${unreferenced_files}" | sed 's/^/  /'
  echo
  echo "Please add them to ${SNIPPETS_FILE} to include them in the regression tests."
  EXIT_CODE=1
else
  echo "All Kotlin files are correctly referenced in the snippets file."
fi

# Check for files in the list that don't exist on disk
dangling_references=$(comm -23 <(echo "${referenced_files}") <(echo "${all_kotlin_files}"))

if [[ -n "${dangling_references}" ]]; then
  echo -e "${RED}Error: The following files are referenced in ${SNIPPETS_FILE} but do not exist:${NC}"
  echo "${dangling_references}" | sed 's/^/  /'
  echo
  echo "Please remove them from ${SNIPPETS_FILE}."
  EXIT_CODE=1
fi

exit ${EXIT_CODE}
