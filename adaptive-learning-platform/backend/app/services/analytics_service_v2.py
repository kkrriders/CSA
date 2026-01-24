"""
Refactored Analytics Service - Mathematical & Signal-Based

Key principles:
1. Separate signals from interpretations
2. Use empirical difficulty (not LLM guesses)
3. Mathematical formulas for weakness scoring
4. Probabilistic cognitive state inference
5. Behavioral profiling
"""

from typing import List, Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import math

from app.models.test_session import QuestionAnswer, AnswerStatus
from app.models.analytics import (
    BehavioralSignals,
    CognitiveScores,
    TopicMastery,
    WeaknessAnalysis,
    AdaptiveTargeting,
    BehavioralType,
    UserBehavioralProfile,
    QuestionStatistics
)


class AnalyticsServiceV2:
    """Signal-based, mathematical analytics - no vibes"""

    # Thresholds for signal interpretation
    FAST_THRESHOLD = 20  # seconds
    SLOW_THRESHOLD = 60  # seconds
    EASY_DIFFICULTY = 0.7  # 70%+ success rate
    HARD_DIFFICULTY = 0.3  # <30% success rate

    @staticmethod
    def extract_behavioral_signals(
        answer: QuestionAnswer,
        question_data: Dict,
        question_stats: Optional[QuestionStatistics] = None
    ) -> BehavioralSignals:
        """STEP 1: Extract raw signals - NO interpretations"""

        # Get empirical difficulty (or bootstrap with 0.5)
        empirical_diff = question_stats.empirical_difficulty if question_stats else 0.5

        return BehavioralSignals(
            question_id=answer.question_id,
            time_spent=answer.time_taken,
            answered=answer.status != AnswerStatus.SKIPPED,
            correct=answer.status == AnswerStatus.CORRECT,
            changed_answer=answer.changed_answer,
            hesitation_count=answer.hesitation_count,
            marked_tricky=answer.marked_tricky,
            empirical_difficulty=empirical_diff,
            topic=question_data.get("topic", "Unknown"),
            llm_difficulty=question_data.get("difficulty", "medium")
        )

    @staticmethod
    def compute_cognitive_scores(signal: BehavioralSignals) -> CognitiveScores:
        """STEP 2: Infer probabilistic states from signals"""

        scores = CognitiveScores(question_id=signal.question_id)

        if not signal.answered:
            # Skipped questions
            # Easy skip = high avoidance
            if signal.empirical_difficulty > AnalyticsServiceV2.EASY_DIFFICULTY:
                scores.avoidance_score = 0.9
            else:
                scores.avoidance_score = 0.6
            return scores

        if not signal.correct:
            # Wrong answers

            # Guessing score: fast + hard question
            if signal.time_spent < AnalyticsServiceV2.FAST_THRESHOLD:
                # Fast wrong on hard = likely guess
                if signal.empirical_difficulty < AnalyticsServiceV2.HARD_DIFFICULTY:
                    scores.guessing_score = 0.8
                else:
                    scores.guessing_score = 0.5

            # Confusion score: slow + hesitation + wrong
            if signal.time_spent > AnalyticsServiceV2.SLOW_THRESHOLD:
                base_confusion = 0.7
                # Add hesitation penalty
                confusion_penalty = min(signal.hesitation_count * 0.1, 0.3)
                scores.confusion_score = min(base_confusion + confusion_penalty, 1.0)

            # Knowledge gap: wrong on easy question
            if signal.empirical_difficulty > AnalyticsServiceV2.EASY_DIFFICULTY:
                scores.knowledge_gap_score = 0.9  # Critical gap

        else:
            # Correct answers

            # Confidence score: fast correct, no changes
            if (signal.time_spent < AnalyticsServiceV2.FAST_THRESHOLD and
                not signal.changed_answer):
                scores.confidence_score = 0.9
            elif not signal.changed_answer and not signal.marked_tricky:
                scores.confidence_score = 0.7

        return scores

    @staticmethod
    def calculate_topic_mastery_v2(
        signals: List[BehavioralSignals],
        cognitive_scores: List[CognitiveScores]
    ) -> List[TopicMastery]:
        """Mathematical topic mastery: weighted_avg(correctness × difficulty × recency)"""

        topic_data = defaultdict(lambda: {
            "attempts": [],
            "total": 0,
            "correct": 0,
            "wrong": 0,
            "time_sum": 0,
            "easy_correct": 0,
            "easy_wrong": 0,
            "medium_correct": 0,
            "medium_wrong": 0,
            "hard_correct": 0,
            "hard_wrong": 0
        })

        # Group by topic
        for signal in signals:
            if not signal.answered:
                continue  # Skip unanswered for mastery calculation

            data = topic_data[signal.topic]
            data["total"] += 1
            data["time_sum"] += signal.time_spent

            # Store for weighted calculation
            data["attempts"].append({
                "correct": signal.correct,
                "difficulty": signal.empirical_difficulty,
                "timestamp": datetime.utcnow()  # Would come from answer object
            })

            if signal.correct:
                data["correct"] += 1
            else:
                data["wrong"] += 1

            # Categorize by empirical difficulty
            if signal.empirical_difficulty > AnalyticsServiceV2.EASY_DIFFICULTY:
                if signal.correct:
                    data["easy_correct"] += 1
                else:
                    data["easy_wrong"] += 1
            elif signal.empirical_difficulty < AnalyticsServiceV2.HARD_DIFFICULTY:
                if signal.correct:
                    data["hard_correct"] += 1
                else:
                    data["hard_wrong"] += 1
            else:
                if signal.correct:
                    data["medium_correct"] += 1
                else:
                    data["medium_wrong"] += 1

        # Calculate mathematical mastery
        mastery_list = []
        for topic, data in topic_data.items():
            if data["total"] == 0:
                continue

            # Mathematical formula: weighted_avg(correctness × difficulty × recency)
            mastery_score = AnalyticsServiceV2._calculate_weighted_mastery(
                data["attempts"]
            )

            mastery_list.append(TopicMastery(
                topic=topic,
                total_attempts=data["total"],
                correct_attempts=data["correct"],
                wrong_attempts=data["wrong"],
                mastery_score=mastery_score,
                mastery_percentage=mastery_score * 100,
                avg_time_taken=data["time_sum"] / data["total"],
                easy_correct=data["easy_correct"],
                easy_wrong=data["easy_wrong"],
                medium_correct=data["medium_correct"],
                medium_wrong=data["medium_wrong"],
                hard_correct=data["hard_correct"],
                hard_wrong=data["hard_wrong"]
            ))

        return mastery_list

    @staticmethod
    def _calculate_weighted_mastery(attempts: List[Dict]) -> float:
        """
        Mathematical formula: weighted_avg(correctness × difficulty × recency)

        - Correctness: 1 if correct, 0 if wrong
        - Difficulty weight: harder questions count more
        - Recency: recent attempts weigh more (exponential decay)
        """
        if not attempts:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        now = datetime.utcnow()

        for i, attempt in enumerate(attempts):
            # Correctness score
            correctness = 1.0 if attempt["correct"] else 0.0

            # Difficulty weight: inverse of empirical difficulty
            # Hard questions (low success rate) weight more
            difficulty_weight = 1.0 - attempt["difficulty"]

            # Recency weight: exponential decay (half-life = 5 attempts)
            recency_weight = math.exp(-0.14 * (len(attempts) - i - 1))

            # Combined weight
            weight = difficulty_weight * recency_weight
            weighted_sum += correctness * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def identify_weakness_areas_v2(
        topic_mastery: List[TopicMastery],
        cognitive_scores: List[CognitiveScores],
        signals: List[BehavioralSignals]
    ) -> List[WeaknessAnalysis]:
        """
        Mathematical weakness analysis:
        priority = weakness × exposure × confidence_penalty
        """

        # Group cognitive scores by topic
        topic_scores = defaultdict(list)
        topic_questions = defaultdict(set)

        signal_by_id = {s.question_id: s for s in signals}

        for score in cognitive_scores:
            signal = signal_by_id.get(score.question_id)
            if signal:
                topic_scores[signal.topic].append(score)
                topic_questions[signal.topic].add(score.question_id)

        weakness_list = []

        for mastery in topic_mastery:
            # Skip topics with high mastery
            if mastery.mastery_score > 0.75:
                continue

            # weakness_score = 1 - mastery_score
            weakness_score = 1.0 - mastery.mastery_score

            # exposure_count
            exposure_count = len(topic_questions.get(mastery.topic, set()))

            # confidence_penalty: based on hesitation, marking tricky
            scores = topic_scores.get(mastery.topic, [])
            confidence_penalty = AnalyticsServiceV2._calculate_confidence_penalty(
                scores,
                signals
            )

            # Final priority = weakness × exposure × confidence_penalty
            priority_score = weakness_score * exposure_count * confidence_penalty

            weakness_list.append(WeaknessAnalysis(
                topic=mastery.topic,
                mastery_score=mastery.mastery_score,
                weakness_score=weakness_score,
                exposure_count=exposure_count,
                confidence_penalty=confidence_penalty,
                priority_score=priority_score,
                question_ids=list(topic_questions.get(mastery.topic, set())),
                cognitive_scores=scores,
                recommendation=AnalyticsServiceV2._generate_recommendation(
                    mastery, scores
                )
            ))

        # Sort by priority (highest first)
        weakness_list.sort(key=lambda w: w.priority_score, reverse=True)

        return weakness_list

    @staticmethod
    def _calculate_confidence_penalty(
        scores: List[CognitiveScores],
        signals: List[BehavioralSignals]
    ) -> float:
        """Calculate confidence penalty from behavioral signals"""
        if not scores:
            return 1.0

        signal_by_id = {s.question_id: s for s in signals}

        # Base penalty
        penalty = 1.0

        # High confusion/hesitation increases penalty
        avg_confusion = sum(s.confusion_score for s in scores) / len(scores)
        penalty += avg_confusion * 0.5

        # Marked tricky increases penalty
        marked_count = sum(
            1 for s in scores
            if signal_by_id.get(s.question_id) and signal_by_id[s.question_id].marked_tricky
        )
        if marked_count > 0:
            penalty += 0.3 * (marked_count / len(scores))

        return min(penalty, 2.0)  # Cap at 2x

    @staticmethod
    def _generate_recommendation(
        mastery: TopicMastery,
        scores: List[CognitiveScores]
    ) -> str:
        """Generate recommendation based on mathematical analysis"""

        if mastery.easy_wrong > mastery.easy_correct:
            return f"Critical gap in {mastery.topic} fundamentals - review basics first"

        avg_knowledge_gap = sum(s.knowledge_gap_score for s in scores) / len(scores) if scores else 0

        if avg_knowledge_gap > 0.5:
            return f"Struggling with basic {mastery.topic} concepts - focused review needed"

        avg_confusion = sum(s.confusion_score for s in scores) / len(scores) if scores else 0

        if avg_confusion > 0.6:
            return f"High confusion in {mastery.topic} - try different explanations or examples"

        return f"Practice more {mastery.topic} problems to build confidence"

    @staticmethod
    def infer_behavioral_type(all_signals: List[BehavioralSignals]) -> BehavioralType:
        """Infer user's behavioral pattern"""

        if not all_signals:
            return BehavioralType.GRINDER  # Default

        total = len(all_signals)
        answered = [s for s in all_signals if s.answered]

        if not answered:
            return BehavioralType.AVOIDER

        # Calculate metrics
        skip_rate = (total - len(answered)) / total
        avg_time = sum(s.time_spent for s in answered) / len(answered)
        fast_count = sum(1 for s in answered if s.time_spent < AnalyticsServiceV2.FAST_THRESHOLD)
        fast_rate = fast_count / len(answered)
        accuracy = sum(1 for s in answered if s.correct) / len(answered)

        # Classify
        if skip_rate > 0.3:
            return BehavioralType.AVOIDER

        if fast_rate > 0.7:
            if accuracy < 0.5:
                return BehavioralType.RANDOM_CLICKER
            else:
                return BehavioralType.RUSHER

        if avg_time > AnalyticsServiceV2.SLOW_THRESHOLD:
            avg_hesitation = sum(s.hesitation_count for s in answered) / len(answered)
            if avg_hesitation > 1:
                return BehavioralType.HESITATOR
            else:
                return BehavioralType.GRINDER

        return BehavioralType.GRINDER  # Default: normal pace

    @staticmethod
    def generate_adaptive_targeting_v2(
        weakness_areas: List[WeaknessAnalysis]
    ) -> AdaptiveTargeting:
        """Generate adaptive targeting from weakness analysis"""

        if not weakness_areas:
            return AdaptiveTargeting(
                weak_topics=[],
                recommended_difficulty=["medium"],
                focus_question_types=["mcq"],
                estimated_questions_needed=10
            )

        # Top 3 weak topics by priority
        weak_topics = [w.topic for w in weakness_areas[:3]]

        # Determine difficulty based on mastery
        top_weakness = weakness_areas[0]
        if top_weakness.mastery_score < 0.3:
            recommended_difficulty = ["easy"]
        elif top_weakness.mastery_score < 0.6:
            recommended_difficulty = ["easy", "medium"]
        else:
            recommended_difficulty = ["medium"]

        # Estimate questions needed: inversely proportional to mastery
        questions_needed = int(20 * (1 - top_weakness.mastery_score))

        return AdaptiveTargeting(
            weak_topics=weak_topics,
            recommended_difficulty=recommended_difficulty,
            focus_question_types=["mcq"],  # Could be enhanced later
            estimated_questions_needed=max(5, min(questions_needed, 50))
        )
