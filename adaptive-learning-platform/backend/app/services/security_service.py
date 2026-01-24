"""
Security service for 2FA and API key management.
"""
import pyotp
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.security import TwoFactorAuth, APIKey


class SecurityService:
    """Service for advanced security features."""

    @staticmethod
    def generate_2fa_secret() -> Tuple[str, str]:
        """Generate a new 2FA secret and provisioning URI."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name="user@adaptivelearning.com",
            issuer_name="Adaptive Learning Platform"
        )
        return secret, provisioning_uri

    @staticmethod
    def verify_2fa_token(secret: str, token: str) -> bool:
        """Verify a 2FA token."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

    @staticmethod
    def generate_backup_codes(count: int = 8) -> list[str]:
        """Generate backup codes for 2FA."""
        return [secrets.token_hex(4) for _ in range(count)]

    @staticmethod
    async def enable_2fa(
        db: AsyncIOMotorDatabase,
        user_id: str,
        token: str
    ) -> bool:
        """Enable 2FA for a user after verifying initial token."""
        # Get pending 2FA setup
        tfa = await db.two_factor_auth.find_one({"user_id": user_id})

        if not tfa:
            return False

        # Verify token
        if not SecurityService.verify_2fa_token(tfa["secret"], token):
            return False

        # Generate backup codes
        backup_codes = SecurityService.generate_backup_codes()

        # Enable 2FA
        await db.two_factor_auth.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "enabled": True,
                    "backup_codes": backup_codes,
                    "last_used": datetime.utcnow()
                }
            }
        )

        return True

    @staticmethod
    async def disable_2fa(
        db: AsyncIOMotorDatabase,
        user_id: str
    ):
        """Disable 2FA for a user."""
        await db.two_factor_auth.delete_one({"user_id": user_id})

    @staticmethod
    def generate_api_key() -> Tuple[str, str]:
        """Generate a new API key and its hash."""
        # Generate random API key
        api_key = f"ak_{secrets.token_urlsafe(32)}"

        # Hash it for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        return api_key, key_hash

    @staticmethod
    async def create_api_key(
        db: AsyncIOMotorDatabase,
        user_id: str,
        name: str,
        scopes: list[str],
        expires_days: Optional[int] = None
    ) -> Tuple[str, str]:
        """Create a new API key."""
        api_key, key_hash = SecurityService.generate_api_key()
        key_id = secrets.token_hex(8)

        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)

        api_key_obj = APIKey(
            key_id=key_id,
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            scopes=scopes,
            expires_at=expires_at
        )

        await db.api_keys.insert_one(api_key_obj.dict())

        return key_id, api_key  # Return plaintext key only once

    @staticmethod
    async def verify_api_key(
        db: AsyncIOMotorDatabase,
        api_key: str
    ) -> Optional[dict]:
        """Verify an API key and return user info."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        api_key_obj = await db.api_keys.find_one({
            "key_hash": key_hash,
            "revoked": False
        })

        if not api_key_obj:
            return None

        # Check expiration
        if api_key_obj.get("expires_at") and api_key_obj["expires_at"] < datetime.utcnow():
            return None

        # Update usage
        await db.api_keys.update_one(
            {"_id": api_key_obj["_id"]},
            {
                "$set": {"last_used": datetime.utcnow()},
                "$inc": {"uses_count": 1}
            }
        )

        return api_key_obj

    @staticmethod
    async def revoke_api_key(
        db: AsyncIOMotorDatabase,
        key_id: str,
        user_id: str
    ):
        """Revoke an API key."""
        await db.api_keys.update_one(
            {"key_id": key_id, "user_id": user_id},
            {"$set": {"revoked": True}}
        )
