"""
Question similarity and management service.
"""
from typing import List, Dict
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import re
from collections import Counter
import math


class QuestionSimilarityService:
    """Service for question similarity detection and management."""

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text for similarity comparison."""
        # Convert to lowercase and split on non-alphanumeric
        tokens = re.findall(r'\w+', text.lower())
        return tokens

    @staticmethod
    def cosine_similarity(text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        tokens1 = QuestionSimilarityService.tokenize(text1)
        tokens2 = QuestionSimilarityService.tokenize(text2)

        # Create term frequency vectors
        vec1 = Counter(tokens1)
        vec2 = Counter(tokens2)

        # Get intersection
        intersection = set(vec1.keys()) & set(vec2.keys())

        if not intersection:
            return 0.0

        # Calculate dot product
        dot_product = sum(vec1[term] * vec2[term] for term in intersection)

        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(count ** 2 for count in vec1.values()))
        magnitude2 = math.sqrt(sum(count ** 2 for count in vec2.values()))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    @staticmethod
    async def find_similar_questions(
        db: AsyncIOMotorDatabase,
        question_id: str,
        threshold: float = 0.7,
        limit: int = 10
    ) -> List[Dict]:
        """Find similar questions based on text similarity."""
        # Get the source question
        source = await db.questions.find_one({"_id": ObjectId(question_id)})
        if not source:
            return []

        source_text = source.get("question_text", "")
        document_id = source.get("document_id")

        # Get all questions from the same document
        cursor = db.questions.find({
            "document_id": document_id,
            "_id": {"$ne": ObjectId(question_id)}
        })
        questions = await cursor.to_list(length=1000)

        # Calculate similarities
        similar = []
        for question in questions:
            question_text = question.get("question_text", "")
            similarity = QuestionSimilarityService.cosine_similarity(source_text, question_text)

            if similarity >= threshold:
                similar.append({
                    "question_id": str(question["_id"]),
                    "question_text": question_text,
                    "topic": question.get("topic"),
                    "difficulty": question.get("difficulty"),
                    "similarity_score": round(similarity, 3)
                })

        # Sort by similarity
        similar.sort(key=lambda x: x["similarity_score"], reverse=True)

        return similar[:limit]

    @staticmethod
    async def recalibrate_difficulty(
        db: AsyncIOMotorDatabase,
        question_id: str
    ) -> str:
        """Recalibrate question difficulty based on empirical data."""
        # Get question stats
        stats = await db.question_statistics.find_one({"question_id": question_id})

        if not stats or stats.get("total_attempts", 0) < 10:
            return "Insufficient data"

        # Calculate empirical success rate
        success_rate = stats.get("empirical_difficulty", 0.5)

        # Determine difficulty from success rate
        if success_rate >= 0.75:
            new_difficulty = "Easy"
        elif success_rate >= 0.5:
            new_difficulty = "Medium"
        elif success_rate >= 0.25:
            new_difficulty = "Hard"
        else:
            new_difficulty = "Tricky"

        # Update question
        await db.questions.update_one(
            {"_id": ObjectId(question_id)},
            {"$set": {"difficulty": new_difficulty}}
        )

        return new_difficulty

    @staticmethod
    async def bulk_import_questions(
        db: AsyncIOMotorDatabase,
        questions_data: List[Dict],
        document_id: str
    ) -> int:
        """Bulk import questions from CSV/JSON."""
        from datetime import datetime

        # Validate and prepare questions
        valid_questions = []
        for q_data in questions_data:
            # Basic validation
            if "question_text" not in q_data or "correct_answer" not in q_data:
                continue

            question = {
                "document_id": document_id,
                "question_type": q_data.get("question_type", "Short Answer"),
                "difficulty": q_data.get("difficulty", "Medium"),
                "topic": q_data.get("topic", "General"),
                "question_text": q_data["question_text"],
                "correct_answer": q_data["correct_answer"],
                "explanation": q_data.get("explanation", ""),
                "options": q_data.get("options", []),
                "source_section": q_data.get("source_section", ""),
                "created_at": datetime.utcnow(),
                "manually_created": True
            }

            valid_questions.append(question)

        if valid_questions:
            result = await db.questions.insert_many(valid_questions)
            return len(result.inserted_ids)

        return 0

    @staticmethod
    async def export_questions(
        db: AsyncIOMotorDatabase,
        document_id: str
    ) -> List[Dict]:
        """Export all questions for a document."""
        cursor = db.questions.find({"document_id": document_id})
        questions = await cursor.to_list(length=10000)

        # Prepare export format
        export_data = []
        for q in questions:
            export_data.append({
                "question_id": str(q["_id"]),
                "topic": q.get("topic"),
                "difficulty": q.get("difficulty"),
                "question_type": q.get("question_type"),
                "question_text": q.get("question_text"),
                "options": q.get("options", []),
                "correct_answer": q.get("correct_answer"),
                "explanation": q.get("explanation"),
                "source_section": q.get("source_section")
            })

        return export_data
