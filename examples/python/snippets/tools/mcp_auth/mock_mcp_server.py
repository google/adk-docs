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

import json
from typing import Annotated, Any, Dict, List

from fastapi import FastAPI, Header, HTTPException, Request
import uvicorn

app = FastAPI(
    title="Mock Authenticated MCP Server",
    description="A simple server to simulate an MCP endpoint requiring Bearer token auth.",
)

EXPECTED_TOKEN = "secret-token-123"

async def check_auth(authorization: Annotated[str | None, Header()] = None):
    """Dependency to check for a valid Bearer token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer" or token != EXPECTED_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Main MCP endpoint that handles list_tools and call_tool methods."""
    await check_auth(request.headers.get("authorization"))

    body = await request.json()
    method = body.get("method")

    if method == "list_tools":
        return {
            "tools": [
                {
                    "name": "get_user_profile",
                    "description": "Gets the profile for a given user ID.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user.",
                            }
                        },
                        "required": ["user_id"],
                    },
                }
            ]
        }

    if method == "call_tool":
        tool_name = body.get("name")
        if tool_name == "get_user_profile":
            user_id = body.get("arguments", {}).get("user_id")
            return {
                "content": [
                    {
                        "type": "json",
                        "json": {
                            "id": user_id,
                            "name": "Jane Doe",
                            "email": "jane.doe@example.com",
                        },
                    }
                ]
            }

    raise HTTPException(status_code=400, detail=f"Unsupported method: {method}")

if __name__ == "__main__":
    print("Starting mock authenticated MCP server on http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)

# --8<-- [end:init]