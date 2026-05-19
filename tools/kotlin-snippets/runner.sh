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

# This script builds Kotlin snippets. It is designed to be run from the project root.
#
# It can run in two modes:
# 1. Targeted Mode: If file paths are provided as arguments, it runs only those files.
#    This is used in PR checks to test only the changed files.
#    Example: ./tools/kotlin-snippets/runner.sh build examples/kotlin/snippets/get-started/HelloTimeAgent.kt
#
# 2. Full Regression Mode: If no arguments are provided, it builds all Kotlin snippets.
#    Example: ./tools/kotlin-snippets/runner.sh build

# --- Configuration ---
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

EXIT_CODE=0
SNIPPETS_FILE="tools/kotlin-snippets/files_to_test.txt"

# --- Helper Functions ---

should_process_line() {
  local line=$1
  local trimmed_line=$(echo "${line}" | tr -d '[:space:]')
  if [[ -z "${trimmed_line}" || "${trimmed_line}" =~ ^# ]]; then
    return 1
  else
    return 0
  fi
}

find_snippet_line() {
  local file_path_from_root=$1
  local relative_path=${file_path_from_root#examples/kotlin/}
  grep -v '^\s*#' "${SNIPPETS_FILE}" | grep "${relative_path}"
}

execute_and_check() {
  local command=$1
  local display_name=$2

  echo "Executing: ${command}"
  local output
  output=$(eval ${command} 2>&1)
  local exit_code=$?

  if [ ${exit_code} -eq 0 ]; then
    echo -e "[${GREEN}PASS${NC}] ${display_name}"
  else
    echo -e "[${RED}FAIL${NC}] ${display_name}"
    echo "${output}" | sed 's/^/  /'
    EXIT_CODE=1
  fi
}

# --- Main Logic ---

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  if [[ "$1" != "build" && "$1" != "lint" ]]; then
    echo "Usage: $0 <build|lint> [file1 file2 ...]"
    exit 1
  fi

  ACTION=$1
  shift

  # Map action to Gradle task
  GRADLE_TASK="build"
  if [[ "${ACTION}" == "lint" ]]; then
    GRADLE_TASK="ktlintCheck"
  fi

  # Check if file paths were provided as arguments (Targeted Mode).
  if [ "$#" -gt 0 ]; then
    echo "Running targeted Kotlin snippet ${ACTION} for changed files..."
    echo
    for file in "$@"; do
      line=$(find_snippet_line "${file}")
      if [[ -z "${line}" ]]; then
        echo -e "[${RED}FAIL${NC}] ${file}"
        echo "  Error: No corresponding entry found in ${SNIPPETS_FILE}."
        EXIT_CODE=1
        continue
      fi
      
      # For Kotlin, we use Gradle to build/lint the project.
      # Use the wrapper if available.
      GRADLE_CMD="gradle"
      if [[ -f "examples/kotlin/gradlew" ]]; then
        GRADLE_CMD="./gradlew"
      fi
      execute_and_check "(cd examples/kotlin && ${GRADLE_CMD} ${GRADLE_TASK})" "${file}"
      
      if [ ${EXIT_CODE} -ne 0 ]; then
        break
      fi
    done
  else
    echo "Running full Kotlin snippet ${ACTION}..."
    echo
    GRADLE_CMD="gradle"
    if [[ -f "examples/kotlin/gradlew" ]]; then
      GRADLE_CMD="./gradlew"
    fi
    execute_and_check "(cd examples/kotlin && ${GRADLE_CMD} ${GRADLE_TASK})" "Full Gradle ${ACTION}"
  fi

  echo
  echo "Script finished."
  exit ${EXIT_CODE}
fi
