import asyncio
import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams


async def wait_seconds(seconds: int) -> dict:
    """Pause before the next status check. Use 30 seconds unless told otherwise.

    Args:
        seconds: How long to wait.

    Returns:
        dict confirming the wait.
    """
    seconds = max(1, min(int(seconds), 120))
    await asyncio.sleep(seconds)
    return {"waited_seconds": seconds}


root_agent = Agent(
    model="gemini-flash-latest",
    name="transform_agent",
    instruction=(
        "You parse documents with the Unstructured Transform MCP server. "
        "Pass public https:// file URLs straight to start_transform_job. It "
        "returns a job_id; poll with check_job_status, calling "
        "wait_seconds(30) between checks (jobs take 30 seconds to a few "
        "minutes). When the job completes, call get_job_results and "
        "report the parsed content back to the user. start_transform_job "
        "accepts an optional stages config; it auto-selects a parse "
        "strategy by default, but if the output looks low quality "
        "(garbled text or lost tables), re-run the file with a hi_res "
        "partition strategy for a cleaner result. If the user wants "
        "specific fields rather than the whole document, extract "
        "instead of just parsing. The extraction tools read the element "
        "JSON a parse produces, so parse the file first and keep the "
        "output_ref that get_job_results returns for it. Call "
        "suggest_extraction_schema_for_file with that output_ref when "
        "you need a schema, then start_extraction_job with "
        "element_json_refs set to the output_refs and schema_to_extract "
        "set to a JSON Schema passed as a JSON string. Poll and read an "
        "extraction job with check_job_status and get_job_results like "
        "any other job; its results come back inline, wrapped with the "
        "source filename, so report that filename with each object. If "
        "asked to parse a local file, explain that this requires the "
        "upload helper from the Unstructured ADK guide."
    ),
    tools=[
        wait_seconds,
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.transform.unstructured.io",  # root URL; do not append /mcp
                headers={
                    "Authorization": f"Bearer {os.environ['UNSTRUCTURED_API_KEY']}",
                },
                timeout=30.0,  # ADK's 5s default is too short for a remote handshake
                sse_read_timeout=300.0,
            ),
            tool_filter=[
                "request_file_upload_url",
                "start_transform_job",
                "suggest_extraction_schema_for_file",
                "start_extraction_job",
                "check_job_status",
                "get_job_results",
            ],
        )
    ],
)