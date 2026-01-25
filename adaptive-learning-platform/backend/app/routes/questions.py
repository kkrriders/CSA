from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import List
from bson import ObjectId
from datetime import datetime
import random

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.question import (
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    QuestionResponse,
    QuestionType,
    DifficultyLevel,
    MCQOption
)
from app.services.llm_service import LLMService
from app.services.question_selection_service import QuestionSelectionService

router = APIRouter()


async def generate_questions_background(
    document_id: str,
    user_id: str,
    num_questions: int,
    difficulty_distribution: dict,
    topics: List[str],
    question_types: List[QuestionType]
):
    """Background task to generate questions"""
    from app.core.database import get_database

    db = get_database()
    llm_service = LLMService()

    try:
        print(f"[Question Gen] Starting generation for document {document_id}")

        # Get document
        document = await db.documents.find_one({"_id": ObjectId(document_id)})
        if not document:
            print(f"[Question Gen] ERROR: Document {document_id} not found")
            return

        sections = document.get("sections", [])
        print(f"[Question Gen] Found {len(sections)} sections")

        if not sections:
            print(f"[Question Gen] ERROR: No sections in document")
            return

        # Filter sections by topics if specified
        if topics:
            sections = [s for s in sections if any(t in s.get("topics", []) for t in topics)]

        if not sections:
            sections = document.get("sections", [])

        # Distribute questions across sections
        questions_per_section = max(1, num_questions // len(sections))

        generated_questions = []

        # Keep generating until we have enough questions
        while len(generated_questions) < num_questions:
            # Cycle through sections if we need more questions than sections
            for section in sections:
                if len(generated_questions) >= num_questions:
                    break

                section_context = section.get("content", "")
                section_topic = section.get("title", "General")

                # Determine difficulty for this question
                if difficulty_distribution:
                    available_difficulties = [
                        k for k, v in difficulty_distribution.items() if v > 0
                    ]
                    if available_difficulties:
                        difficulty = random.choice(available_difficulties)
                        difficulty_distribution[difficulty] -= 1
                    else:
                        difficulty = "medium"
                else:
                    difficulty = random.choice(["easy", "medium", "hard", "tricky"])

                # Determine question type
                question_type = random.choice(question_types)

                # Generate questions using LLM
                try:
                    print(f"[Question Gen] Generating question {len(generated_questions) + 1}/{num_questions} for section: {section_topic}")

                    questions = await llm_service.generate_questions_from_context(
                        context=section_context[:2000],  # Limit context size
                        topic=section_topic,
                        num_questions=1,
                        difficulty=difficulty,
                        question_type=question_type
                    )

                    print(f"[Question Gen] LLM returned {len(questions)} questions")

                    for q in questions:
                        # Ensure question_type is stored as string value, not enum
                        q_type = q["question_type"]
                        if hasattr(q_type, 'value'):
                            q_type = q_type.value
                        elif isinstance(q_type, str) and '.' in q_type:
                            # Handle "QuestionType.MCQ" format
                            q_type = q_type.split('.')[-1].lower()

                        question_doc = {
                            "document_id": ObjectId(document_id),
                            "user_id": ObjectId(user_id),
                            "question_text": q["question_text"],
                            "question_type": q_type,
                            "difficulty": q["difficulty"],
                            "topic": q["topic"],
                            "section_title": section.get("title"),
                            "options": q.get("options", []),
                            "correct_answer": q["correct_answer"],
                            "explanation": q["explanation"],
                            "source_context": q.get("source_context", section_context[:500]),
                            "created_at": datetime.utcnow()
                        }

                        result = await db.questions.insert_one(question_doc)
                        generated_questions.append(str(result.inserted_id))
                        print(f"[Question Gen] Saved question {len(generated_questions)}/{num_questions}")

                        if len(generated_questions) >= num_questions:
                            break

                except Exception as e:
                    print(f"[Question Gen] ERROR for section {section_topic}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

        print(f"[Question Gen] COMPLETED: Generated {len(generated_questions)} questions total")

    except Exception as e:
        print(f"[Question Gen] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await llm_service.close()


@router.post("/generate", response_model=GenerateQuestionsResponse)
async def generate_questions(
    request: GenerateQuestionsRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Generate questions from a document"""

    # Verify document exists and belongs to user
    document = await db.documents.find_one({
        "_id": ObjectId(request.document_id),
        "user_id": ObjectId(user_id)
    })

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if document["processing_status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is still processing"
        )

    # Start background generation
    background_tasks.add_task(
        generate_questions_background,
        request.document_id,
        user_id,
        request.num_questions,
        request.difficulty_distribution,
        request.topics,
        request.question_types
    )

    return GenerateQuestionsResponse(
        document_id=request.document_id,
        total_generated=0,  # Will be generated in background
        questions=[]
    )


@router.get("/document/{document_id}", response_model=List[QuestionResponse])
async def get_questions_for_document(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get all questions for a document"""

    # Verify document belongs to user
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": ObjectId(user_id)
    })

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Get questions
    cursor = db.questions.find({"document_id": ObjectId(document_id)})
    questions = await cursor.to_list(length=1000)

    return [
        QuestionResponse(
            _id=str(q["_id"]),
            question_text=q["question_text"],
            question_type=q["question_type"],
            difficulty=q["difficulty"],
            topic=q["topic"],
            section_title=q.get("section_title"),
            options=[
                {"text": opt["text"]}
                for opt in q.get("options", [])
            ] if q.get("options") else None
        )
        for q in questions
    ]


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get a specific question (without answer)"""

    question = await db.questions.find_one({
        "_id": ObjectId(question_id),
        "user_id": ObjectId(user_id)
    })

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    return QuestionResponse(
        _id=str(question["_id"]),
        question_text=question["question_text"],
        question_type=question["question_type"],
        difficulty=question["difficulty"],
        topic=question["topic"],
        section_title=question.get("section_title"),
        options=[
            {"text": opt["text"]}
            for opt in question.get("options", [])
        ] if question.get("options") else None
    )


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Delete a question"""

    result = await db.questions.delete_one({
        "_id": ObjectId(question_id),
        "user_id": ObjectId(user_id)
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    return None


@router.get("/document/{document_id}/pool-stats")
async def get_question_pool_stats(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """
    Get statistics about the question pool for a document

    Shows how many questions are:
    - Total: all questions ever generated
    - Available: questions that can be used (not mastered)
    - Never answered: fresh questions
    - Needs practice: questions answered wrong
    - Mastered: questions answered correctly 2+ times
    """

    stats = await QuestionSelectionService.get_question_pool_stats(
        document_id=document_id,
        user_id=user_id,
        db=db
    )

    return {
        "document_id": document_id,
        **stats,
        "message": f"{stats['available']} questions available for testing"
    }
