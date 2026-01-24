"""
Question bank management routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
import json
import csv
import io

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.services.question_similarity_service import QuestionSimilarityService

router = APIRouter()


@router.get("/{question_id}/similar")
async def find_similar_questions(
    question_id: str,
    threshold: float = 0.7,
    limit: int = 10,
    db=Depends(get_database)
):
    """Find similar questions."""
    similar = await QuestionSimilarityService.find_similar_questions(
        db=db,
        question_id=question_id,
        threshold=threshold,
        limit=limit
    )

    return {"similar_questions": similar, "count": len(similar)}


@router.put("/{question_id}/recalibrate")
async def recalibrate_difficulty(
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Recalibrate question difficulty based on empirical data."""
    new_difficulty = await QuestionSimilarityService.recalibrate_difficulty(
        db=db,
        question_id=question_id
    )

    return {
        "question_id": question_id,
        "new_difficulty": new_difficulty,
        "message": "Difficulty recalibrated"
    }


@router.post("/bulk/import")
async def bulk_import_questions(
    document_id: str,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Bulk import questions from CSV or JSON."""
    content = await file.read()
    questions_data = []

    # Parse file based on type
    if file.filename.endswith('.json'):
        questions_data = json.loads(content.decode())
    elif file.filename.endswith('.csv'):
        csv_content = content.decode()
        reader = csv.DictReader(io.StringIO(csv_content))
        questions_data = list(reader)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JSON and CSV files are supported"
        )

    count = await QuestionSimilarityService.bulk_import_questions(
        db=db,
        questions_data=questions_data,
        document_id=document_id
    )

    return {
        "imported_count": count,
        "message": f"Successfully imported {count} questions"
    }


@router.get("/bulk/export")
async def export_questions(
    document_id: str,
    format: str = "json",
    db=Depends(get_database)
):
    """Export questions for a document."""
    questions = await QuestionSimilarityService.export_questions(
        db=db,
        document_id=document_id
    )

    if format == "csv":
        # Convert to CSV
        if not questions:
            return {"questions": [], "format": "csv"}

        output = io.StringIO()
        fieldnames = questions[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(questions)

        return {
            "data": output.getvalue(),
            "format": "csv"
        }

    return {
        "questions": questions,
        "count": len(questions),
        "format": "json"
    }
