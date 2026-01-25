"""
Question Selection Service - Smart question reuse and selection

Reduces LLM costs and database load by intelligently reusing existing questions
"""

from typing import List, Dict, Optional, Tuple
from bson import ObjectId
from datetime import datetime


class QuestionSelectionService:
    """
    Intelligent question selection that prioritizes reuse over regeneration
    """

    @staticmethod
    async def get_available_questions(
        document_id: str,
        user_id: str,
        num_needed: int,
        question_types: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        difficulty_levels: Optional[List[str]] = None,
        db = None
    ) -> Tuple[List[Dict], bool]:
        """
        Get available questions for a test, returns (questions, needs_generation)

        Selection Priority:
        1. Never answered questions (fresh)
        2. Answered wrong (needs practice)
        3. Answered correct once (needs reinforcement)
        4. Skip: Answered correct 2+ times (mastered)

        Returns:
            tuple: (list of questions, boolean indicating if more generation needed)
        """

        # Build query - treat missing is_mastered field as False (backwards compatibility)
        query = {
            "document_id": ObjectId(document_id),
            "user_id": ObjectId(user_id),
            "$or": [
                {"is_mastered": False},
                {"is_mastered": {"$exists": False}}  # Old questions without tracking fields
            ]
        }

        # Apply filters
        if question_types:
            query["question_type"] = {"$in": question_types}
        if topics:
            query["topic"] = {"$in": topics}
        if difficulty_levels:
            query["difficulty"] = {"$in": difficulty_levels}

        # Get all available (non-mastered) questions
        cursor = db.questions.find(query)
        all_questions = await cursor.to_list(length=1000)

        # Prioritize questions by usage
        prioritized = QuestionSelectionService._prioritize_questions(all_questions)

        # Take the needed amount
        selected = prioritized[:num_needed]

        # Determine if we need to generate more
        needs_generation = len(selected) < num_needed

        return selected, needs_generation

    @staticmethod
    def _prioritize_questions(questions: List[Dict]) -> List[Dict]:
        """
        Sort questions by priority (smart reuse strategy)

        Priority Order:
        1. Never answered (times_answered = 0)
        2. Answered wrong more than correct (times_correct < times_answered)
        3. Answered correct but only once (times_correct = 1)
        4. Least recently used (older last_used_at)
        """

        def priority_score(q: Dict) -> tuple:
            times_answered = q.get("times_answered", 0)
            times_correct = q.get("times_correct", 0)
            last_used = q.get("last_used_at", datetime.min)

            # Never answered = highest priority (0)
            if times_answered == 0:
                return (0, last_used)

            # Answered wrong more than correct = high priority (1)
            if times_correct < times_answered:
                return (1, last_used)

            # Answered correct once = medium priority (2)
            if times_correct == 1:
                return (2, last_used)

            # Everything else = lower priority (3)
            return (3, last_used)

        return sorted(questions, key=priority_score)

    @staticmethod
    async def mark_questions_used(
        question_ids: List[str],
        db = None
    ):
        """
        Mark questions as used in a test (update last_used_at)
        """
        await db.questions.update_many(
            {"_id": {"$in": [ObjectId(qid) for qid in question_ids]}},
            {"$set": {"last_used_at": datetime.utcnow()}}
        )

    @staticmethod
    async def update_question_performance(
        question_id: str,
        is_correct: bool,
        db = None
    ):
        """
        Update question performance after being answered

        Increments:
        - times_answered (always)
        - times_correct (if correct)

        Updates:
        - is_mastered (if answered correctly 2+ times)
        """
        update = {
            "$inc": {
                "times_answered": 1,
                "times_correct": 1 if is_correct else 0
            }
        }

        # Update the question
        result = await db.questions.find_one_and_update(
            {"_id": ObjectId(question_id)},
            update,
            return_document=True
        )

        # Check if it should be marked as mastered
        if result:
            times_correct = result.get("times_correct", 0)
            if times_correct >= 2 and not result.get("is_mastered", False):
                await db.questions.update_one(
                    {"_id": ObjectId(question_id)},
                    {"$set": {"is_mastered": True}}
                )

    @staticmethod
    async def get_question_pool_stats(
        document_id: str,
        user_id: str,
        db = None
    ) -> Dict:
        """
        Get statistics about the question pool for a document

        Returns:
            dict with counts of:
            - total: total questions
            - available: non-mastered questions
            - never_answered: fresh questions
            - needs_practice: answered wrong
            - mastered: answered correctly 2+ times
        """
        query_base = {
            "document_id": ObjectId(document_id),
            "user_id": ObjectId(user_id)
        }

        total = await db.questions.count_documents(query_base)

        # Backwards compatible queries - handle old questions without tracking fields
        available = await db.questions.count_documents({
            **query_base,
            "$or": [
                {"is_mastered": False},
                {"is_mastered": {"$exists": False}}
            ]
        })

        never_answered = await db.questions.count_documents({
            **query_base,
            "$or": [
                {"times_answered": 0},
                {"times_answered": {"$exists": False}}
            ]
        })

        needs_practice = await db.questions.count_documents({
            **query_base,
            "$expr": {"$lt": ["$times_correct", "$times_answered"]},
            "$or": [
                {"is_mastered": False},
                {"is_mastered": {"$exists": False}}
            ]
        })

        mastered = await db.questions.count_documents({
            **query_base,
            "is_mastered": True
        })

        return {
            "total": total,
            "available": available,
            "never_answered": never_answered,
            "needs_practice": needs_practice,
            "mastered": mastered
        }
