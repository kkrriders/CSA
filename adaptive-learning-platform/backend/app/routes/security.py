"""
Security routes for 2FA and API keys.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
import qrcode
import io
import base64

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.security import Enable2FARequest, Verify2FARequest, CreateAPIKeyRequest
from app.services.security_service import SecurityService

router = APIRouter()


@router.post("/2fa/setup")
async def setup_2fa(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Initialize 2FA setup."""
    # Check if already enabled
    existing = await db.two_factor_auth.find_one({"user_id": user_id})
    if existing and existing.get("enabled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )

    # Generate secret
    secret, provisioning_uri = SecurityService.generate_2fa_secret()

    # Store in database (not yet enabled)
    await db.two_factor_auth.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "secret": secret,
                "enabled": False
            }
        },
        upsert=True
    )

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_code_base64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "secret": secret,
        "qr_code": f"data:image/png;base64,{qr_code_base64}",
        "message": "Scan the QR code with your authenticator app, then verify with a token"
    }


@router.post("/2fa/enable")
async def enable_2fa(
    request: Enable2FARequest,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Enable 2FA after verifying token."""
    success = await SecurityService.enable_2fa(db=db, user_id=user_id, token=request.token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    # Get backup codes
    tfa = await db.two_factor_auth.find_one({"user_id": user_id})

    return {
        "message": "2FA enabled successfully",
        "backup_codes": tfa.get("backup_codes", [])
    }


@router.post("/2fa/disable")
async def disable_2fa(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Disable 2FA."""
    await SecurityService.disable_2fa(db=db, user_id=user_id)
    return {"message": "2FA disabled successfully"}


@router.post("/2fa/verify")
async def verify_2fa(
    request: Verify2FARequest,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Verify a 2FA token."""
    tfa = await db.two_factor_auth.find_one({"user_id": user_id, "enabled": True})

    if not tfa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="2FA not enabled"
        )

    valid = SecurityService.verify_2fa_token(tfa["secret"], request.token)

    return {"valid": valid}


@router.post("/api-keys")
async def create_api_key(
    request: CreateAPIKeyRequest,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Create a new API key."""
    key_id, api_key = await SecurityService.create_api_key(
        db=db,
        user_id=user_id,
        name=request.name,
        scopes=request.scopes,
        expires_days=request.expires_days
    )

    return {
        "key_id": key_id,
        "api_key": api_key,
        "message": "API key created. Save it now - it won't be shown again!"
    }


@router.get("/api-keys")
async def list_api_keys(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """List all API keys for the user."""
    cursor = db.api_keys.find({"user_id": user_id, "revoked": False})
    keys = await cursor.to_list(length=100)

    # Remove sensitive data
    for key in keys:
        key.pop("key_hash", None)

    return {"api_keys": keys}


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Revoke an API key."""
    await SecurityService.revoke_api_key(db=db, key_id=key_id, user_id=user_id)
    return {"message": "API key revoked successfully"}
