"""
Teacher dashboard routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime, timedelta

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.classroom import Classroom, Assignment

router = APIRouter()


@router.post("/classrooms")
async def create_classroom(
    classroom: Classroom,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Create a new classroom."""
    classroom.teacher_id = user_id
    result = await db.classrooms.insert_one(classroom.dict())

    return {
        "classroom_id": str(result.inserted_id),
        "message": "Classroom created successfully"
    }


@router.get("/classrooms")
async def list_classrooms(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """List all classrooms for a teacher."""
    cursor = db.classrooms.find({"teacher_id": user_id})
    classrooms = await cursor.to_list(length=100)

    return {"classrooms": classrooms}


@router.post("/classrooms/{classroom_id}/students")
async def add_student_to_classroom(
    classroom_id: str,
    student_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Add a student to a classroom."""
    classroom = await db.classrooms.find_one({
        "_id": ObjectId(classroom_id),
        "teacher_id": user_id
    })

    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    await db.classrooms.update_one(
        {"_id": ObjectId(classroom_id)},
        {"$addToSet": {"students": student_id}}
    )

    return {"message": "Student added to classroom"}


@router.get("/classrooms/{classroom_id}/analytics")
async def get_classroom_analytics(
    classroom_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get aggregate analytics for a classroom."""
    classroom = await db.classrooms.find_one({
        "_id": ObjectId(classroom_id),
        "teacher_id": user_id
    })

    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    # Get all sessions from students
    student_ids = classroom.get("students", [])
    sessions = await db.test_sessions.find({
        "user_id": {"$in": student_ids},
        "status": "completed"
    }).to_list(length=10000)

    if not sessions:
        return {"message": "No data yet"}

    # Calculate aggregates
    total_sessions = len(sessions)
    avg_score = sum(s.get("score", 0) for s in sessions) / total_sessions

    # Per-student stats
    student_stats = {}
    for student_id in student_ids:
        student_sessions = [s for s in sessions if str(s.get("user_id")) == student_id]
        if student_sessions:
            student_stats[student_id] = {
                "sessions_completed": len(student_sessions),
                "average_score": sum(s.get("score", 0) for s in student_sessions) / len(student_sessions),
                "last_activity": max(s.get("completed_at") for s in student_sessions if s.get("completed_at"))
            }

    return {
        "classroom_id": classroom_id,
        "total_students": len(student_ids),
        "total_sessions": total_sessions,
        "average_score": round(avg_score, 1),
        "student_stats": student_stats
    }


@router.get("/classrooms/{classroom_id}/alerts")
async def get_student_alerts(
    classroom_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get alerts for struggling students."""
    classroom = await db.classrooms.find_one({
        "_id": ObjectId(classroom_id),
        "teacher_id": user_id
    })

    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    alerts = []
    student_ids = classroom.get("students", [])

    for student_id in student_ids:
        # Get recent sessions
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_sessions = await db.test_sessions.find({
            "user_id": student_id,
            "completed_at": {"$gte": week_ago},
            "status": "completed"
        }).to_list(length=100)

        # Check for low scores
        if recent_sessions:
            avg_score = sum(s.get("score", 0) for s in recent_sessions) / len(recent_sessions)

            if avg_score < 50:
                alerts.append({
                    "student_id": student_id,
                    "alert_type": "low_score",
                    "severity": "high",
                    "message": f"Average score is {avg_score:.1f}% (last 7 days)"
                })
        else:
            # No recent activity
            alerts.append({
                "student_id": student_id,
                "alert_type": "no_progress",
                "severity": "medium",
                "message": "No activity in the last 7 days"
            })

    return {"alerts": alerts}
