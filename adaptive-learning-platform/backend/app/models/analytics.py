from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


# STEP 1: Raw signals only - no psychology
class BehavioralSignals(BaseModel):
    """Raw facts about how user answered - NO interpretations"""
    question_id: str
    time_spent: int
    answered: bool  # True if answered, False if skipped
    correct: bool
    changed_answer: bool
    hesitation_count: int
    marked_tricky: bool
    empirical_difficulty: float  # % who got it right (0-1)
    topic: str
    llm_difficulty: str  # Original LLM tag (for bootstrapping)


# STEP 2: Computed probabilistic states
class CognitiveScores(BaseModel):
    """Inferred psychological states - computed from signals"""
    question_id: str
    guessing_score: float = 0.0  # 0-1: fast wrong on hard question
    confusion_score: float = 0.0  # 0-1: slow wrong, hesitation
    avoidance_score: float = 0.0  # 0-1: skipped, especially easy ones
    knowledge_gap_score: float = 0.0  # 0-1: wrong on empirically easy question
    confidence_score: float = 0.0  # 0-1: fast correct, no changes


# Behavioral user types
class BehavioralType(str, Enum):
    RUSHER = "rusher"  # Fast answers, many wrong
    HESITATOR = "hesitator"  # Slow, changes answers
    AVOIDER = "avoider"  # High skip rate
    GRINDER = "grinder"  # Slow but accurate
    RANDOM_CLICKER = "random_clicker"  # Fast, inconsistent patterns


class QuestionStatistics(BaseModel):
    """Track empirical difficulty - replaces LLM guesses"""
    question_id: str
    total_attempts: int = 0
    correct_attempts: int = 0
    empirical_difficulty: float = 0.5  # Bootstrap at 0.5, update with data
    avg_time_taken: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def update_from_attempt(self, correct: bool, time_taken: int):
        """Update statistics with new attempt"""
        self.total_attempts += 1
        if correct:
            self.correct_attempts += 1

        # Empirical difficulty = % who got it right
        self.empirical_difficulty = self.correct_attempts / self.total_attempts

        # Update average time
        self.avg_time_taken = (
            (self.avg_time_taken * (self.total_attempts - 1) + time_taken)
            / self.total_attempts
        )
        self.last_updated = datetime.utcnow()


class TopicMastery(BaseModel):
    """Mathematical topic mastery - not vibes"""
    topic: str
    total_attempts: int
    correct_attempts: int
    wrong_attempts: int

    # Mathematical formula: weighted_avg(correctness × difficulty × recency)
    mastery_score: float  # 0-1, computed mathematically
    mastery_percentage: float  # For display

    avg_time_taken: float
    difficulty_breakdown: Dict[str, Dict[str, int]] = {}

    # Breakdown by empirical difficulty
    easy_correct: int = 0  # empirical_difficulty > 0.7
    easy_wrong: int = 0
    medium_correct: int = 0  # 0.3 < difficulty < 0.7
    medium_wrong: int = 0
    hard_correct: int = 0  # difficulty < 0.3
    hard_wrong: int = 0


class FailurePattern(str, Enum):
    FAST_WRONG = "fast_wrong"
    SLOW_WRONG = "slow_wrong"
    EASY_WRONG = "easy_wrong"
    TRICKY_WRONG = "tricky_wrong"
    REPEATED_TOPIC = "repeated_topic"


class WeaknessAnalysis(BaseModel):
    """Mathematical weakness analysis"""
    topic: str
    mastery_score: float = 0.0  # 0-1 from TopicMastery
    mastery_percentage: float = 0.0

    # Mathematical formula: weakness × exposure × confidence_penalty
    weakness_score: float = 0.0 # 1 - mastery_score
    exposure_count: int = 0 # How many questions seen
    confidence_penalty: float = 0.0 # Based on hesitation, marking tricky

    # Final priority = weakness × exposure × confidence_penalty
    priority_score: float  # Higher = more urgent

    question_ids: List[str]
    failure_patterns: List[FailurePattern] = []
    cognitive_scores: List[CognitiveScores] = []  # Probabilistic states
    recommendation: str


class CognitiveProfile(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    document_id: PyObjectId
    topic_mastery: List[TopicMastery] = []
    weakness_areas: List[WeaknessAnalysis] = []
    overall_stats: Dict[str, Any] = {}
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PatternDetection(BaseModel):
    session_id: str
    patterns: List[Dict[str, Any]]


class WeaknessMapResponse(BaseModel):
    user_id: str
    document_id: str
    weakness_areas: List[WeaknessAnalysis]
    high_priority_topics: List[str]
    recommended_focus: List[str]


# 1. LEARNING VELOCITY
class LearningVelocity(BaseModel):
    """Track how fast a topic improves per session"""
    topic: str
    sessions_analyzed: int
    mastery_trajectory: List[float]  # [0.3, 0.5, 0.7, 0.8] over sessions
    velocity: float  # Slope: mastery_gain / session
    acceleration: float  # Is velocity increasing or decreasing?
    sessions_to_mastery: Optional[int]  # Predicted sessions to 0.9 mastery
    comparative_rank: Optional[str]  # "3× faster than Transformers"


# 2. FORGETTING CURVE
class ForgettingCurveData(BaseModel):
    """Detect mastery decay over time"""
    topic: str
    peak_mastery: float  # Highest mastery achieved
    peak_date: datetime  # When it peaked
    current_mastery: float
    days_since_peak: int
    decay_rate: float  # How fast it's decaying (0-1 per day)
    half_life_days: Optional[float]  # Days until mastery halves
    needs_review: bool  # True if decayed significantly


# 3. EXAM READINESS SCORE
class ExamReadinessScore(BaseModel):
    """Holistic exam readiness - insanely powerful"""
    overall_score: float  # 0-100: "You are 72% ready"

    # Components (weighted)
    mastery_score: float  # 40% weight: avg topic mastery
    consistency_score: float  # 25% weight: low variance across topics
    confidence_score: float  # 20% weight: low hesitation, fast correct
    coverage_score: float  # 15% weight: % of topics practiced

    # Breakdown by component
    strong_topics: List[str]  # Mastery > 0.8
    weak_topics: List[str]  # Mastery < 0.5
    inconsistent_topics: List[str]  # High variance

    # Actionable insights
    estimated_study_hours: int  # To reach 90% readiness
    priority_actions: List[str]  # Specific recommendations
    readiness_level: str  # "Ready", "Almost Ready", "Needs Work"


# 4. BEHAVIOR FINGERPRINT
class BehaviorFingerprint(BaseModel):
    """Deep personality profiling - beyond just types"""
    user_id: str

    # Core traits (0-1 scale)
    risk_taking: float  # High = answers fast even when uncertain
    perfectionism: float  # High = slow, changes answers, marks tricky
    skimming: float  # High = fast, skips hard questions
    grinding: float  # High = slow but thorough, high accuracy

    # Detailed metrics
    confidence_calibration: float  # Are they confident when correct?
    speed_accuracy_tradeoff: float  # -1 (slow accurate) to +1 (fast sloppy)
    difficulty_seeking: float  # Do they avoid or embrace hard questions?
    consistency: float  # How stable is performance across sessions?

    # Personality label
    primary_trait: str  # "Risk-taker", "Perfectionist", "Skimmer", "Grinder"
    secondary_trait: Optional[str]

    # Coaching recommendations
    strengths: List[str]
    growth_areas: List[str]
    optimal_study_strategy: str


class UserBehavioralProfile(BaseModel):
    """Inferred user behavior type across all sessions"""
    user_id: str
    behavioral_type: BehavioralType
    avg_time_per_question: float
    skip_rate: float  # 0-1
    hesitation_rate: float  # 0-1
    accuracy_by_speed: Dict[str, float]  # {fast: 0.6, medium: 0.8, slow: 0.7}

    # Enhanced with fingerprint
    behavior_fingerprint: Optional[BehaviorFingerprint] = None


class ExplainAnswerRequest(BaseModel):
    session_id: str
    question_id: str


class AIExplanation(BaseModel):
    """AI explanation WITH behavioral grounding - no hallucination"""
    question_id: str
    user_answer: str
    correct_answer: str

    # Grounding - citation to source
    source_paragraph: str  # Exact text from document
    section_reference: str  # e.g. "Section 2.3"

    # Explanation WITH behavioral context
    why_wrong: str
    concept_explanation: str
    common_mistake: str

    # Behavioral context included
    behavioral_insight: str  # "You spent 15s and skipped - suggests avoidance" etc


class AdaptiveTargeting(BaseModel):
    weak_topics: List[str]
    recommended_difficulty: List[str]
    focus_question_types: List[str]
    estimated_questions_needed: int


class ReviewOrder(BaseModel):
    question_id: str
    priority: int  # 1 = highest
    reason: str
    topic: str
