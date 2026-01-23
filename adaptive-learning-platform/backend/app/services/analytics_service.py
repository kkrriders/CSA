from typing import List, Dict
from collections import defaultdict
from app.models.test_session import QuestionAnswer, AnswerStatus
from app.models.analytics import (
    FailurePattern,
    TopicMastery,
    WeaknessAnalysis,
    AdaptiveTargeting
)


class AnalyticsService:
    """AI-powered analytics for pattern detection and cognitive profiling"""

    @staticmethod
    def detect_answer_patterns(answers: List[QuestionAnswer]) -> Dict[str, List[str]]:
        """Detect cognitive patterns from answer data"""
        patterns = {
            "fast_wrong": [],
            "slow_wrong": [],
            "easy_wrong": [],
            "tricky_wrong": [],
            "high_confidence_mistakes": []
        }

        for answer in answers:
            if answer.status == AnswerStatus.WRONG:
                question_id = answer.question_id

                # Fast wrong: < 30 seconds (likely guessed)
                if answer.time_taken < 30:
                    patterns["fast_wrong"].append(question_id)
                    answer.answer_speed = "fast"
                    answer.confidence_signal = "guessed"

                # Slow wrong: > 60 seconds (confused/struggled)
                elif answer.time_taken > 60:
                    patterns["slow_wrong"].append(question_id)
                    answer.answer_speed = "slow"
                    answer.confidence_signal = "confused"

                else:
                    answer.answer_speed = "medium"
                    answer.confidence_signal = "uncertain"

                # Marked tricky + wrong = high priority
                if answer.marked_tricky:
                    patterns["tricky_wrong"].append(question_id)

        return patterns

    @staticmethod
    def calculate_topic_mastery(
        answers: List[QuestionAnswer],
        questions_data: List[Dict]
    ) -> List[TopicMastery]:
        """Calculate mastery level for each topic"""

        topic_stats = defaultdict(lambda: {
            "total": 0,
            "correct": 0,
            "wrong": 0,
            "total_time": 0,
            "difficulties": defaultdict(lambda: {"correct": 0, "wrong": 0})
        })

        # Build question lookup
        question_lookup = {q["_id"]: q for q in questions_data}

        for answer in answers:
            if answer.status in [AnswerStatus.CORRECT, AnswerStatus.WRONG]:
                question = question_lookup.get(answer.question_id)
                if not question:
                    continue

                topic = question.get("topic", "Unknown")
                difficulty = question.get("difficulty", "medium")

                stats = topic_stats[topic]
                stats["total"] += 1
                stats["total_time"] += answer.time_taken

                if answer.status == AnswerStatus.CORRECT:
                    stats["correct"] += 1
                    stats["difficulties"][difficulty]["correct"] += 1
                else:
                    stats["wrong"] += 1
                    stats["difficulties"][difficulty]["wrong"] += 1

        # Convert to TopicMastery objects
        mastery_list = []
        for topic, stats in topic_stats.items():
            mastery_pct = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            avg_time = stats["total_time"] / stats["total"] if stats["total"] > 0 else 0

            mastery_list.append(TopicMastery(
                topic=topic,
                total_attempts=stats["total"],
                correct_attempts=stats["correct"],
                wrong_attempts=stats["wrong"],
                mastery_percentage=round(mastery_pct, 2),
                avg_time_taken=round(avg_time, 2),
                difficulty_breakdown=dict(stats["difficulties"])
            ))

        return sorted(mastery_list, key=lambda x: x.mastery_percentage)

    @staticmethod
    def identify_weakness_areas(
        topic_mastery: List[TopicMastery],
        patterns: Dict[str, List[str]],
        questions_data: List[Dict]
    ) -> List[WeaknessAnalysis]:
        """Identify and prioritize weakness areas"""

        weaknesses = []
        question_lookup = {q["_id"]: q for q in questions_data}

        for mastery in topic_mastery:
            if mastery.mastery_percentage < 70:  # Below 70% = weakness
                topic = mastery.topic

                # Find questions for this topic
                topic_questions = [
                    q_id for q_id, q in question_lookup.items()
                    if q.get("topic") == topic
                ]

                # Identify failure patterns
                failure_patterns = []
                priority_score = 0

                # Check pattern presence
                fast_wrong_count = len([q for q in topic_questions if q in patterns["fast_wrong"]])
                slow_wrong_count = len([q for q in topic_questions if q in patterns["slow_wrong"]])
                tricky_wrong_count = len([q for q in topic_questions if q in patterns["tricky_wrong"]])

                if fast_wrong_count > 0:
                    failure_patterns.append(FailurePattern.FAST_WRONG)
                    priority_score += fast_wrong_count * 1

                if slow_wrong_count > 0:
                    failure_patterns.append(FailurePattern.SLOW_WRONG)
                    priority_score += slow_wrong_count * 2  # Confusion is worse than guessing

                if tricky_wrong_count > 0:
                    failure_patterns.append(FailurePattern.TRICKY_WRONG)
                    priority_score += tricky_wrong_count * 3  # High priority

                # Check for easy questions failed (dangerous gap)
                easy_failed = [
                    q_id for q_id in topic_questions
                    if question_lookup[q_id].get("difficulty") == "easy" and q_id in patterns.get("fast_wrong", []) + patterns.get("slow_wrong", [])
                ]
                if easy_failed:
                    failure_patterns.append(FailurePattern.EASY_WRONG)
                    priority_score += len(easy_failed) * 4  # Critical

                # Check for repeated failures
                if mastery.wrong_attempts >= 3:
                    failure_patterns.append(FailurePattern.REPEATED_TOPIC)
                    priority_score += 2

                # Calculate final priority (0-100)
                priority_score = min(100, priority_score * 10)

                # Generate recommendation
                recommendation = AnalyticsService._generate_recommendation(
                    mastery.mastery_percentage,
                    failure_patterns
                )

                weaknesses.append(WeaknessAnalysis(
                    topic=topic,
                    mastery_percentage=mastery.mastery_percentage,
                    failure_patterns=failure_patterns,
                    question_ids=topic_questions,
                    priority_score=round(priority_score, 2),
                    recommendation=recommendation
                ))

        # Sort by priority
        return sorted(weaknesses, key=lambda x: x.priority_score, reverse=True)

    @staticmethod
    def _generate_recommendation(mastery_pct: float, patterns: List[FailurePattern]) -> str:
        """Generate smart recommendation based on patterns"""

        if FailurePattern.EASY_WRONG in patterns:
            return "⚠️ CRITICAL: You're failing easy questions. Review fundamental concepts immediately."

        if FailurePattern.TRICKY_WRONG in patterns and mastery_pct < 40:
            return "Focus on understanding core concepts. These questions are confusing you."

        if FailurePattern.FAST_WRONG in patterns:
            return "You're guessing quickly. Slow down and read questions carefully."

        if FailurePattern.SLOW_WRONG in patterns:
            return "You're spending time but still getting wrong answers. The concept is unclear - revisit the source material."

        if FailurePattern.REPEATED_TOPIC in patterns:
            return "Multiple failures in this topic. This is a knowledge gap - study this section thoroughly."

        if mastery_pct < 50:
            return "Low mastery. Focus on understanding basic concepts before moving forward."

        return "Practice more questions in this topic to build confidence."

    @staticmethod
    def generate_adaptive_targeting(
        weakness_areas: List[WeaknessAnalysis]
    ) -> AdaptiveTargeting:
        """Generate targeting for next test based on weaknesses"""

        # Get high-priority topics (top 60% of priority scores)
        if not weakness_areas:
            return AdaptiveTargeting(
                weak_topics=[],
                recommended_difficulty=["medium"],
                focus_question_types=["mcq", "short_answer"],
                estimated_questions_needed=10
            )

        sorted_weaknesses = sorted(weakness_areas, key=lambda x: x.priority_score, reverse=True)
        cutoff_index = max(1, int(len(sorted_weaknesses) * 0.6))
        top_weaknesses = sorted_weaknesses[:cutoff_index]

        weak_topics = [w.topic for w in top_weaknesses]

        # Determine recommended difficulty
        avg_mastery = sum(w.mastery_percentage for w in top_weaknesses) / len(top_weaknesses)

        if avg_mastery < 40:
            recommended_difficulty = ["easy", "medium"]
        elif avg_mastery < 60:
            recommended_difficulty = ["medium"]
        else:
            recommended_difficulty = ["medium", "hard"]

        # Estimate questions needed (more questions for weaker topics)
        questions_per_topic = max(3, int(100 - avg_mastery) // 10)
        total_questions = len(weak_topics) * questions_per_topic

        return AdaptiveTargeting(
            weak_topics=weak_topics,
            recommended_difficulty=recommended_difficulty,
            focus_question_types=["mcq", "short_answer", "conceptual"],
            estimated_questions_needed=min(total_questions, 50)
        )

    @staticmethod
    def smart_review_ordering(
        weakness_areas: List[WeaknessAnalysis],
        question_ids: List[str]
    ) -> List[Dict[str, any]]:
        """Order questions for review based on priority"""

        review_order = []
        priority_map = {}

        # Build priority map
        for weakness in weakness_areas:
            for q_id in weakness.question_ids:
                if q_id not in priority_map:
                    priority_map[q_id] = {
                        "score": weakness.priority_score,
                        "topic": weakness.topic,
                        "patterns": weakness.failure_patterns
                    }

        # Order the requested questions
        for idx, q_id in enumerate(question_ids):
            if q_id in priority_map:
                info = priority_map[q_id]
                review_order.append({
                    "question_id": q_id,
                    "priority": int(info["score"]),
                    "reason": AnalyticsService._get_priority_reason(info["patterns"]),
                    "topic": info["topic"]
                })

        # Sort by priority score
        review_order.sort(key=lambda x: x["priority"], reverse=True)

        return review_order

    @staticmethod
    def _get_priority_reason(patterns: List[FailurePattern]) -> str:
        """Get human-readable priority reason"""
        if FailurePattern.EASY_WRONG in patterns:
            return "Critical knowledge gap"
        if FailurePattern.TRICKY_WRONG in patterns:
            return "High-priority confusion point"
        if FailurePattern.SLOW_WRONG in patterns:
            return "Concept unclear"
        if FailurePattern.FAST_WRONG in patterns:
            return "Guessed incorrectly"
        if FailurePattern.REPEATED_TOPIC in patterns:
            return "Repeated failures"
        return "Needs review"
