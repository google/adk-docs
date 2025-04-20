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

import os


def load_instruction_from_file(
    filename: str, default_instruction: str = "Default instruction."
) -> str:
    """Reads instruction text from a file relative to this script."""
    instruction = default_instruction
    try:
        # Construct path relative to the current script file (__file__)
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, "r", encoding="utf-8") as f:
            instruction = f.read()
        print(f"Successfully loaded instruction from {filename}")
    except FileNotFoundError:
        print(f"WARNING: Instruction file not found: {filepath}. Using default.")
    except Exception as e:
        print(f"ERROR loading instruction file {filepath}: {e}. Using default.")
    return instruction
