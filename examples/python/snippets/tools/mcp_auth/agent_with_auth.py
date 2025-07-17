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

# --8<-- [start:init]

import asyncio
import os

from google.adk.agents import LlmAgent
from google.adk.auth import AuthCredential, AuthCredentialTypes, HttpAuth, HttpCredentials
from google.adk.auth.auth_schemes import HTTPBearer
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHTTPConnectionParams,
)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --- Authentication Configuration ---
# In a real application, load the token from an environment variable or secret manager.
# e.g., MY_MCP_API_TOKEN = os.environ.get("MY_MCP_API_TOKEN")
MY_MCP_API_TOKEN = "secret-token-123"  # This must match the mock server's token

# Define the authentication scheme: HTTP Bearer token.
auth_scheme = HTTPBearer()

# Define the credential containing the actual token.
auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.HTTP,
    http=HttpAuth(
        scheme="bearer", credentials=HttpCredentials(token=MY_MCP_API_TOKEN)
    ),
)
# --- End Authentication Configuration ---

# --- MCP Toolset Configuration ---
mcp_toolset = MCPToolset(
    # Use StreamableHTTPConnectionParams for remote HTTP servers.
    connection_params=StreamableHTTPConnectionParams(
        url="http://127.0.0.1:8001/mcp",
    ),
    # Provide the authentication scheme and credential to the toolset.
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
)
# --- End MCP Toolset Configuration ---

# --- Agent Definition ---
root_agent = LlmAgent(
    model="gemini-1.5-flash",
    name="profile_assistant_agent",
    instruction="You can access user profiles through a secure MCP tool.",
    tools=[mcp_toolset],
)
# --- End Agent Definition ---

# --- Main Execution Logic ---
async def main():
    """Runs the agent to test the authenticated MCP tool call."""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="mcp_auth_app", user_id="test_user"
    )

    query = "What is the profile for user 42?"
    print(f"User Query: '{query}'")
    content = types.Content(role="user", parts=[types.Part(text=query)])

    runner = Runner(agent=root_agent, session_service=session_service)

    print("Running agent...")
    events_async = runner.run_async(
        session_id=session.id, user_id=session.user_id, new_message=content
    )

    async for event in events_async:
        print(f"Event received: {event}")

    # Clean up the MCP connection when done.
    await mcp_toolset.close()
    print("Cleanup complete.")

if __name__ == "__main__":
    # Set GOOGLE_API_KEY environment variable if not already set
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set.")
    else:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"An error occurred: {e}")

# --8<-- [end:init]