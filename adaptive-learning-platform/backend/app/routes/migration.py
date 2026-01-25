from fastapi import APIRouter, Depends
from app.core.database import get_database

router = APIRouter()


@router.post("/fix-question-tracking-fields")
async def fix_question_tracking_fields(db=Depends(get_database)):
    """
    Migration endpoint: Add tracking fields to existing questions
    Run this once to fix old questions that don't have is_mastered, times_answered, etc.
    """

    # Update all questions that don't have tracking fields
    result = await db.questions.update_many(
        {
            "$or": [
                {"is_mastered": {"$exists": False}},
                {"times_answered": {"$exists": False}},
                {"times_correct": {"$exists": False}},
                {"last_used_at": {"$exists": False}}
            ]
        },
        {
            "$set": {
                "is_mastered": False,
                "times_answered": 0,
                "times_correct": 0,
                "last_used_at": None
            }
        }
    )

    return {
        "status": "success",
        "questions_updated": result.modified_count,
        "message": f"Added tracking fields to {result.modified_count} existing questions"
    }
