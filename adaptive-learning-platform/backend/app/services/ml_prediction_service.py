"""
Machine learning prediction service.
"""
from typing import Dict, List
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import statistics


class MLPredictionService:
    """Service for ML-based predictions."""

    @staticmethod
    async def predict_success(
        db: AsyncIOMotorDatabase,
        user_id: str,
        topic: str
    ) -> Dict:
        """Predict probability of success on a topic."""
        # Get historical performance on this topic
        sessions = await db.test_sessions.find({
            "user_id": user_id,
            "status": "completed"
        }).to_list(length=1000)

        if not sessions:
            return {"probability": 0.5, "confidence": "low"}

        # Extract topic performance
        topic_scores = []
        for session in sessions:
            topic_answers = [
                ans for ans in session.get("answers", [])
                if ans.get("topic") == topic
            ]

            if topic_answers:
                correct = sum(1 for ans in topic_answers if ans.get("correct", False))
                score = (correct / len(topic_answers)) * 100
                topic_scores.append(score)

        if not topic_scores:
            return {"probability": 0.5, "confidence": "low"}

        # Simple probability based on average score
        avg_score = statistics.mean(topic_scores)
        probability = avg_score / 100

        # Calculate trend
        recent_scores = topic_scores[-3:] if len(topic_scores) >= 3 else topic_scores
        is_improving = all(recent_scores[i] <= recent_scores[i+1] for i in range(len(recent_scores)-1))

        # Adjust probability based on trend
        if is_improving:
            probability = min(1.0, probability * 1.1)

        confidence = "high" if len(topic_scores) >= 5 else "medium" if len(topic_scores) >= 2 else "low"

        return {
            "probability": round(probability, 2),
            "confidence": confidence,
            "avg_score": round(avg_score, 1),
            "attempts": len(topic_scores),
            "trend": "improving" if is_improving else "stable"
        }

    @staticmethod
    async def detect_burnout(
        db: AsyncIOMotorDatabase,
        user_id: str
    ) -> Dict:
        """Detect signs of burnout from behavioral patterns."""
        # Get recent sessions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sessions = await db.test_sessions.find({
            "user_id": user_id,
            "completed_at": {"$gte": thirty_days_ago},
            "status": "completed"
        }).sort("completed_at", 1).to_list(length=1000)

        if len(sessions) < 5:
            return {"risk": "unknown", "indicators": []}

        # Calculate burnout indicators
        indicators = []
        risk_score = 0

        # 1. Declining performance
        scores = [s.get("score", 0) for s in sessions]
        if len(scores) >= 5:
            recent_avg = statistics.mean(scores[-5:])
            older_avg = statistics.mean(scores[:-5])

            if recent_avg < older_avg - 10:
                indicators.append("Declining performance trend")
                risk_score += 2

        # 2. Increased session frequency without improvement
        daily_counts = {}
        for session in sessions:
            date = session["completed_at"].date()
            daily_counts[date] = daily_counts.get(date, 0) + 1

        if max(daily_counts.values()) > 5:
            indicators.append("Very high session frequency")
            risk_score += 1

        # 3. Increasing time per question without accuracy improvement
        avg_times = [s.get("total_time", 0) / len(s.get("answers", [1])) for s in sessions]
        if len(avg_times) >= 5:
            if avg_times[-1] > statistics.mean(avg_times[:-1]) * 1.5:
                indicators.append("Increased hesitation/time per question")
                risk_score += 1

        # 4. High skip rate
        recent_sessions = sessions[-5:]
        total_questions = sum(len(s.get("answers", [])) for s in recent_sessions)
        skipped = sum(
            sum(1 for ans in s.get("answers", []) if not ans.get("answered", True))
            for s in recent_sessions
        )

        if total_questions > 0 and (skipped / total_questions) > 0.3:
            indicators.append("High question skip rate")
            risk_score += 1

        # Determine risk level
        if risk_score >= 4:
            risk = "high"
        elif risk_score >= 2:
            risk = "medium"
        else:
            risk = "low"

        return {
            "risk": risk,
            "risk_score": risk_score,
            "indicators": indicators,
            "recommendation": "Consider taking a break" if risk in ["high", "medium"] else "Keep up the good work"
        }

    @staticmethod
    async def recommend_next_difficulty(
        db: AsyncIOMotorDatabase,
        user_id: str,
        topic: str
    ) -> str:
        """Recommend optimal difficulty level for next session."""
        # Get recent performance on this topic
        sessions = await db.test_sessions.find({
            "user_id": user_id,
            "status": "completed"
        }).sort("completed_at", -1).limit(5).to_list(length=5)

        if not sessions:
            return "Easy"  # Start with easy for new users

        # Analyze difficulty performance
        difficulty_scores = {"Easy": [], "Medium": [], "Hard": [], "Tricky": []}

        for session in sessions:
            for ans in session.get("answers", []):
                if ans.get("topic") == topic:
                    difficulty = ans.get("difficulty", "Medium")
                    correct = ans.get("correct", False)
                    difficulty_scores[difficulty].append(1 if correct else 0)

        # Calculate success rates
        success_rates = {}
        for diff, scores in difficulty_scores.items():
            if scores:
                success_rates[diff] = statistics.mean(scores)

        # Recommendation logic
        if success_rates.get("Easy", 0) < 0.7:
            return "Easy"
        elif success_rates.get("Medium", 0) < 0.6:
            return "Medium"
        elif success_rates.get("Hard", 0) < 0.5:
            return "Hard"
        else:
            return "Tricky"
