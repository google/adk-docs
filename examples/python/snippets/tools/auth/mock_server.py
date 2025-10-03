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

from fastapi import FastAPI, Depends, HTTPException, status, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import httpx
from .models import UserInfo, Error

# Create FastAPI app
app = FastAPI(
    title="User Info API",
    description="API to retrieve user profile information based on a valid OIDC Access Token.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get(
    "/oidc-jwt-user-api",
    response_model=UserInfo,
    responses={
        401: {"model": Error, "description": "Unauthorized. The provided Bearer token is missing, invalid, or expired."},
        403: {"model": Error, "description": "Forbidden. The provided token does not have the required scopes or permissions to access this resource."},
    },
    tags=["User Profile"],
    summary="Get Authenticated User Info",
    description="Fetches profile details for the user",
    operation_id="getUserInfo",
)
async def get_user_info(request: Request, authorization: Optional[str] = Header(None)):
    """
    Get authenticated user information.
    
    This endpoint returns the profile information of the authenticated user
    based on the provided OIDC access token.
    
    The token must be provided in the Authorization header as a Bearer token.
    """
    # TODO: configure with your userinfo endpoint depend on where you deployed. 
    # Okta: https://your-endpoint.okta.com/oauth2/v1/userinfo
    # Google Account: https://openidconnect.googleapis.com/v1/userinfo  can be found within https://accounts.google.com/.well-known/openid-configuration
    USER_INFO_ENDPOINT="https://your-endpoint.okta.com/oauth2/v1/userinfo"

    # Check if Authorization header is present
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from Authorization header
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Use Bearer {token}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Make a request to UserInfo endpoint to get user info
        async with httpx.AsyncClient() as client:
            response = await client.get(
                USER_INFO_ENDPOINT,
                headers={
                    "Authorization": authorization
                }
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                error_detail = "Failed to retrieve user information"
                try:
                    error_data = response.json()
                    if "error" in error_data and "message" in error_data["error"]:
                        error_detail = error_data["error"]["message"]
                except:
                    pass
                
                if response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=error_detail,
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_detail,
                    )
            
            # Parse the response JSON
            user_data = response.json()
            
            # Convert the user data to a UserInfo model
            user_info = UserInfo(**user_data)
            return user_info
            
    except httpx.RequestError as e:
        # Handle network errors
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error connecting to UserInfo API: {str(e)}",
        )
    except Exception as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user data: {str(e)}",
        )


@app.get("/dev-ui")
async def callback(request: Request):
    # Get full URL from request
    url = str(request.url)
    return(url)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom exception handler for HTTP exceptions."""
    if exc.status_code == 401:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": "unauthorized", "message": exc.detail},
        )
    elif exc.status_code == 403:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": "forbidden", "message": exc.detail},
        )
    else:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": "error", "message": exc.detail},
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("user_info_api_server:app", host="0.0.0.0", port=8000, reload=True)