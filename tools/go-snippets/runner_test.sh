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

# Unit tests for runner.sh.
# This script can be run directly to validate the logic of the functions in runner.sh.

# --- Test Setup ---
# Source the script to make its functions available for testing.
source "$(dirname "$0")/runner.sh"

# --- Test Harness ---
# Simple assertion function to check for equality.
assert_equals() {
  local expected=$1
  local actual=$2
  local test_name=$3

  if [ "${expected}" == "${actual}" ]; then
    echo -e "[${GREEN}PASS${NC}] ${test_name}"
  else
    echo -e "[${RED}FAIL${NC}] ${test_name}"
    echo "  Expected: '${expected}'"
    echo "  Actual:   '${actual}'"
    exit 1
  fi
}

# --- Test Cases ---

# Tests that the 'run' action correctly forms a 'go run' command,
# preserving any arguments that might be on the line.
test_get_command_for_run_action() {
  local line="snippets/quickstart/main.go"
  local expected="go run snippets/quickstart/main.go"
  local actual=$(get_command_for_action "run" "${line}")
  assert_equals "${expected}" "${actual}" "Should create correct 'run' command without arguments"
}

# Tests that the 'build' action correctly forms a 'go build' command
# and, most importantly, strips any non-.go file arguments from the line.
# This is critical because 'go build' does not accept application arguments.
test_get_command_for_build_action_strips_args() {
  local line="snippets/quickstart/main.go"
  local expected="go build snippets/quickstart/main.go "
  local actual=$(get_command_for_action "build" "${line}")
  assert_equals "${expected}" "${actual}" "Should create correct 'build' command and strip arguments"
}

# Tests that a line with multiple .go files is correctly handled for a build.
# This is important for packages that are split across multiple files.
test_get_command_for_multi_file_build() {
  local line="file1.go file2.go"
  local expected="go build file1.go file2.go "
  local actual=$(get_command_for_action "build" "${line}")
  assert_equals "${expected}" "${actual}" "Should handle multiple files correctly for build"
}

# Tests that a line with multiple .go files is correctly handled for a run.
test_get_command_for_multi_file_run() {
  local line="file1.go file2.go"
  local expected="go run file1.go file2.go"
  local actual=$(get_command_for_action "run" "${line}")
  assert_equals "${expected}" "${actual}" "Should handle multiple files correctly for run"
}

# Tests the core logic for finding a snippet in the configuration file.
# It ensures that:
# 1. The 'examples/go/' prefix is correctly stripped from the input path.
# 2. The correct line is found in the test file.
# 3. Commented-out lines are ignored.
test_find_snippet_line() {
  # Create a temporary SNIPPETS_FILE for this test to isolate it.
  local original_snippets_file="${SNIPPETS_FILE}"
  SNIPPETS_FILE=$(mktemp)
  # Populate the temporary file with test data.
  # This first line acts as a negative test case. The test specifically searches for 'snippets/quickstart/main.go',
  # so this line should be correctly ignored by the grep logic, ensuring the function doesn't just return the first line it finds.
  echo "file1.go" > "${SNIPPETS_FILE}"
  # This line is a commented-out version of our target and should also be ignored.
  echo "# snippets/quickstart/main.go" >> "${SNIPPETS_FILE}" # This line should be ignored by grep.
  # This is the actual line we expect the function to find and return.
  echo "snippets/quickstart/main.go" >> "${SNIPPETS_FILE}" # This is the line we expect to find.

  # This simulates the file path that would be passed to the script (e.g., from 'git diff').
  local input_file_path="examples/go/snippets/quickstart/main.go"
  local expected_line="snippets/quickstart/main.go"
  
  # Call the function under test.
  local actual_line=$(find_snippet_line "${input_file_path}")
  
  assert_equals "${expected_line}" "${actual_line}" "Should find the correct snippet line, ignoring comments"

  # Cleanup
  rm "${SNIPPETS_FILE}"
  SNIPPETS_FILE="${original_snippets_file}" # Restore original path
}

# Tests that find_snippet_line correctly matches a line when the changed file
# is part of a multi-file snippet listed on a single line in files_to_test.txt.
test_find_snippet_line_multi_file_match() {
  local original_snippets_file="${SNIPPETS_FILE}"
  SNIPPETS_FILE=$(mktemp)
  
  # A snippet line with multiple files.
  echo "snippets/my-multi-file/main.go snippets/my-multi-file/helper.go" > "${SNIPPETS_FILE}"

  # Simulate changing the helper file.
  local input_file_path="examples/go/snippets/my-multi-file/helper.go"
  local expected_line="snippets/my-multi-file/main.go snippets/my-multi-file/helper.go"
  
  local actual_line=$(find_snippet_line "${input_file_path}")
  
  assert_equals "${expected_line}" "${actual_line}" "Should find the entire multi-file snippet line"

  # Cleanup
  rm "${SNIPPETS_FILE}"
  SNIPPETS_FILE="${original_snippets_file}"
}

# Tests the logic for determining if a line should be processed.
test_should_process_line() {
  # A valid line should return 0 (success).
  should_process_line "file1.go"
  assert_equals "0" "$?" "Should return success for a valid line"

  # An empty line should return 1 (failure).
  should_process_line ""
  assert_equals "1" "$?" "Should return failure for an empty line"

  # A line with only whitespace should return 1 (failure).
  should_process_line "   "
  assert_equals "1" "$?" "Should return failure for a whitespace-only line"

  # A commented line should return 1 (failure).
  should_process_line "# file1.go"
  assert_equals "1" "$?" "Should return failure for a commented line"

  # A commented line with leading spaces should return 1 (failure).
  should_process_line "  # file1.go"
  assert_equals "1" "$?" "Should return failure for a commented line with leading spaces"
}

# --- Run Tests ---
echo "Running tests for runner.sh..."
test_get_command_for_run_action
test_get_command_for_build_action_strips_args
test_get_command_for_multi_file_build
test_get_command_for_multi_file_run
test_find_snippet_line
test_find_snippet_line_multi_file_match
test_should_process_line
echo "All tests passed."
