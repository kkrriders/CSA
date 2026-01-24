"""
Security models for 2FA and API keys.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TwoFactorAuth(BaseModel):
    """Two-factor authentication model."""
    user_id: str
    secret: str
    enabled: bool = False
    backup_codes: list[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None


class APIKey(BaseModel):
    """API key for programmatic access."""
    key_id: str
    user_id: str
    name: str
    key_hash: str  # Hashed API key
    scopes: list[str] = ["read"]  # Permissions

    # Usage tracking
    last_used: Optional[datetime] = None
    uses_count: int = 0

    # Expiration
    expires_at: Optional[datetime] = None
    revoked: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)


class Enable2FARequest(BaseModel):
    """Request to enable 2FA."""
    token: str  # TOTP token to verify


class Verify2FARequest(BaseModel):
    """Request to verify 2FA."""
    token: str


class CreateAPIKeyRequest(BaseModel):
    """Request to create API key."""
    name: str
    scopes: list[str] = ["read"]
    expires_days: Optional[int] = None
