#  Copyright 2025 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import re
from collections import defaultdict

DOCS_DIRECTORY = "docs"
REPORT_FILENAME = "docs_health_report.md"
VERSION_REPORT_START_MARKER = "<!-- BEGIN_VERSION_REPORT -->"
VERSION_REPORT_END_MARKER = "<!-- END_VERSION_REPORT -->"

def generate_version_report():
    version_map = defaultdict(list)
    files_without_version = []

    for root, _, files in os.walk(DOCS_DIRECTORY):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    content = f.read()
                    if content.startswith("---"):
                        front_matter = content.split("---")[1]
                        match = re.search(r"version:\s*(.*)", front_matter)
                        if match:
                            version = match.group(1).strip()
                            version_map[version].append(filepath)
                        else:
                            files_without_version.append(filepath)
                    else:
                        files_without_version.append(filepath)

    # --- Generate the new report content ---
    report_parts = [f"{VERSION_REPORT_START_MARKER}\n"]
    report_parts.append("# Documentation Version Report\n\n")
    report_parts.append("This report provides a summary of the versions of the documentation pages.\n\n")

    for version, files in sorted(version_map.items()):
        report_parts.append(f"## Version {version}\n\n")
        report_parts.append(f"Found {len(files)} pages with this version:\n\n")
        for file in files:
            link = os.path.relpath(file, "docs").replace(".md", ".html")
            report_parts.append(f"- [{file}]({link})\n")
        report_parts.append("\n")

    if files_without_version:
        report_parts.append("## Pages without Version Information\n\n")
        report_parts.append(f"Found {len(files_without_version)} pages without version metadata:\n\n")
        for file in files_without_version:
            link = os.path.relpath(file, "docs").replace(".md", ".html")
            report_parts.append(f"- [{file}]({link})\n")
        report_parts.append("\n")
    report_parts.append(VERSION_REPORT_END_MARKER)
    
    report_content = "".join(report_parts)

    # --- Read the existing report and replace the version section ---
    try:
        with open(REPORT_FILENAME, "r") as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = ""

    # Use a regex to replace the content between the markers, or append if not found
    # The re.DOTALL flag allows "." to match newlines
    pattern = re.compile(f"{VERSION_REPORT_START_MARKER}.*{VERSION_REPORT_END_MARKER}", re.DOTALL)
    
    if pattern.search(existing_content):
        new_full_content = pattern.sub(report_content, existing_content)
    else:
        # If the markers aren't found, append the new report with a newline
        new_full_content = existing_content + "\n\n" + report_content

    print(f"\nWriting version report to: {REPORT_FILENAME}")
    with open(REPORT_FILENAME, "w") as f:
        f.write(new_full_content)

    print(f"\nVersion report analysis done.")

if __name__ == "__main__":
    generate_version_report()
