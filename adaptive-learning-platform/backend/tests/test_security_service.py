"""
Tests for security service (2FA and API keys).
"""
import pytest
from app.services.security_service import SecurityService


@pytest.mark.unit
def test_generate_2fa_secret():
    """Test 2FA secret generation."""
    secret, uri = SecurityService.generate_2fa_secret()

    assert len(secret) > 0
    assert uri.startswith("otpauth://")


@pytest.mark.unit
def test_verify_2fa_token():
    """Test 2FA token verification."""
    import pyotp

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    token = totp.now()

    # Should verify current token
    assert SecurityService.verify_2fa_token(secret, token) is True

    # Should not verify wrong token
    assert SecurityService.verify_2fa_token(secret, "000000") is False


@pytest.mark.unit
def test_generate_api_key():
    """Test API key generation."""
    api_key, key_hash = SecurityService.generate_api_key()

    assert api_key.startswith("ak_")
    assert len(key_hash) == 64  # SHA256 hex digest


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_and_verify_api_key(test_db, test_user):
    """Test creating and verifying an API key."""
    user_id = str(test_user["_id"])

    # Create API key
    key_id, api_key = await SecurityService.create_api_key(
        db=test_db,
        user_id=user_id,
        name="Test Key",
        scopes=["read"],
        expires_days=30
    )

    assert key_id is not None
    assert api_key.startswith("ak_")

    # Verify API key
    api_key_obj = await SecurityService.verify_api_key(test_db, api_key)

    assert api_key_obj is not None
    assert api_key_obj["user_id"] == user_id
    assert "read" in api_key_obj["scopes"]
