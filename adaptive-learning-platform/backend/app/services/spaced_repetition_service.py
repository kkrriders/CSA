"""
Spaced Repetition Service implementing SM-2 algorithm.

The SM-2 (SuperMemo 2) algorithm calculates optimal review intervals based on:
- Quality of recall (0-5 rating)
- Number of consecutive successful reviews
- Ease factor (difficulty of the material)

Formula:
- If quality < 3: repetitions = 0, interval = 1
- If repetitions = 0: interval = 1
- If repetitions = 1: interval = 6
- If repetitions > 1: interval = interval * ease_factor

Ease factor:
- EF' = EF + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
- Minimum EF = 1.3
"""
from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.review import (
    Review,
    ReviewResponse,
    ReviewQueueItem,
    ReviewSchedule
)


class SpacedRepetitionService:
    """Service for managing spaced repetition reviews."""

    @staticmethod
    def calculate_next_review(
        interval: int,
        repetitions: int,
        ease_factor: float,
        quality: int
    ) -> tuple[int, int, float]:
        """
        Calculate next review using SM-2 algorithm.

        Args:
            interval: Current interval (days)
            repetitions: Number of consecutive successful reviews
            ease_factor: Current ease factor
            quality: Quality of recall (0-5)

        Returns:
            Tuple of (new_interval, new_repetitions, new_ease_factor)
        """
        # Update ease factor
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(1.3, new_ease_factor)  # Minimum EF = 1.3

        # If recall quality < 3, reset
        if quality < 3:
            new_repetitions = 0
            new_interval = 1
        else:
            new_repetitions = repetitions + 1

            if new_repetitions == 1:
                new_interval = 1
            elif new_repetitions == 2:
                new_interval = 6
            else:
                new_interval = round(interval * new_ease_factor)

        return new_interval, new_repetitions, new_ease_factor

    @staticmethod
    async def create_review(
        db: AsyncIOMotorDatabase,
        user_id: str,
        question_id: str,
        document_id: str,
        topic: str,
        difficulty: str
    ) -> str:
        """Create a new review item."""
        review = Review(
            question_id=question_id,
            user_id=user_id,
            document_id=document_id,
            topic=topic,
            difficulty=difficulty,
            interval=1,
            repetitions=0,
            ease_factor=2.5,
            next_review_date=datetime.utcnow() + timedelta(days=1)
        )

        result = await db.reviews.insert_one(review.dict())
        return str(result.inserted_id)

    @staticmethod
    async def update_review(
        db: AsyncIOMotorDatabase,
        review_id: str,
        response: ReviewResponse
    ) -> Review:
        """Update review after user response."""
        # Get current review
        review_data = await db.reviews.find_one({"_id": ObjectId(review_id)})
        if not review_data:
            raise ValueError("Review not found")

        review = Review(**{**review_data, "_id": str(review_data["_id"])})

        # Calculate next review using SM-2
        new_interval, new_repetitions, new_ease_factor = SpacedRepetitionService.calculate_next_review(
            review.interval,
            review.repetitions,
            review.ease_factor,
            response.quality
        )

        # Update review
        review.interval = new_interval
        review.repetitions = new_repetitions
        review.ease_factor = new_ease_factor
        review.next_review_date = datetime.utcnow() + timedelta(days=new_interval)
        review.last_reviewed_at = datetime.utcnow()
        review.total_reviews += 1

        if response.correct:
            review.successful_reviews += 1

        # Update average quality (running average)
        review.average_quality = (
            (review.average_quality * (review.total_reviews - 1) + response.quality)
            / review.total_reviews
        )
        review.updated_at = datetime.utcnow()

        # Save to database
        await db.reviews.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": review.dict(exclude={"question_id", "user_id"})}
        )

        return review

    @staticmethod
    async def get_due_reviews(
        db: AsyncIOMotorDatabase,
        user_id: str,
        document_id: Optional[str] = None,
        limit: int = 20
    ) -> List[ReviewQueueItem]:
        """Get reviews that are due for the user."""
        query = {
            "user_id": user_id,
            "next_review_date": {"$lte": datetime.utcnow()}
        }

        if document_id:
            query["document_id"] = document_id

        cursor = db.reviews.find(query).sort("next_review_date", 1).limit(limit)
        reviews = await cursor.to_list(length=limit)

        queue_items = []
        for review in reviews:
            days_overdue = (datetime.utcnow() - review["next_review_date"]).days

            # Calculate priority (higher for overdue, lower ease factor, more repetitions)
            priority = (
                days_overdue * 2 +  # Overdue reviews get higher priority
                (3.0 - review["ease_factor"]) * 10 +  # Harder items get higher priority
                review["repetitions"] * 0.5  # Items with more reps get slightly higher priority
            )

            queue_items.append(ReviewQueueItem(
                review_id=str(review["_id"]),
                question_id=review["question_id"],
                topic=review["topic"],
                difficulty=review["difficulty"],
                next_review_date=review["next_review_date"],
                days_overdue=max(0, days_overdue),
                priority=priority
            ))

        # Sort by priority (highest first)
        queue_items.sort(key=lambda x: x.priority, reverse=True)

        return queue_items

    @staticmethod
    async def get_review_schedule(
        db: AsyncIOMotorDatabase,
        user_id: str,
        document_id: Optional[str] = None,
        topic: Optional[str] = None
    ) -> ReviewSchedule:
        """Get review schedule summary."""
        query = {"user_id": user_id}

        if document_id:
            query["document_id"] = document_id
        if topic:
            query["topic"] = topic

        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        next_week = now + timedelta(days=7)
        next_month = now + timedelta(days=30)

        # Count reviews by time period
        due_today = await db.reviews.count_documents({
            **query,
            "next_review_date": {"$lte": tomorrow}
        })

        due_this_week = await db.reviews.count_documents({
            **query,
            "next_review_date": {"$lte": next_week}
        })

        due_this_month = await db.reviews.count_documents({
            **query,
            "next_review_date": {"$lte": next_month}
        })

        total_reviews = await db.reviews.count_documents(query)

        # Get next review
        next_review = await db.reviews.find_one(
            query,
            sort=[("next_review_date", 1)]
        )

        return ReviewSchedule(
            user_id=user_id,
            document_id=document_id,
            topic=topic,
            due_today=due_today,
            due_this_week=due_this_week,
            due_this_month=due_this_month,
            total_reviews=total_reviews,
            next_review_date=next_review["next_review_date"] if next_review else None,
            next_review_topic=next_review["topic"] if next_review else None
        )

    @staticmethod
    async def create_reviews_from_mistakes(
        db: AsyncIOMotorDatabase,
        user_id: str,
        session_id: str
    ) -> int:
        """
        Create review items from questions answered incorrectly in a session.

        Returns:
            Number of reviews created
        """
        # Get session
        session = await db.test_sessions.find_one({"_id": ObjectId(session_id)})
        if not session:
            return 0

        # Get incorrect answers
        incorrect_question_ids = [
            ObjectId(ans["question_id"])
            for ans in session["answers"]
            if not ans.get("correct", False)
        ]

        if not incorrect_question_ids:
            return 0

        # Get question details
        questions = await db.questions.find(
            {"_id": {"$in": incorrect_question_ids}}
        ).to_list(length=1000)

        reviews_created = 0
        for question in questions:
            # Check if review already exists
            existing = await db.reviews.find_one({
                "user_id": user_id,
                "question_id": str(question["_id"])
            })

            if not existing:
                await SpacedRepetitionService.create_review(
                    db=db,
                    user_id=user_id,
                    question_id=str(question["_id"]),
                    document_id=str(question["document_id"]),
                    topic=question["topic"],
                    difficulty=question["difficulty"]
                )
                reviews_created += 1

        return reviews_created

    @staticmethod
    async def reschedule_review(
        db: AsyncIOMotorDatabase,
        review_id: str,
        new_date: datetime
    ):
        """Manually reschedule a review."""
        await db.reviews.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": {
                "next_review_date": new_date,
                "updated_at": datetime.utcnow()
            }}
        )
