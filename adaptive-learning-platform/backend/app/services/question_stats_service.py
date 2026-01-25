
from typing import Optional
from bson import ObjectId
from app.models.analytics import QuestionStatistics
from app.core.database import get_database


class QuestionStatsService:
    """Manage empirical question difficulty"""

    @staticmethod
    async def get_question_stats(
        question_id: str,
        db
    ) -> Optional[QuestionStatistics]:
        """Get statistics for a question"""

        stats_doc = await db.question_statistics.find_one({
            "question_id": question_id
        })

        if stats_doc:
            return QuestionStatistics(**stats_doc)
        return None

    @staticmethod
    async def update_question_stats(
        question_id: str,
        correct: bool,
        time_taken: int,
        db
    ):
        """Update question statistics after an attempt"""

        stats_doc = await db.question_statistics.find_one({
            "question_id": question_id
        })

        if stats_doc:
            # Update existing stats
            stats = QuestionStatistics(**stats_doc)
            stats.update_from_attempt(correct, time_taken)

            await db.question_statistics.update_one(
                {"question_id": question_id},
                {"$set": stats.dict()}
            )
        else:
            # Create new stats (bootstrap at 0.5 difficulty)
            stats = QuestionStatistics(question_id=question_id)
            stats.update_from_attempt(correct, time_taken)

            await db.question_statistics.insert_one(stats.dict())

    @staticmethod
    async def get_empirical_difficulty(
        question_id: str,
        db
    ) -> float:
        """Get empirical difficulty (% who got it right)"""

        stats = await QuestionStatsService.get_question_stats(question_id, db)

        if stats:
            return stats.empirical_difficulty

        # Bootstrap at 0.5 if no data yet
        return 0.5
