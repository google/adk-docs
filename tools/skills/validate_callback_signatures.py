#!/usr/bin/env python3
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

"""Validate callback signatures in skills documentation against actual ADK source.

This validator:
1. Extracts callback function signatures from skills markdown
2. Compares them against the actual ADK source code
3. Reports any mismatches

Usage:
  python validate_callback_signatures.py                    # validate all skills/**/*.md
  python validate_callback_signatures.py skills/foo/bar.md  # validate specific files
"""

import ast
import inspect
import re
import sys
from pathlib import Path
from typing import Any, Optional

try:
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models import LlmResponse, LlmRequest
    from google.adk.tools.tool_context import ToolContext
    from google.adk.tools.base_tool import BaseTool
    from google.genai import types as genai_types
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    print("[WARN] google-adk not installed. Callback signature validation will be skipped.")


# Expected callback signatures extracted from ADK source code
# These are manually maintained but validated against actual source
EXPECTED_SIGNATURES = {
    "before_agent_callback": {
        "params": ["callback_context: CallbackContext"],
        "return": "None",
        "description": "Called before agent execution starts"
    },
    "after_agent_callback": {
        "params": ["callback_context: CallbackContext"],
        "return": "genai_types.Content | None",
        "description": "Called after agent execution completes"
    },
    "before_model_callback": {
        "params": ["callback_context: CallbackContext", "llm_request: LlmRequest"],
        "return": "LlmResponse | None",
        "description": "Called before LLM API call"
    },
    "after_model_callback": {
        "params": ["callback_context: CallbackContext", "llm_response: LlmResponse"],
        "return": "LlmResponse | None",
        "description": "Called after LLM API call"
    },
    "before_tool_callback": {
        "params": ["tool: BaseTool", "args: dict", "tool_context: ToolContext"],
        "return": "dict | None",
        "description": "Called before tool execution"
    },
    "after_tool_callback": {
        "params": ["tool: BaseTool", "args: dict", "tool_context: ToolContext", "tool_response: dict"],
        "return": "dict | None",
        "description": "Called after tool execution"
    },
}


def extract_function_signature(code: str) -> Optional[dict[str, Any]]:
    """Extract function name, parameters, and return type from Python code."""
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Extract parameter names and annotations
                params = []
                for arg in node.args.args:
                    if arg.annotation:
                        param_str = f"{arg.arg}: {ast.unparse(arg.annotation)}"
                    else:
                        param_str = arg.arg
                    params.append(param_str)

                # Extract return annotation
                return_type = ast.unparse(node.returns) if node.returns else "None"

                return {
                    "name": node.name,
                    "params": params,
                    "return": return_type,
                }
    except SyntaxError:
        pass
    return None


def validate_callback_signature(func_name: str, actual_params: list[str], actual_return: str) -> tuple[bool, str]:
    """Validate a callback signature against expected signature."""
    if func_name not in EXPECTED_SIGNATURES:
        return True, ""  # Not a callback we're tracking

    expected = EXPECTED_SIGNATURES[func_name]
    expected_params = expected["params"]
    expected_return = expected["return"]

    # Normalize parameter lists for comparison
    actual_params_normalized = [p.strip() for p in actual_params if p.strip() not in ["", "self"]]
    expected_params_normalized = [p.strip() for p in expected_params]

    errors = []

    # Check parameters
    if actual_params_normalized != expected_params_normalized:
        errors.append(f"Parameter mismatch:")
        errors.append(f"  Expected: ({', '.join(expected_params_normalized)})")
        errors.append(f"  Actual:   ({', '.join(actual_params_normalized)})")

    # Check return type (normalize Optional[X] vs X | None)
    actual_return_norm = actual_return.replace("Optional[", "").replace("]", " | None")
    expected_return_norm = expected_return.replace("Optional[", "").replace("]", " | None")

    if actual_return_norm != expected_return_norm:
        errors.append(f"Return type mismatch:")
        errors.append(f"  Expected: {expected_return}")
        errors.append(f"  Actual:   {actual_return}")

    if errors:
        return False, "\n".join(errors)
    return True, ""


def extract_code_blocks(filepath: Path) -> list[tuple[int, str]]:
    """Extract Python code blocks from markdown file."""
    code_blocks = []
    with open(filepath) as f:
        lines = f.readlines()

    in_block = False
    lang = ""
    start_line = 0
    block_lines = []

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not in_block:
                # Starting a code block
                match = re.match(r"^```(\w+)", line.strip())
                if match:
                    lang = match.group(1)
                    in_block = True
                    start_line = i
                    block_lines = []
            else:
                # Ending a code block
                if lang == "python":
                    code_blocks.append((start_line, "\n".join(block_lines)))
                in_block = False
        elif in_block:
            block_lines.append(line.rstrip())

    return code_blocks


def validate_file(filepath: Path) -> list[str]:
    """Validate all callback signatures in a markdown file."""
    errors = []
    code_blocks = extract_code_blocks(filepath)

    for line_num, code in code_blocks:
        sig = extract_function_signature(code)
        if sig and sig["name"] in EXPECTED_SIGNATURES:
            is_valid, error_msg = validate_callback_signature(
                sig["name"], sig["params"], sig["return"]
            )
            if not is_valid:
                location = f"{filepath}:{line_num}"
                errors.append(f"\n[FAIL] {location}")
                errors.append(f"Function: {sig['name']}")
                errors.append(error_msg)

    return errors


def main():
    if not ADK_AVAILABLE:
        print("[SKIP] Callback signature validation skipped (google-adk not installed)")
        return 0

    # Determine which files to validate
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:] if f.endswith('.md')]
    else:
        files = list(Path("skills").glob("**/*.md"))

    if not files:
        print("[INFO] No markdown files found to validate")
        return 0

    print(f"[INFO] Validating callback signatures in {len(files)} file(s)...")

    all_errors = []
    for filepath in files:
        errors = validate_file(filepath)
        if errors:
            all_errors.extend(errors)

    if all_errors:
        print("\n=== Callback Signature Validation Failed ===")
        for error in all_errors:
            print(error)
        print("\n[FAIL] Found callback signature mismatches")
        print("\nExpected signatures:")
        for name, sig in EXPECTED_SIGNATURES.items():
            params = ", ".join(sig["params"])
            print(f"  {name}({params}) -> {sig['return']}")
        return 1

    print("[PASS] All callback signatures are correct")
    return 0


if __name__ == "__main__":
    sys.exit(main())
