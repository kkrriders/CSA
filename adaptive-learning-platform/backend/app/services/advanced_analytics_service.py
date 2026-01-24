"""
Advanced Analytics - World-Class Features

1. Learning Velocity - "You learn CNNs 3× faster than Transformers"
2. Forgetting Curve - Detect mastery decay
3. Exam Readiness - "You are 72% ready"
4. Behavior Fingerprint - Deep personality profiling
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import math
import statistics

from bson import ObjectId
from app.models.analytics import (
    LearningVelocity,
    ForgettingCurveData,
    ExamReadinessScore,
    BehaviorFingerprint,
    BehavioralSignals,
    TopicMastery
)


class AdvancedAnalyticsService:
    """World-class analytics features"""

    # ============================================================
    # 1. LEARNING VELOCITY
    # ============================================================

    @staticmethod
    async def calculate_learning_velocity(
        user_id: str,
        topic: str,
        db
    ) -> LearningVelocity:
        """
        Track how fast a topic improves per session

        Returns: "You learn CNNs 3× faster than Transformers"
        """

        # Get all sessions for this user, ordered by date
        sessions = await db.test_sessions.find({
            "user_id": ObjectId(user_id),
            "status": "completed"
        }).sort("completed_at", 1).to_list(length=100)

        # Calculate mastery for this topic in each session
        mastery_trajectory = []

        for session in sessions:
            # Calculate topic mastery for this session
            topic_stats = {"correct": 0, "total": 0}

            # Get questions for this session
            question_ids = [ObjectId(qid) for qid in session["questions"]]
            questions = await db.questions.find({
                "_id": {"$in": question_ids},
                "topic": topic
            }).to_list(length=1000)

            question_id_set = {str(q["_id"]) for q in questions}

            # Count correct answers for this topic
            for answer in session["answers"]:
                if answer["question_id"] in question_id_set:
                    topic_stats["total"] += 1
                    if answer.get("status") == "correct":
                        topic_stats["correct"] += 1

            if topic_stats["total"] > 0:
                mastery = topic_stats["correct"] / topic_stats["total"]
                mastery_trajectory.append(mastery)

        if len(mastery_trajectory) < 2:
            return LearningVelocity(
                topic=topic,
                sessions_analyzed=len(mastery_trajectory),
                mastery_trajectory=mastery_trajectory,
                velocity=0.0,
                acceleration=0.0,
                sessions_to_mastery=None,
                comparative_rank=None
            )

        # Calculate velocity (linear regression slope)
        velocity = AdvancedAnalyticsService._calculate_slope(mastery_trajectory)

        # Calculate acceleration (change in velocity)
        if len(mastery_trajectory) >= 4:
            first_half = mastery_trajectory[:len(mastery_trajectory)//2]
            second_half = mastery_trajectory[len(mastery_trajectory)//2:]
            velocity_first = AdvancedAnalyticsService._calculate_slope(first_half)
            velocity_second = AdvancedAnalyticsService._calculate_slope(second_half)
            acceleration = velocity_second - velocity_first
        else:
            acceleration = 0.0

        # Predict sessions to mastery (0.9 threshold)
        current_mastery = mastery_trajectory[-1]
        if velocity > 0 and current_mastery < 0.9:
            sessions_needed = math.ceil((0.9 - current_mastery) / velocity)
            sessions_to_mastery = max(1, sessions_needed)
        else:
            sessions_to_mastery = None

        return LearningVelocity(
            topic=topic,
            sessions_analyzed=len(mastery_trajectory),
            mastery_trajectory=mastery_trajectory,
            velocity=velocity,
            acceleration=acceleration,
            sessions_to_mastery=sessions_to_mastery,
            comparative_rank=None  # Will be computed by comparison
        )

    @staticmethod
    async def compare_learning_velocities(
        user_id: str,
        db
    ) -> List[LearningVelocity]:
        """
        Compare learning velocities across topics

        Returns: "You learn CNNs 3× faster than Transformers"
        """

        # Get all topics for this user
        sessions = await db.test_sessions.find({
            "user_id": ObjectId(user_id),
            "status": "completed"
        }).to_list(length=100)

        topics = set()
        for session in sessions:
            question_ids = [ObjectId(qid) for qid in session["questions"]]
            questions = await db.questions.find({
                "_id": {"$in": question_ids}
            }).to_list(length=1000)
            topics.update(q["topic"] for q in questions)

        # Calculate velocity for each topic
        velocities = []
        for topic in topics:
            velocity_data = await AdvancedAnalyticsService.calculate_learning_velocity(
                user_id, topic, db
            )
            velocities.append(velocity_data)

        # Sort by velocity (fastest learners first)
        velocities.sort(key=lambda v: v.velocity, reverse=True)

        # Add comparative ranks
        if len(velocities) > 1:
            fastest = velocities[0]
            for i, v in enumerate(velocities):
                if i == 0:
                    v.comparative_rank = "Fastest learning topic"
                elif v.velocity > 0:
                    ratio = fastest.velocity / v.velocity
                    v.comparative_rank = f"{ratio:.1f}× slower than {fastest.topic}"

        return velocities

    @staticmethod
    def _calculate_slope(values: List[float]) -> float:
        """Calculate linear regression slope"""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = list(range(n))
        y = values

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    # ============================================================
    # 2. FORGETTING CURVE
    # ============================================================

    @staticmethod
    async def detect_forgetting_curve(
        user_id: str,
        topic: str,
        db
    ) -> ForgettingCurveData:
        """
        Detect if mastery has decayed over time

        Uses Ebbinghaus forgetting curve: R = e^(-t/S)
        Where R = retention, t = time, S = stability
        """

        # Get all sessions for this user, ordered by date
        sessions = await db.test_sessions.find({
            "user_id": ObjectId(user_id),
            "status": "completed"
        }).sort("completed_at", 1).to_list(length=100)

        mastery_by_date = []

        for session in sessions:
            # Get topic mastery for this session
            topic_stats = {"correct": 0, "total": 0}

            question_ids = [ObjectId(qid) for qid in session["questions"]]
            questions = await db.questions.find({
                "_id": {"$in": question_ids},
                "topic": topic
            }).to_list(length=1000)

            question_id_set = {str(q["_id"]) for q in questions}

            for answer in session["answers"]:
                if answer["question_id"] in question_id_set:
                    topic_stats["total"] += 1
                    if answer.get("status") == "correct":
                        topic_stats["correct"] += 1

            if topic_stats["total"] > 0:
                mastery = topic_stats["correct"] / topic_stats["total"]
                mastery_by_date.append({
                    "mastery": mastery,
                    "date": session["completed_at"]
                })

        if not mastery_by_date:
            return ForgettingCurveData(
                topic=topic,
                peak_mastery=0.0,
                peak_date=datetime.utcnow(),
                current_mastery=0.0,
                days_since_peak=0,
                decay_rate=0.0,
                half_life_days=None,
                needs_review=False
            )

        # Find peak mastery
        peak_entry = max(mastery_by_date, key=lambda x: x["mastery"])
        peak_mastery = peak_entry["mastery"]
        peak_date = peak_entry["date"]

        # Current mastery (most recent)
        current_mastery = mastery_by_date[-1]["mastery"]
        current_date = mastery_by_date[-1]["date"]

        days_since_peak = (current_date - peak_date).days

        # Calculate decay rate
        if days_since_peak > 0 and peak_mastery > 0:
            # R = e^(-t/S) => ln(R) = -t/S => S = -t/ln(R)
            retention_ratio = current_mastery / peak_mastery
            if retention_ratio > 0:
                # Decay rate per day
                decay_rate = -math.log(retention_ratio) / days_since_peak

                # Half-life: time for mastery to halve
                half_life_days = math.log(2) / decay_rate if decay_rate > 0 else None
            else:
                decay_rate = 1.0  # Complete decay
                half_life_days = 0
        else:
            decay_rate = 0.0
            half_life_days = None

        # Needs review if: dropped >20% from peak and was previously good
        needs_review = (
            peak_mastery > 0.7 and
            current_mastery < peak_mastery * 0.8 and
            days_since_peak >= 7
        )

        return ForgettingCurveData(
            topic=topic,
            peak_mastery=peak_mastery,
            peak_date=peak_date,
            current_mastery=current_mastery,
            days_since_peak=days_since_peak,
            decay_rate=decay_rate,
            half_life_days=half_life_days,
            needs_review=needs_review
        )

    # ============================================================
    # 3. EXAM READINESS SCORE
    # ============================================================

    @staticmethod
    async def calculate_exam_readiness(
        user_id: str,
        document_id: str,
        db
    ) -> ExamReadinessScore:
        """
        Holistic exam readiness score

        Returns: "You are 72% ready for this exam"
        """

        # Get all completed sessions for this document
        sessions = await db.test_sessions.find({
            "user_id": ObjectId(user_id),
            "document_id": ObjectId(document_id),
            "status": "completed"
        }).to_list(length=100)

        if not sessions:
            return AdvancedAnalyticsService._default_readiness()

        # Get all topics in document
        all_questions = await db.questions.find({
            "document_id": ObjectId(document_id)
        }).to_list(length=10000)

        all_topics = set(q["topic"] for q in all_questions)

        # Calculate topic masteries
        topic_masteries = {}
        topic_variances = {}

        for topic in all_topics:
            mastery_values = []

            for session in sessions:
                topic_stats = {"correct": 0, "total": 0}

                question_ids = [ObjectId(qid) for qid in session["questions"]]
                questions = await db.questions.find({
                    "_id": {"$in": question_ids},
                    "topic": topic
                }).to_list(length=1000)

                question_id_set = {str(q["_id"]) for q in questions}

                for answer in session["answers"]:
                    if answer["question_id"] in question_id_set:
                        topic_stats["total"] += 1
                        if answer.get("status") == "correct":
                            topic_stats["correct"] += 1

                if topic_stats["total"] > 0:
                    mastery = topic_stats["correct"] / topic_stats["total"]
                    mastery_values.append(mastery)

            if mastery_values:
                topic_masteries[topic] = statistics.mean(mastery_values)
                topic_variances[topic] = statistics.variance(mastery_values) if len(mastery_values) > 1 else 0
            else:
                topic_masteries[topic] = 0.0
                topic_variances[topic] = 0.0

        # 1. MASTERY SCORE (40% weight)
        mastery_score = statistics.mean(topic_masteries.values()) if topic_masteries else 0

        # 2. CONSISTENCY SCORE (25% weight)
        # Low variance = high consistency
        avg_variance = statistics.mean(topic_variances.values()) if topic_variances else 0
        consistency_score = max(0, 1 - avg_variance * 2)  # Normalize variance

        # 3. CONFIDENCE SCORE (20% weight)
        # Based on hesitation and speed
        total_hesitation = 0
        total_answers = 0

        for session in sessions:
            for answer in session["answers"]:
                if answer.get("status") in ["correct", "wrong"]:
                    total_answers += 1
                    total_hesitation += answer.get("hesitation_count", 0)

        avg_hesitation = total_hesitation / total_answers if total_answers > 0 else 0
        confidence_score = max(0, 1 - avg_hesitation * 0.2)

        # 4. COVERAGE SCORE (15% weight)
        practiced_topics = sum(1 for m in topic_masteries.values() if m > 0)
        coverage_score = practiced_topics / len(all_topics) if all_topics else 0

        # OVERALL SCORE (weighted average)
        overall_score = (
            mastery_score * 0.40 +
            consistency_score * 0.25 +
            confidence_score * 0.20 +
            coverage_score * 0.15
        ) * 100

        # Categorize topics
        strong_topics = [t for t, m in topic_masteries.items() if m > 0.8]
        weak_topics = [t for t, m in topic_masteries.items() if m < 0.5]
        inconsistent_topics = [t for t, v in topic_variances.items() if v > 0.1]

        # Readiness level
        if overall_score >= 85:
            readiness_level = "Ready"
        elif overall_score >= 70:
            readiness_level = "Almost Ready"
        else:
            readiness_level = "Needs Work"

        # Estimate study hours to reach 90%
        score_gap = max(0, 90 - overall_score)
        estimated_study_hours = int(score_gap * 0.5)  # ~30min per % point

        # Priority actions
        priority_actions = []
        if weak_topics:
            priority_actions.append(f"Focus on weak topics: {', '.join(weak_topics[:3])}")
        if inconsistent_topics:
            priority_actions.append(f"Practice inconsistent topics: {', '.join(inconsistent_topics[:2])}")
        if coverage_score < 0.8:
            priority_actions.append("Cover more topics to improve breadth")
        if confidence_score < 0.7:
            priority_actions.append("Build confidence: practice under time pressure")

        return ExamReadinessScore(
            overall_score=round(overall_score, 1),
            mastery_score=round(mastery_score * 100, 1),
            consistency_score=round(consistency_score * 100, 1),
            confidence_score=round(confidence_score * 100, 1),
            coverage_score=round(coverage_score * 100, 1),
            strong_topics=strong_topics,
            weak_topics=weak_topics,
            inconsistent_topics=inconsistent_topics,
            estimated_study_hours=estimated_study_hours,
            priority_actions=priority_actions,
            readiness_level=readiness_level
        )

    @staticmethod
    def _default_readiness() -> ExamReadinessScore:
        return ExamReadinessScore(
            overall_score=0,
            mastery_score=0,
            consistency_score=0,
            confidence_score=0,
            coverage_score=0,
            strong_topics=[],
            weak_topics=[],
            inconsistent_topics=[],
            estimated_study_hours=20,
            priority_actions=["Complete at least one practice test"],
            readiness_level="Not Started"
        )

    # ============================================================
    # 4. BEHAVIOR FINGERPRINT
    # ============================================================

    @staticmethod
    async def generate_behavior_fingerprint(
        user_id: str,
        signals: List[BehavioralSignals],
        db
    ) -> BehaviorFingerprint:
        """
        Deep personality profiling

        Traits: risk-taker, perfectionist, skimmer, grinder
        """

        if not signals:
            return AdvancedAnalyticsService._default_fingerprint(user_id)

        answered = [s for s in signals if s.answered]
        total = len(signals)

        if not answered:
            return AdvancedAnalyticsService._default_fingerprint(user_id)

        # === CORE TRAITS (0-1 scale) ===

        # 1. RISK TAKING: Answers fast even when uncertain
        fast_count = sum(1 for s in answered if s.time_spent < 20)
        fast_rate = fast_count / len(answered)
        fast_accuracy = sum(1 for s in answered if s.time_spent < 20 and s.correct) / fast_count if fast_count > 0 else 0
        # High risk = high fast rate, even if accuracy suffers
        risk_taking = fast_rate * (1 + (1 - fast_accuracy) * 0.5)
        risk_taking = min(1.0, risk_taking)

        # 2. PERFECTIONISM: Slow, changes answers, marks tricky
        avg_hesitation = sum(s.hesitation_count for s in answered) / len(answered)
        marked_rate = sum(1 for s in answered if s.marked_tricky) / len(answered)
        slow_rate = sum(1 for s in answered if s.time_spent > 60) / len(answered)
        perfectionism = (avg_hesitation * 0.3 + marked_rate * 0.4 + slow_rate * 0.3)
        perfectionism = min(1.0, perfectionism)

        # 3. SKIMMING: Fast, skips hard questions
        skip_rate = (total - len(answered)) / total
        hard_skips = sum(1 for s in signals if not s.answered and s.empirical_difficulty < 0.3)
        hard_skip_rate = hard_skips / (total - len(answered)) if (total - len(answered)) > 0 else 0
        skimming = (skip_rate * 0.6 + hard_skip_rate * 0.4)
        skimming = min(1.0, skimming)

        # 4. GRINDING: Slow but thorough, high accuracy
        accuracy = sum(1 for s in answered if s.correct) / len(answered)
        slow_accurate = sum(1 for s in answered if s.time_spent > 60 and s.correct) / len(answered)
        grinding = slow_rate * accuracy
        grinding = min(1.0, grinding)

        # === DETAILED METRICS ===

        # Confidence calibration: Are they confident when correct?
        fast_correct = sum(1 for s in answered if s.time_spent < 30 and s.correct)
        slow_wrong = sum(1 for s in answered if s.time_spent > 60 and not s.correct)
        confidence_calibration = (fast_correct - slow_wrong) / len(answered)
        confidence_calibration = max(0, min(1, (confidence_calibration + 1) / 2))  # Normalize to 0-1

        # Speed-accuracy tradeoff
        avg_time = sum(s.time_spent for s in answered) / len(answered)
        # -1 (slow accurate) to +1 (fast sloppy)
        speed_norm = (avg_time - 45) / 45  # Normalize around 45s
        accuracy_norm = (accuracy - 0.5) / 0.5  # Normalize around 50%
        speed_accuracy_tradeoff = speed_norm - accuracy_norm
        speed_accuracy_tradeoff = max(-1, min(1, speed_accuracy_tradeoff))

        # Difficulty seeking
        hard_attempts = sum(1 for s in answered if s.empirical_difficulty < 0.3)
        easy_skips = sum(1 for s in signals if not s.answered and s.empirical_difficulty > 0.7)
        difficulty_seeking = (hard_attempts - easy_skips) / total
        difficulty_seeking = max(0, min(1, (difficulty_seeking + 1) / 2))

        # Consistency (from historical sessions)
        # TODO: Calculate variance across sessions
        consistency = 0.7  # Placeholder

        # === PRIMARY TRAIT ===
        traits = {
            "Risk-taker": risk_taking,
            "Perfectionist": perfectionism,
            "Skimmer": skimming,
            "Grinder": grinding
        }
        sorted_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)
        primary_trait = sorted_traits[0][0]
        secondary_trait = sorted_traits[1][0] if sorted_traits[1][1] > 0.3 else None

        # === COACHING RECOMMENDATIONS ===
        strengths = []
        growth_areas = []

        if risk_taking > 0.6:
            strengths.append("Bold decision-making under time pressure")
            growth_areas.append("Slow down on complex questions")

        if perfectionism > 0.6:
            strengths.append("Attention to detail and accuracy")
            growth_areas.append("Trust your first instinct more")

        if grinding > 0.6:
            strengths.append("Thorough understanding of concepts")
            strengths.append("High accuracy through persistence")

        if skimming > 0.6:
            growth_areas.append("Engage with difficult material")
            growth_areas.append("Build tolerance for challenging problems")

        if accuracy > 0.8:
            strengths.append("Strong foundational knowledge")

        # Optimal strategy
        if primary_trait == "Risk-taker":
            optimal_strategy = "Use timed practice to channel your speed advantage. Review mistakes to improve accuracy."
        elif primary_trait == "Perfectionist":
            optimal_strategy = "Set time limits to prevent overthinking. Practice trusting your preparation."
        elif primary_trait == "Grinder":
            optimal_strategy = "Your persistence is your strength. Focus on efficiency to maximize coverage."
        else:  # Skimmer
            optimal_strategy = "Build stamina for difficult topics. Start with moderate difficulty, then increase."

        return BehaviorFingerprint(
            user_id=user_id,
            risk_taking=round(risk_taking, 2),
            perfectionism=round(perfectionism, 2),
            skimming=round(skimming, 2),
            grinding=round(grinding, 2),
            confidence_calibration=round(confidence_calibration, 2),
            speed_accuracy_tradeoff=round(speed_accuracy_tradeoff, 2),
            difficulty_seeking=round(difficulty_seeking, 2),
            consistency=round(consistency, 2),
            primary_trait=primary_trait,
            secondary_trait=secondary_trait,
            strengths=strengths,
            growth_areas=growth_areas,
            optimal_study_strategy=optimal_strategy
        )

    @staticmethod
    def _default_fingerprint(user_id: str) -> BehaviorFingerprint:
        return BehaviorFingerprint(
            user_id=user_id,
            risk_taking=0.5,
            perfectionism=0.5,
            skimming=0.5,
            grinding=0.5,
            confidence_calibration=0.5,
            speed_accuracy_tradeoff=0.0,
            difficulty_seeking=0.5,
            consistency=0.5,
            primary_trait="Developing",
            secondary_trait=None,
            strengths=["Building foundation"],
            growth_areas=["Complete more tests for analysis"],
            optimal_study_strategy="Focus on consistent practice"
        )
