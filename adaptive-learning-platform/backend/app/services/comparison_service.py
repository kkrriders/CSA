"""
Performance comparison and ranking service.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import statistics


class ComparisonService:
    """Service for performance comparisons and rankings."""

    @staticmethod
    async def calculate_percentile_ranking(
        db: AsyncIOMotorDatabase,
        user_id: str,
        document_id: str
    ) -> Dict:
        """Calculate user's percentile ranking for a document."""
        # Get all users who completed tests on this document
        all_sessions = await db.test_sessions.find({
            "document_id": document_id,
            "status": "completed"
        }).to_list(length=10000)

        if len(all_sessions) < 5:
            return {
                "message": "Not enough data for ranking",
                "percentile": None
            }

        # Calculate average score per user
        user_scores = {}
        for session in all_sessions:
            uid = str(session["user_id"])
            score = session.get("score", 0)

            if uid not in user_scores:
                user_scores[uid] = []
            user_scores[uid].append(score)

        # Average scores
        avg_scores = {uid: statistics.mean(scores) for uid, scores in user_scores.items()}

        # Calculate percentile
        user_avg = avg_scores.get(user_id, 0)
        below = sum(1 for s in avg_scores.values() if s < user_avg)
        percentile = (below / len(avg_scores)) * 100

        # Ranking
        sorted_users = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        rank = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id), None)

        return {
            "percentile": round(percentile, 1),
            "rank": rank,
            "total_users": len(avg_scores),
            "user_average_score": round(user_avg, 1),
            "top_score": max(avg_scores.values()),
            "median_score": statistics.median(avg_scores.values())
        }

    @staticmethod
    async def get_peer_comparison(
        db: AsyncIOMotorDatabase,
        user_id: str,
        document_id: str
    ) -> Dict:
        """Get anonymized peer comparison."""
        # Get user's sessions
        user_sessions = await db.test_sessions.find({
            "user_id": user_id,
            "document_id": document_id,
            "status": "completed"
        }).to_list(length=1000)

        if not user_sessions:
            return {"message": "No completed sessions found"}

        # Get peer sessions (exclude current user)
        peer_sessions = await db.test_sessions.find({
            "document_id": document_id,
            "user_id": {"$ne": user_id},
            "status": "completed"
        }).to_list(length=10000)

        if not peer_sessions:
            return {"message": "No peer data available"}

        # Calculate user stats
        user_scores = [s.get("score", 0) for s in user_sessions]
        user_times = [s.get("total_time", 0) for s in user_sessions]

        # Calculate peer stats
        peer_scores = [s.get("score", 0) for s in peer_sessions]
        peer_times = [s.get("total_time", 0) for s in peer_sessions]

        return {
            "your_stats": {
                "average_score": round(statistics.mean(user_scores), 1),
                "average_time": round(statistics.mean(user_times)),
                "sessions_count": len(user_sessions)
            },
            "peer_stats": {
                "average_score": round(statistics.mean(peer_scores), 1),
                "median_score": round(statistics.median(peer_scores), 1),
                "top_25_percent": round(statistics.quantiles(peer_scores, n=4)[2], 1),
                "average_time": round(statistics.mean(peer_times)),
                "total_peers": len(set(str(s["user_id"]) for s in peer_sessions))
            },
            "comparison": {
                "score_vs_average": round(statistics.mean(user_scores) - statistics.mean(peer_scores), 1),
                "score_vs_median": round(statistics.mean(user_scores) - statistics.median(peer_scores), 1)
            }
        }

    @staticmethod
    async def get_historical_comparison(
        db: AsyncIOMotorDatabase,
        user_id: str,
        document_id: Optional[str] = None
    ) -> Dict:
        """Compare current performance vs historical (30/60/90 days ago)."""
        now = datetime.utcnow()
        periods = [
            ("last_7_days", now - timedelta(days=7), now),
            ("last_30_days", now - timedelta(days=30), now - timedelta(days=7)),
            ("last_90_days", now - timedelta(days=90), now - timedelta(days=30)),
        ]

        results = {}

        for period_name, start, end in periods:
            query = {
                "user_id": user_id,
                "completed_at": {"$gte": start, "$lt": end},
                "status": "completed"
            }

            if document_id:
                query["document_id"] = document_id

            sessions = await db.test_sessions.find(query).to_list(length=1000)

            if sessions:
                scores = [s.get("score", 0) for s in sessions]
                results[period_name] = {
                    "sessions_count": len(sessions),
                    "average_score": round(statistics.mean(scores), 1),
                    "best_score": max(scores),
                    "improvement": None  # Calculated later
                }
            else:
                results[period_name] = None

        # Calculate improvements
        if results["last_7_days"] and results["last_30_days"]:
            results["last_7_days"]["improvement"] = round(
                results["last_7_days"]["average_score"] - results["last_30_days"]["average_score"],
                1
            )

        if results["last_30_days"] and results["last_90_days"]:
            results["last_30_days"]["improvement"] = round(
                results["last_30_days"]["average_score"] - results["last_90_days"]["average_score"],
                1
            )

        return results

    @staticmethod
    async def get_cohort_stats(
        db: AsyncIOMotorDatabase,
        document_id: str
    ) -> Dict:
        """Get aggregate cohort statistics for a document."""
        # Get all completed sessions
        sessions = await db.test_sessions.find({
            "document_id": document_id,
            "status": "completed"
        }).to_list(length=10000)

        if not sessions:
            return {"message": "No data available"}

        scores = [s.get("score", 0) for s in sessions]
        times = [s.get("total_time", 0) for s in sessions]

        # Get unique users
        unique_users = len(set(str(s["user_id"]) for s in sessions))

        # Score distribution
        score_ranges = {
            "90-100": sum(1 for s in scores if s >= 90),
            "80-89": sum(1 for s in scores if 80 <= s < 90),
            "70-79": sum(1 for s in scores if 70 <= s < 80),
            "60-69": sum(1 for s in scores if 60 <= s < 70),
            "below_60": sum(1 for s in scores if s < 60)
        }

        return {
            "total_sessions": len(sessions),
            "unique_users": unique_users,
            "score_stats": {
                "mean": round(statistics.mean(scores), 1),
                "median": round(statistics.median(scores), 1),
                "std_dev": round(statistics.stdev(scores), 1) if len(scores) > 1 else 0,
                "min": min(scores),
                "max": max(scores),
                "distribution": score_ranges
            },
            "time_stats": {
                "mean_minutes": round(statistics.mean(times) / 60, 1),
                "median_minutes": round(statistics.median(times) / 60, 1),
            }
        }
