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

from pydantic import BaseModel, EmailStr, Field


class UserInfo(BaseModel):
    """User information model based on Okta OIDC response."""
    sub: str = Field(..., description="Subject identifier for the user")
    name: str = Field(..., description="Full name of the user")
    locale: str = Field(..., description="User's locale, e.g., en-US or en_US")
    email: EmailStr = Field(..., description="User's primary email address")
    preferred_username: str = Field(..., description="Preferred username of the user (often the email)")
    given_name: str = Field(..., description="Given name (first name) of the user")
    family_name: str = Field(..., description="Family name (last name) of the user")
    zoneinfo: str = Field(..., description="User's timezone, e.g., America/Los_Angeles")
    updated_at: int = Field(..., description="Timestamp when the user's profile was last updated (Unix epoch time)")
    email_verified: bool = Field(..., description="Indicates if the user's email address has been verified")


class Error(BaseModel):
    """Error response model based on the OpenAPI specification."""
    code: str = Field(..., description="An error code")
    message: str = Field(..., description="A human-readable error message")