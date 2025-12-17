from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class JWTPayload(BaseModel):
    """
    Schema for JWT token payload
    """
    sub: Optional[str] = Field(None, description="Subject - typically user ID")
    userId: Optional[str] = Field(None, description="User ID from Better Auth")
    email: Optional[str] = Field(None, description="User email")
    name: Optional[str] = Field(None, description="User name")
    iat: Optional[int] = Field(None, description="Issued at time (timestamp)")
    exp: Optional[int] = Field(None, description="Expiration time (timestamp)")
    nbf: Optional[int] = Field(None, description="Not before time (timestamp)")
    iss: Optional[str] = Field(None, description="Issuer")
    aud: Optional[str] = Field(None, description="Audience")

    class Config:
        extra = "allow"  # Allow additional fields that might be in the JWT


class AuthenticatedUser(BaseModel):
    """
    Schema for authenticated user information
    """
    user_id: str = Field(..., description="Unique identifier for the user")
    email: Optional[str] = Field(None, description="User's email address")
    name: Optional[str] = Field(None, description="User's display name")
    token_valid: bool = Field(True, description="Whether the token is currently valid")
    permissions: List[str] = Field(default_factory=list, description="User permissions/roles")
    token_expires_at: Optional[datetime] = Field(None, description="When the token expires")


class AuthTokenResponse(BaseModel):
    """
    Schema for authentication token response
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Type of token")
    expires_in: Optional[int] = Field(None, description="Token expiration in seconds")
    user: Optional[AuthenticatedUser] = Field(None, description="User information")


class AuthError(BaseModel):
    """
    Schema for authentication error responses
    """
    error_code: str = Field(..., description="Error code (e.g., INVALID_TOKEN, UNAUTHORIZED)")
    message: str = Field(..., description="Human-readable error message")
    timestamp: datetime = Field(default_factory=datetime.now, description="When error occurred")
    request_id: Optional[str] = Field(None, description="Request ID for debugging correlation")


class TokenVerificationRequest(BaseModel):
    """
    Schema for token verification requests
    """
    token: str = Field(..., description="JWT token to verify")


class TokenVerificationResponse(BaseModel):
    """
    Schema for token verification responses
    """
    valid: bool = Field(..., description="Whether the token is valid")
    user_id: Optional[str] = Field(None, description="User ID if token is valid")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    payload: Optional[Dict[str, Any]] = Field(None, description="Full token payload")


class UserAccessCheck(BaseModel):
    """
    Schema for user access verification
    """
    user_id: str = Field(..., description="ID of the authenticated user")
    resource_owner_id: str = Field(..., description="ID of the resource owner")
    access_granted: bool = Field(..., description="Whether access is granted")
    reason: Optional[str] = Field(None, description="Reason for access decision")