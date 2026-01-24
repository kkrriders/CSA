"""
Data export and privacy compliance routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from bson import ObjectId
import json

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.services.export_service import ExportService
from app.models.user import UserInDB

router = APIRouter()


@router.get("/export")
async def export_all_data(
    format: str = "json",
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Export all user data (GDPR compliance)."""
    data = await ExportService.export_all_user_data(db=db, user_id=user_id)

    # Log export
    await ExportService.log_export(db=db, user_id=user_id, export_type="full_export")

    if format == "json":
        return Response(
            content=json.dumps(data, indent=2, default=str),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=user_data_{user_id}.json"}
        )

    return data


@router.delete("/delete-all-data")
async def delete_all_user_data(
    confirm: bool = False,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Delete all user data (GDPR right to be forgotten)."""
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must confirm deletion with confirm=true parameter"
        )

    # Log before deletion
    await ExportService.log_export(db=db, user_id=user_id, export_type="data_deletion")

    deleted_count = await ExportService.delete_all_user_data(db=db, user_id=user_id)

    return {
        "message": "All user data deleted successfully",
        "deleted_records": deleted_count
    }


@router.get("/audit-log")
async def get_audit_log(
    limit: int = 100,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get user's audit log (data exports and deletions)."""
    cursor = db.data_exports.find({"user_id": user_id}).sort("exported_at", -1).limit(limit)
    logs = await cursor.to_list(length=limit)

    return {"audit_log": logs, "total": len(logs)}
