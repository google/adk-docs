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
import subprocess
from datetime import datetime, timedelta

# Configuration
STALENESS_THRESHOLD_DAYS = 90
RECENT_UPDATE_THRESHOLD_WEEKS = 4
DOCS_DIRECTORY = "docs"
REPORT_FILENAME = "docs_health_report.md"
HEALTH_REPORT_START_MARKER = "<!-- BEGIN_DOCS_HEALTH_REPORT -->"
HEALTH_REPORT_END_MARKER = "<!-- END_DOCS_HEALTH_REPORT -->"

def get_last_commit_date(file_path):
    """Gets the last commit date of a file."""
    try:
        commit_date_str = subprocess.check_output(
            ["git", "log", "-1", "--format=%ci", file_path]
        ).decode("utf-8").strip()
        return datetime.strptime(commit_date_str, "%Y-%m-%d %H:%M:%S %z")
    except subprocess.CalledProcessError:
        return None

def check_docs_health():
    """Checks the health of the documentation and generates a detailed report."""
    section_stats = {}
    recently_updated_count = 0
    total_docs_count = 0
    total_stale_files = 0
    now = datetime.now(datetime.now().astimezone().tzinfo)
    staleness_threshold = now - timedelta(days=STALENESS_THRESHOLD_DAYS)
    recent_update_threshold = now - timedelta(weeks=RECENT_UPDATE_THRESHOLD_WEEKS)

    # Change to the adk-docs directory
    original_cwd = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    adk_docs_root = os.path.abspath(os.path.join(script_dir, ".."))
    os.chdir(adk_docs_root)

    for root, _, files in os.walk(DOCS_DIRECTORY):
        for file in files:
            if file.endswith(".md"):
                total_docs_count += 1
                file_path = os.path.join(root, file)
                section = os.path.basename(root) if root != DOCS_DIRECTORY else "Root"
                
                section_stats.setdefault(section, {
                    "total_files": 0,
                    "stale_files": []
                })
                section_stats[section]["total_files"] += 1
                
                last_commit_date = get_last_commit_date(file_path)

                if last_commit_date:
                    if last_commit_date < staleness_threshold:
                        section_stats[section]["stale_files"].append(
                            (file_path, now - last_commit_date)
                        )
                        total_stale_files += 1
                    
                    if last_commit_date > recent_update_threshold:
                        recently_updated_count += 1

    # Revert to original working directory
    os.chdir(original_cwd)

    recent_percentage = (recently_updated_count / total_docs_count * 100) if total_docs_count > 0 else 0
    exit_code = 0 if total_stale_files == 0 else 1

    # --- Generate the new report content ---
    report_parts = [f"{HEALTH_REPORT_START_MARKER}\n"]
    report_parts.append("# Documentation Health Report\n\n")
    report_parts.append(f"**Summary:** **{recent_percentage:.1f}%** of documentation pages were updated in the last "
                       f"{RECENT_UPDATE_THRESHOLD_WEEKS} weeks. ")
    report_parts.append(f"A total of **{total_stale_files}** page(s) are considered stale (older than {STALENESS_THRESHOLD_DAYS} days).\n\n")

    if total_stale_files == 0:
        report_parts.append("**All documentation is up-to-date!**\n")
    else:
        report_parts.append("## Detailed Health by Section\n\n")
        for section, stats in sorted(section_stats.items()):
            stale_count = len(stats["stale_files"])
            if stale_count == 0:
                report_parts.append(f"### {section} - ✅ Healthy\n")
                report_parts.append(f"All {stats['total_files']} page(s) in this section are up-to-date.\n\n")
            else:
                report_parts.append(f"### {section} - ⚠️ Needs Review\n")
                report_parts.append(f"{stale_count} of {stats['total_files']} page(s) in this section are stale:\n\n")
                for file_path, days_since_update in stats["stale_files"]:
                    report_parts.append(f"- **{file_path}**: Last updated {days_since_update.days} days ago\n")
                report_parts.append("\n")
    report_parts.append(HEALTH_REPORT_END_MARKER)

    report_content = "".join(report_parts)

    # --- Read the existing report and replace the health section ---
    report_path = os.path.join(adk_docs_root, REPORT_FILENAME)
    try:
        with open(report_path, "r") as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = ""

    pattern = re.compile(f"{HEALTH_REPORT_START_MARKER}.*{HEALTH_REPORT_END_MARKER}", re.DOTALL)
    
    if pattern.search(existing_content):
        new_full_content = pattern.sub(report_content, existing_content)
    else:
        new_full_content = existing_content + "\n\n" + report_content

    with open(report_path, "w") as f:
        f.write(new_full_content)

    print("Docs Health Analysis done.")
    # (Not used currently) Set outputs for GitHub Actions
    # To be used if SVG badge is to be displayed in README.
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"recent_percentage={recent_percentage:.1f}\n")
            f.write(f"exit_code={exit_code}\n")

    return exit_code

if __name__ == "__main__":
    exit(check_docs_health())
